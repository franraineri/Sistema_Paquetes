# app_paquetes/urls.py (corregido)
from django.urls import path
from .views import (
    PaqueteListView,
    PaqueteCreateView,
    PaqueteAsignarPlanillaView,
    PlanillaDetailView,
    PlanillaDistribuirView,
    ItemAsignarMotivoFalloView,
    PaqueteBulkAsignarPlanillaView,
    MotivoSimpleListView,
)

app_name = 'app_paquetes'

urlpatterns = [
    # paquetes
    path('paquetes/', PaqueteListView.as_view(), name='paquete-list'),
    path('paquetes/crear/', PaqueteCreateView.as_view(), name='paquete-create'),
    path('paquetes/<int:pk>/asignar-planilla/', PaqueteAsignarPlanillaView.as_view(), name='paquete-asignar-planilla'),
    path('paquetes/bulk-asignar-planilla/', PaqueteBulkAsignarPlanillaView.as_view(), name='paquete-bulk-asignar-planilla'),
    
    # planillas
    path('planillas/<int:pk>/', PlanillaDetailView.as_view(), name='planilla-detail'),
    path('planillas/<int:pk>/distribuir/', PlanillaDistribuirView.as_view(), name='planilla-distribuir'),
    
    # items
    path('items/<int:pk>/asignar-motivo/', ItemAsignarMotivoFalloView.as_view(), name='item-asignar-motivo'),

    # motivos
    path('motivos/', MotivoSimpleListView.as_view(), name='motivo-list')
]   