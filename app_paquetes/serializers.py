# serializers.py
from rest_framework import serializers
from .models import Cliente, Paquete, Planilla, Item, MotivoFalloSimple


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class PaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paquete
        fields = '__all__'
        read_only_fields = ('tipo',)


class PaqueteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paquete
        fields = [
            'tracking', 'direccion_destinatario', 'telefono_destinatario',
            'nombre_destinatario', 'peso', 'altura', 'cliente'
        ]


class PlanillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planilla
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class ItemWithDetailsSerializer(serializers.ModelSerializer):
    paquete_tracking = serializers.CharField(source='paquete.tracking', read_only=True)
    paquete_estado = serializers.CharField(source='paquete.estado', read_only=True)
    paquete_tipo = serializers.CharField(source='paquete.tipo', read_only=True)
    paquete_peso = serializers.FloatField(source='paquete.peso', read_only=True)
    
    class Meta:
        model = Item
        fields = ['id', 'posicion', 'paquete_tracking', 'paquete_estado', 
                 'paquete_tipo', 'paquete_peso', 'motivo_fallo']


class PlanillaResumenSerializer(serializers.ModelSerializer):
    items = ItemWithDetailsSerializer(many=True, read_only=True)
    peso_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Planilla
        fields = ['id', 'numero_planilla', 'fecha', 'items', 'peso_total']
    
    def get_peso_total(self, obj):
        return obj.get_peso_total()


class MotivoFalloSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoFalloSimple
        fields = '__all__'


# class MotivoFalloCompuestoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MotivoFalloCompuesto
#         fields = '__all__'

