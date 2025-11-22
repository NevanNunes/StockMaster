from rest_framework import serializers
from .models import Warehouse, Location, Category, Product, ProductStock, Operation, OperationLine, StockMovement

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = Location
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_total_stock(self, obj):
        return sum(stock.quantity for stock in obj.stocks.all())

class ProductStockSerializer(serializers.ModelSerializer):
    location_code = serializers.CharField(source='location.code', read_only=True)
    warehouse_name = serializers.CharField(source='location.warehouse.name', read_only=True)

    class Meta:
        model = ProductStock
        fields = '__all__'

class OperationLineSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OperationLine
        fields = ['id', 'product', 'product_sku', 'product_name', 'quantity_demanded', 'quantity_done']

class OperationSerializer(serializers.ModelSerializer):
    lines = OperationLineSerializer(many=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    source_location_name = serializers.CharField(source='source_location.name', read_only=True, allow_null=True)
    destination_location_name = serializers.CharField(source='destination_location.name', read_only=True, allow_null=True)

    class Meta:
        model = Operation
        fields = '__all__'
        read_only_fields = ['reference_number', 'status', 'created_by', 'created_at', 'updated_at', 'validated_at']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        operation = Operation.objects.create(**validated_data)
        
        # Generate Reference Number (Simple logic for now)
        operation.reference_number = f"{operation.operation_type[:3]}-{operation.id:06d}"
        operation.save()

        for line_data in lines_data:
            OperationLine.objects.create(operation=operation, **line_data)
        
        return operation

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        
        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update lines if provided (Full replacement for simplicity in this MVP)
        if lines_data is not None:
            instance.lines.all().delete()
            for line_data in lines_data:
                OperationLine.objects.create(operation=instance, **line_data)
        
        return instance

class StockMovementSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    from_loc_name = serializers.CharField(source='from_location.name', read_only=True, allow_null=True)
    to_loc_name = serializers.CharField(source='to_location.name', read_only=True, allow_null=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = StockMovement
        fields = '__all__'
