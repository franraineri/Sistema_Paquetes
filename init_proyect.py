# inicializar_proyecto.py

"""
Script para
1. Crear migraciones
2. Aplicar migraciones
3. Crear superusuario
4. Cargar datos de prueba
"""

import logging
import os
import subprocess
import sys
from typing import Dict, List
from django.contrib.auth import get_user_model
from django.db import OperationalError
from Sistema_Paquetes import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sistema_Paquetes.settings')
django.setup()

# Importaciones Django (deben estar al final para evitar circular imports)
try:
    from app_paquetes.models import (
        Cliente, Paquete, Planilla, Item, 
        MotivoFalloSimple, MotivoFalloCompuesto
    )
except ImportError:
    # Para testing o ejecución directa
    pass


def setup_django():
    """Configura Django correctamente"""
    try:
        # Verificar si Django ya está configurado
        if not settings.configured:
            # Ajusta esto al nombre real de tu proyecto Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sistema_Paquetes.settings')
            django.setup()
        
    
        return True
    except Exception as e:
        print(f"Error configurando Django: {e}")
        return False


def set_admin():
    """Crea el superusuario si no existe"""
    User = get_user_model()
    username = "admin"
    email = "admin@example.com"
    password = "admin123"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superusuario creado: {username} / {password}")
    else:
        print(f"Superusuario ya existe: {username}")



def creacion_de_datos() -> Dict[str, int]:
    """
    Crea datos de prueba con motivos de fallo simples y compuestos
    
    Returns:
        Dict con conteo de objetos creados por tipo
    """

    setup_django()
    
    django.setup()

    logger.info("Iniciando creación de datos de prueba...")
    
    # Inicializar loaders
    cliente_loader = ClienteDataLoader()
    motivo_simple_loader = MotivoFalloDataLoader()
    paquete_loader = PaqueteDataLoader()
    planilla_loader = PlanillaDataLoader()
    asignacion_loader = AsignacionDataLoader()
    motivo_asignacion_loader = MotivoAsignacionDataLoader()
    
    results = {}
    
    try:
        # 1. Crear usuario administrador
        admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='password'
            )
        logger.info("Usuario administrador creado")
        results['usuarios'] = 1
        
        # 2. Crear clientes
        clientes = cliente_loader.load()
        results['clientes'] = len(clientes)
        
        # 3. Crear motivos simples
        motivos_simples = motivo_simple_loader.load()
        results['motivos_simples'] = len(motivos_simples)
        

        # 5. Crear paquetes
        paquetes = paquete_loader.load(clientes)
        results['paquetes'] = len(paquetes)
        
        # 6. Crear planillas
        planillas = planilla_loader.load()
        results['planillas'] = len(planillas)
        
        # 7. Asignar paquetes a planillas
        items_creados = asignacion_loader.assign_packages_to_plans(planillas, paquetes)
        results['items'] = items_creados
        
        # 8. Asignar motivos a ítems
        motivos_asignados = motivo_asignacion_loader.assign_motivos_to_items(motivos_simples, motivos_compuestos)
        results['motivos_asignados'] = motivos_asignados
        
        logger.info("Datos de prueba creados exitosamente!")
        
        # Mostrar resumen
        logger.info(f"Resumen de creación:")
        for key, value in results.items():
            logger.info(f"- {key}: {value}")
            
        return results
        
    except Exception as e:
        logger.error(f"Error durante la creación de datos: {e}")
        raise DataLoaderError(f"Fallo en creación de datos: {e}")


# Configurar logging
logger = logging.getLogger(__name__)



class BaseDataLoader:
    """Clase base para loaders de datos"""
    
    def __init__(self):
        self.created_objects = []
        self.logger = logger
    
    def log_creation(self, model_name: str, instance) -> None:
        """Registra la creación de un objeto"""
        self.logger.info(f"{model_name} creado: {instance}")

class DataLoaderError(Exception):
    pass


class ClienteDataLoader(BaseDataLoader):
    """Carga de datos de clientes"""
    
    CLIENTES_DATA = [
        {
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "telefono": "123456789",
            "direccion": "Calle Principal 123"
        },
        {
            "nombre": "María García",
            "email": "maria@example.com",
            "telefono": "987654321",
            "direccion": "Avenida Secundaria 456"
        },
        {
            "nombre": "Carlos López",
            "email": "carlos@example.com",
            "telefono": "456789123",
            "direccion": "Plaza Central 789"
        }
    ]
    
    def load(self) -> List[Cliente]:
        """Carga clientes de prueba"""
        clientes = []
        for cliente_data in self.CLIENTES_DATA:
            try:
                cliente, created = Cliente.objects.get_or_create(**cliente_data)
                if created:
                    self.log_creation("Cliente", cliente.nombre)
                else:
                    self.logger.info(f"Cliente existente: {cliente.nombre}")
                clientes.append(cliente)
            except Exception as e:
                self.logger.error(f"Error creando cliente {cliente_data}: {e}")
                raise DataLoaderError(f"Error al crear cliente: {e}")
        
        return clientes


