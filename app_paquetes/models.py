from abc import ABC, abstractmethod
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Sum
from .utils.paquete_utils import PaqueteUtils
#TODO: mover las constantes a un unico archivo

class Cliente(models.Model):
    """Modelo básico de cliente"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Email", blank=True)
    telefono = models.CharField(max_length=20, verbose_name="Teléfono", blank=True)
    direccion = models.TextField(verbose_name="Dirección", blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]

class Paquete(models.Model):
    class EstadoPaquete(models.TextChoices):
        EN_DEPOSITO = "en_deposito", "En depósito"
        EN_DISTRIBUCION = "en_distribucion", "En distribución"

    class TipoPaquete(models.TextChoices):
        PEQUENO = "P"
        MEDIANO = "M"
        GRANDE = "G"
    
    tracking = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de seguimiento"
    )
    direccion_destinatario = models.CharField(max_length=200, verbose_name="Dirección del destinatario")
    telefono_destinatario = models.CharField(max_length=20, verbose_name="Teléfono del destinatario")
    nombre_destinatario = models.CharField(max_length=100, verbose_name="Nombre del destinatario")
    peso = models.FloatField(verbose_name="Peso", help_text="En gramos")
    altura = models.FloatField(verbose_name="Altura", help_text="En centímetros")
    estado = models.CharField(
        max_length=20,
        choices=EstadoPaquete.choices,
        default=EstadoPaquete.EN_DEPOSITO,
        verbose_name="Estado"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="paquetes",
        verbose_name="Cliente"
    )
    tipo = models.CharField(
        max_length=1,
        choices=TipoPaquete.choices,
        blank=True,
        verbose_name="Tipo de paquete"
    )

    def __str__(self):
        return f"Paquete {self.tracking} - {self.nombre_destinatario}"

    def clean(self):
        if self.peso <= 0:
            raise ValidationError({"peso": "El peso debe ser mayor a 0"})
        if self.peso > 25000.0:
            raise ValidationError({"peso": "El peso debe ser menor a 25"}) #se asume como regla de negocio

    def save(self, *args, **kwargs):
        """Calcula el tipo de paquete basado en el peso"""
        if self.peso > 25000.0:
            raise ValidationError({"peso": "El peso debe ser menor a 25"}) #se asume como regla de negocio
        self.tipo = PaqueteUtils.determinar_tipo_paquete(self.peso)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Paquete"
        verbose_name_plural = "Paquetes"
        ordering = ["-estado", "tracking"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["tipo"]),
        ]

class Planilla(models.Model):
    numero_planilla = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de planilla"
    )
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha de creación")
    PESO_LIMITE = 25000

    def __str__(self):
        return f"Planilla {self.numero_planilla} - {self.fecha}"

    def marcar_paquetes_en_distribucion(self):
        """Cambia estado de todos los paquetes a 'en distribución'"""
        updated_count = 0
        for item in self.items.all():
            if item.paquete.estado == Paquete.EstadoPaquete.EN_DEPOSITO:
                item.paquete.estado = Paquete.EstadoPaquete.EN_DISTRIBUCION
                item.paquete.save()
                updated_count += 1
        return updated_count

    def get_peso_total(self):
        """Calcula el peso total de todos los paquetes """
        return self.items.aggregate(
            total_peso=Sum("paquete__peso")
        )["total_peso"] or 0

    def verificar_limite_peso(self, peso_a_agregar):
        """
        Verifica si agregar el peso excede el peso limite
        """
        peso_actual = self.get_peso_total()
        return (peso_actual + peso_a_agregar) <= self.PESO_LIMITE 

    class Meta:
        verbose_name = "Planilla"
        verbose_name_plural = "Planillas"
        ordering = ["-fecha"]
    
class MotivoFallo(models.Model):
    codigo = models.CharField(max_length=20, default= 'no code');
    nombre = models.CharField(max_length=100, default= 'no name')
    descripcion = models.TextField(default='no description')
    active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def get_codigo(self) -> str:
        raise NotImplementedError
    
    def get_nombre(self) -> str:
        raise NotImplementedError
    
    def get_descripcion(self) -> str:
        raise NotImplementedError
    
    def is_active(self) -> bool:
        raise NotImplementedError
    

class MotivoFalloSimple(MotivoFallo, models.Model):
    def get_codigo(self) -> str:
        return self.codigo 
    
    def get_nombre(self) -> str:
        return self.nombre

    def get_descripcion(self) -> str:
        return self.descripcion

    def is_active(self) -> bool:
        return self.active  


# class MotivoFalloCompuesto(MotivoFallo, models.Model):
#     """(WIP): Futura combinación de motivos simples y compuestos, implementa el patron Composite"""
#     motivos = models.ManyToManyField(MotivoFalloSimple)

#     def get_codigo(self) -> str:
#         return "".join(motivo.get_codigo() for motivo in self.motivos.all())

#     def get_nombre(self) -> str:
#         return " y ".join(motivo.get_nombre() for motivo in self.motivos.all())

#     def get_descripcion(self) -> str:
#         return " Y ".join(
#             f"({motivo.get_nombre()}: {motivo.get_descripcion()})"
#             for motivo in self.motivos.all()
#         )

#     def is_active(self) -> bool:
#         return all(motivo.is_active() for motivo in self.motivos.all())

class Item(models.Model):
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Planilla"
    )
    paquete = models.ForeignKey(
        Paquete,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Paquete"
    )
    posicion = models.PositiveIntegerField(verbose_name="Posición")
    
    motivo_fallo = models.ForeignKey(
        MotivoFalloSimple,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Motivo de fallo"
    )

    def validar_paquete_unico_en_planilla(item: 'Item') -> None:    #Agregado
        """Validacion de que un paquete no esté en múltiples planillas activas"""
        if item.paquete.estado != Paquete.EstadoPaquete.EN_DEPOSITO:
            return

        query = Item.objects.filter(
            paquete=item.paquete,
            planilla__items__paquete__estado=Paquete.EstadoPaquete.EN_DEPOSITO
        ).exclude(id=item.id)

        if query.exists():
            raise ValidationError({
                "paquete": "Este paquete está en otra planilla activa."
            })

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["planilla", "paquete"],
                name="unique_planilla_paquete"
            )
        ]
        ordering = ["posicion"]
        verbose_name = "Ítem de Planilla"
        verbose_name_plural = "Ítems de Planilla"

    def __str__(self):
        return f"Ítem {self.posicion} - {self.paquete.tracking}"

    def clean(self):
        """Solo permite motivos actives"""
        if self.motivo_fallo and not self.motivo_fallo.is_active():            
            raise ValidationError({
                "motivo_fallo": "No se puede usar un motivo de fallo inactive."
            })

        # Agregado: Validar que el paquete no esté en múltiples planillas activas
        self.validar_paquete_unico_en_planilla(self)
