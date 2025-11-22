import django_filters
from .models import Operation

class OperationFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Operation
        fields = ['operation_type', 'status', 'start_date', 'end_date']