class MotivoFalloDataLoader(BaseDataLoader):
    """Carga de datos de motivos de fallo"""
    
    MOTIVOS_SIMPLRES_DATA = [
        {
            "codigo": "MP001",
            "nombre": "Paquete dañado",
            "descripcion": "El paquete presenta daños visibles en su envoltura"
        },
        {
            "codigo": "MP002",
            "nombre": "Dirección incorrecta",
            "descripcion": "La dirección del destinatario es incorrecta o incompleta"
        },
        {
            "codigo": "MP003",
            "nombre": "Peso excesivo",
            "descripcion": "El paquete excede el peso máximo permitido"
        },
        {
            "codigo": "MP004",
            "nombre": "Información incompleta",
            "descripcion": "Faltan datos importantes en la etiqueta del paquete"
        }
    ]
    
    def load(self) -> List[MotivoFalloSimple]:
        """Carga motivos de fallo simples"""
        motivos = []
        for motivo_data in self.MOTIVOS_SIMPLRES_DATA:
            try:
                motivo, created = MotivoFalloSimple.objects.get_or_create(**motivo_data)
                if created:
                    self.log_creation("Motivo Simple", motivo.nombre)
                else:
                    self.logger.info(f"Motivo simple existente: {motivo.nombre}")
                motivos.append(motivo)
            except Exception as e:
                self.logger.error(f"Error creando motivo simple {motivo_data}: {e}")
                raise DataLoaderError(f"Error al crear motivo simple: {e}")
        
        return motivos


class PaqueteDataLoader(BaseDataLoader):
    """Carga de datos de paquetes"""
    
    PAQUETES_DATA = [
        {
            "tracking": "TRK001",
            "direccion_destinatario": "Calle Principal 123",
            "telefono_destinatario": "123456789",
            "nombre_destinatario": "Juan Pérez",
            "peso": 500.0,  # 500g - pequeño
            "altura": 10.0,
            "estado": Paquete.EstadoPaquete.EN_DEPOSITO
        },
        {
            "tracking": "TRK002",
            "direccion_destinatario": "Avenida Secundaria 456",
            "telefono_destinatario": "987654321",
            "nombre_destinatario": "María García",
            "peso": 2500.0,  # 2500g - mediano
            "altura": 15.0,
            "estado": Paquete.EstadoPaquete.EN_DEPOSITO
        },
        {
            "tracking": "TRK003",
            "direccion_destinatario": "Plaza Central 789",
            "telefono_destinatario": "456789123",
            "nombre_destinatario": "Carlos López",
            "peso": 4000.0,  # 4000g - grande
            "altura": 20.0,
            "estado": Paquete.EstadoPaquete.EN_DEPOSITO
        },
        {
            "tracking": "TRK004",
            "direccion_destinatario": "Calle Secundaria 321",
            "telefono_destinatario": "321654987",
            "nombre_destinatario": "Ana Martínez",
            "peso": 800.0,  # 800g - pequeño
            "altura": 12.0,
            "estado": Paquete.EstadoPaquete.EN_DEPOSITO
        },
        {
            "tracking": "TRK005",
            "direccion_destinatario": "Avenida Principal 654",
            "telefono_destinatario": "654321987",
            "nombre_destinatario": "Luis Rodríguez",
            "peso": 3500.0,  # 3500g - grande
            "altura": 18.0,
            "estado": Paquete.EstadoPaquete.EN_DEPOSITO
        }
    ]
    
    def load(self, clientes: List[Cliente]) -> List[Paquete]:
        """Carga paquetes de prueba"""
        paquetes = []
        for i, paquete_data in enumerate(self.PAQUETES_DATA):
            try:
                # Asignar cliente secuencialmente
                if i < len(clientes):
                    paquete_data["cliente"] = clientes[i % len(clientes)]
                
                paquete, created = Paquete.objects.get_or_create(**paquete_data)
                if created:
                    self.log_creation("Paquete", paquete.tracking)
                else:
                    self.logger.info(f"Paquete existente: {paquete.tracking}")
                paquetes.append(paquete)
            except Exception as e:
                self.logger.error(f"Error creando paquete {paquete_data}: {e}")
                raise DataLoaderError(f"Error al crear paquete: {e}")
        
        return paquetes


