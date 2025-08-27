from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .utils.paquete_utils import PaqueteUtils
from .models import MotivoFalloSimple, Paquete, Planilla, Item
from .serializers import (
    PaqueteSerializer, PaqueteCreateSerializer, PlanillaSerializer,
    ItemSerializer, PlanillaResumenSerializer, MotivoFalloSimpleSerializer
)
from django.db import transaction


class PaqueteListView(generics.ListAPIView):
    serializer_class = PaqueteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'cliente', 'tipo']
    search_fields = ['tracking', 'nombre_destinatario']
    ordering_fields = ['estado', 'tracking', 'fecha']
    ordering = ['-tracking']

    def get_queryset(self):
        queryset = Paquete.objects.select_related('cliente')
        return queryset


class MotivoSimpleListView(generics.ListAPIView):
    """listar motivos de fallo"""
    serializer_class = MotivoFalloSimpleSerializer
    queryset = MotivoFalloSimple.objects.all(),
    
    def get_queryset(self):
        return MotivoFalloSimple.objects.all()


class PaqueteCreateView(generics.CreateAPIView):
    serializer_class = PaqueteCreateSerializer

    def perform_create(self, serializer):
        paquete = serializer.save()


class PaqueteAsignarPlanillaView(generics.UpdateAPIView):
    queryset = Paquete.objects.all()
    serializer_class = PaqueteSerializer
    
    def update(self, request, *args, **kwargs):
        paquete = self.get_object()
        
        # verificar que el paquete esté en estado de depósito
        if paquete.estado != Paquete.EstadoPaquete.EN_DEPOSITO:
            return Response(
                {'error': 'Solo se pueden asignar paquetes en estado "en depósito"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        planilla_id = request.data.get('planilla_id')
        if not planilla_id:
            return Response(
                {'error': 'Se requiere el ID de la planilla'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            planilla = Planilla.objects.get(id=planilla_id)
            
            # Verificar límite de peso antes de crear el ítem
            if not PaqueteUtils.verificar_limite_planilla(planilla, paquete.peso):
                return Response(
                    {'error': 'La planilla excedería el límite de peso total'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crea el ítem de planilla en la ultima posicion
            Item.objects.create(
                planilla=planilla,
                paquete=paquete,
                posicion=planilla.items.count() + 1
            )
            
            return Response(
                {'message': f'Paquete {paquete.tracking} asignado a planilla {planilla.numero_planilla}'},
                status=status.HTTP_200_OK
            )
            
        except Planilla.DoesNotExist:
            return Response(
                {'error': 'Planilla no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class PlanillaDetailView(generics.RetrieveAPIView):
    queryset = Planilla.objects.prefetch_related('items', 'items__paquete')
    serializer_class = PlanillaResumenSerializer


class PlanillaDistribuirView(generics.UpdateAPIView):
    queryset = Planilla.objects.all()
    serializer_class = PlanillaSerializer
    
    def update(self, request, *args, **kwargs):
        planilla = self.get_object()
        
        # Marcar todos los paquetes como "en distribución"
        updated_count = planilla.marcar_paquetes_en_distribucion()
        
        return Response({
            'message': f'Se actualizaron {updated_count} paquetes a estado "en distribución"',
            'paquetes_actualizados': updated_count
        }, status=status.HTTP_200_OK)


class ItemAsignarMotivoFalloView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    
    def update(self, request, *args, **kwargs):
        item = self.get_object()
        
        motivo_fallo_id = request.data.get('motivo_fallo_id')
        print(motivo_fallo_id)
        
        if not motivo_fallo_id:
            return Response(
                {'error': 'Se requiere el ID del motivo de fallo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .models import MotivoFalloSimple
            motivo_fallo = MotivoFalloSimple.objects.get(id=motivo_fallo_id)
            
            item.motivo_fallo = motivo_fallo
            item.save()
            
            return Response({
                'message': f'Motivo de fallo asignado correctamente al ítem {item.id}',
                'motivo_fallo': motivo_fallo.get_nombre()
            }, status=status.HTTP_200_OK)
            
        except:
            return Response(
                {'error': 'Motivo de fallo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

class PaqueteBulkAsignarPlanillaView(generics.GenericAPIView):
    # múltiples asignaciones de paquetes a planilla
    
    #transaccion realizada de forma unica como bloque
    @transaction.atomic
    def post(self, request):
        paquete_ids = request.data.get('paquete_ids', [])
        planilla_id = request.data.get('planilla_id')
        
        # paquete_ids debe ser una lista
        if isinstance(paquete_ids, int):
            paquete_ids = [paquete_ids]
        elif not isinstance(paquete_ids, list):
            paquete_ids = list(paquete_ids) if paquete_ids else []
        
        if not paquete_ids or not planilla_id:
            return Response(
                {'error': 'Se requieren paquete_ids y planilla_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            planilla = Planilla.objects.get(id=planilla_id)
            paquetes = Paquete.objects.filter(id__in=paquete_ids)
            
            nuevo_peso_total = sum(paquete.peso for paquete in paquetes)
            
            # todos los paquetes deben estar en estado "en depósito"
            invalid_paquetes = paquetes.exclude(estado=Paquete.EstadoPaquete.EN_DEPOSITO)
            if invalid_paquetes.exists():
                return Response(
                    {'error': 'Solo se pueden asignar paquetes en estado "en depósito"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # el límite de peso debe ser menor al peso limite
            if not planilla.verificar_limite_peso(nuevo_peso_total):
                return Response(
                    {'error': 'La planilla excedería el límite de peso total'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Asignar paquetes a la planilla
            posicion_inicial = planilla.items.count() + 1
            items_creados = []
            
            for i, paquete in enumerate(paquetes):
                item = Item.objects.create(
                    planilla=planilla,
                    paquete=paquete,
                    posicion=posicion_inicial + i
                )
                items_creados.append(item)
            
            return Response({
                'message': f'Se asignaron {len(items_creados)} paquetes a la planilla {planilla.numero_planilla}',
                'items_creados': len(items_creados)
            }, status=status.HTTP_200_OK)
            
        except Planilla.DoesNotExist:
            return Response(
                {'error': 'Planilla no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al asignar paquetes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )           
    
