import django_filters
from .models import Operation

class OperationFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    sku = django_filters.CharFilter(field_name='lines__product__sku', lookup_expr='icontains')
    partner_name = django_filters.CharFilter(field_name='partner__name', lookup_expr='icontains')

    class Meta:
        model = Operation
        fields = ['operation_type', 'status', 'source_location', 'destination_location']