class PlanillaDataLoader(BaseDataLoader):
    """Carga de datos de planillas"""
    
    PLANILLAS_DATA = [
        {
            "numero_planilla": "PLN001",
        },
        {
            "numero_planilla": "PLN002",
        }
    ]
    
    def load(self) -> List[Planilla]:
        """Carga planillas de prueba"""
        planillas = []
        for planilla_data in self.PLANILLAS_DATA:
            try:
                planilla, created = Planilla.objects.get_or_create(**planilla_data)
                if created:
                    self.log_creation("Planilla", planilla.numero_planilla)
                else:
                    self.logger.info(f"Planilla existente: {planilla.numero_planilla}")
                planillas.append(planilla)
            except Exception as e:
                self.logger.error(f"Error creando planilla {planilla_data}: {e}")
                raise DataLoaderError(f"Error al crear planilla: {e}")
        
        return planillas


class AsignacionDataLoader(BaseDataLoader):
    """Carga de asignaciones de datos"""
    
    def assign_packages_to_plans(self, planillas: List[Planilla], paquetes: List[Paquete]) -> int:
        """Asigna paquetes a planillas"""
        try:
            # Asignar primer paquete a primera planilla
            item1 = Item.objects.create(
                planilla=planillas[0],
                paquete=paquetes[0],
                posicion=1
            )
            self.log_creation("Ítem", f"Paquete {paquetes[0].tracking} a planilla {planillas[0].numero_planilla}")
            
            # Asignar segundo y tercer paquete a segunda planilla
            item2 = Item.objects.create(
                planilla=planillas[1],
                paquete=paquetes[1],
                posicion=1
            )
            self.log_creation("Ítem", f"Paquete {paquetes[1].tracking} a planilla {planillas[1].numero_planilla}")
            
            item3 = Item.objects.create(
                planilla=planillas[1],
                paquete=paquetes[2],
                posicion=2
            )
            self.log_creation("Ítem", f"Paquete {paquetes[2].tracking} a planilla {planillas[1].numero_planilla}")
            
            # Asignar cuarto paquete a primera planilla
            item4 = Item.objects.create(
                planilla=planillas[0],
                paquete=paquetes[3],
                posicion=2
            )
            self.log_creation("Ítem", f"Paquete {paquetes[3].tracking} a planilla {planillas[0].numero_planilla}")
            
            return 4  # Número de ítems creados
            
        except Exception as e:
            self.logger.error(f"Error asignando paquetes a planillas: {e}")
            raise DataLoaderError(f"Error al asignar paquetes: {e}")


class MotivoAsignacionDataLoader(BaseDataLoader):
    """Carga de asignaciones de motivos de fallo"""
    
    def assign_motivos_to_items(self, motivos_simples: List[MotivoFalloSimple], 
                              motivos_compuestos: List[MotivoFalloCompuesto]) -> int:
        """Asigna motivos de fallo a ítems"""
        try:
            items = Item.objects.all()
            assigned_count = 0
            
            # Asignar motivo simple a primer ítem
            if items.exists() and len(motivos_simples) > 0:
                item_con_motivo = items.first()
                item_con_motivo.motivo_fallo = motivos_simples[0]
                item_con_motivo.save()
                self.log_creation("Motivo Asignado", f"Ítem {item_con_motivo.id}")
                assigned_count += 1
            
            return assigned_count
            
        except Exception as e:
            self.logger.error(f"Error asignando motivos de fallo: {e}")
            raise DataLoaderError(f"Error al asignar motivos: {e}")


if __name__ == "__main__":
    print("____ Inicialización del proyecto ____")


    print("\n____ Paso 3: Creación de datos de prueba ____")
    try:
        results = creacion_de_datos()
        print(f"\n¡Datos creados exitosamente Resultados: {results}")
    except Exception as e:
        print(f"Error al crear datos: {e}")
        sys.exit(1)

    # 3. Mensaje final
    print("\n____ Proyecto inicializado con éxito ____")
    print("Inicia el servcodigoor con: python manage.py runserver")
    print("Admin: http://127.0.0.1:8000/admin/ (usuario: admin, clave: admin123)")
    print("API de paquetes: http://127.0.0.1:8000/api/paquetes/")
    print("API de motivos de fallo: http://127.0.0.1:8000/api/motivos-fallo/")
    print("Verificación de motivos: http://127.0.0.1:8000/api/motivos-fallo/5/check/?motivos=1&motivos=2")