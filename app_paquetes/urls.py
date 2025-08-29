# app_paquetes/urls.py (corregido)
from django.urls import path
from .views import (
    PaqueteListView,
    PaqueteCreateView,
    PaqueteAssignPlanillaView,
    PlanillaDetailView,
    PlanillaDistribuirView,
    ItemAssignMotivoFalloView,
    PaqueteBulkAssignPlanillaView,
    MotivoSimpleListView,
)

app_name = 'app_paquetes'

urlpatterns = [
    # paquetes
    path('paquetes/', PaqueteListView.as_view(), name='paquete-list'),
    path('paquetes/create/', PaqueteCreateView.as_view(), name='paquete-create'),
    path('paquetes/<int:pk>/assign-planilla/', PaqueteAssignPlanillaView.as_view(), name='paquete-assign-planilla'),
    path('paquetes/bulk-assign-planilla/', PaqueteBulkAssignPlanillaView.as_view(), name='paquete-bulk-assign-planilla'),
    
    # planillas
    path('planillas/<int:pk>/', PlanillaDetailView.as_view(), name='planilla-detail'),
    path('planillas/<int:pk>/distribuir/', PlanillaDistribuirView.as_view(), name='planilla-distribuir'),
    
    # items
    path('items/<int:pk>/assign-motivo/', ItemAssignMotivoFalloView.as_view(), name='item-assign-motivo'),

    # motivos
    path('motivos/', MotivoSimpleListView.as_view(), name='motivo-list')
]   