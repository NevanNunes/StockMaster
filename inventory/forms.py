from django import forms
from .models import Product, Operation, OperationLine, Partner, Warehouse

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'uom', 'min_stock_level']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ['partner', 'notes'] # Warehouse is not directly on Operation?
        # Wait, Operation model has partner, but NOT warehouse?
        # Let's check models.py again.
        
    # Operation model has source_location and destination_location.
    # For a receipt, destination_location is the warehouse (or a location in it).
    # The template has "Warehouse" dropdown.
    
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all(), required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partner'].label = "Supplier"
        # Filter partners to suppliers if needed
        self.fields['partner'].queryset = Partner.objects.filter(partner_type='SUPPLIER')

class OperationLineForm(forms.ModelForm):
    class Meta:
        model = OperationLine
        fields = ['product', 'quantity_demanded']
