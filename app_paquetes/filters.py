import django_filters
from .models import Paquete

class PaqueteFilter(django_filters.FilterSet):
    estado = django_filters.ChoiceFilter(choices=Paquete.EstadoPaquete)
    cliente = django_filters.NumberFilter(field_name='cliente_id')
    tipo = django_filters.ChoiceFilter(choices=Paquete.TipoPaquete)

    class Meta:
        model = Paquete
        fields = ['estado', 'cliente', 'tipo']