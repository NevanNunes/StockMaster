from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from inventory.models import Warehouse, Location, Category, Product

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Create Users
        manager, _ = User.objects.get_or_create(username='manager', email='manager@example.com', role=User.Role.MANAGER)
        manager.set_password('password123')
        manager.save()

        staff, _ = User.objects.get_or_create(username='staff', email='staff@example.com', role=User.Role.STAFF)
        staff.set_password('password123')
        staff.save()

        # Create Warehouses & Locations
        main_wh, _ = Warehouse.objects.get_or_create(name='Main Warehouse', code='WH01', address='123 Main St')
        prod_wh, _ = Warehouse.objects.get_or_create(name='Production Floor', code='PROD', address='456 Ind. Park')

        Location.objects.get_or_create(warehouse=main_wh, name='Receiving Area', code='WH01-RECV')
        Location.objects.get_or_create(warehouse=main_wh, name='Rack A', code='WH01-RACK-A')
        Location.objects.get_or_create(warehouse=main_wh, name='Rack B', code='WH01-RACK-B')
        Location.objects.get_or_create(warehouse=prod_wh, name='Assembly Line', code='PROD-LINE-1')

        # Create Categories
        raw_cat, _ = Category.objects.get_or_create(name='Raw Materials')
        finished_cat, _ = Category.objects.get_or_create(name='Finished Goods')

        # Create Products
        Product.objects.get_or_create(name='Steel Sheet', sku='RM-STEEL-001', category=raw_cat, uom='kg', min_stock_level=100)
        Product.objects.get_or_create(name='Plastic Pellets', sku='RM-PLASTIC-001', category=raw_cat, uom='kg', min_stock_level=500)
        Product.objects.get_or_create(name='Office Chair', sku='FG-CHAIR-001', category=finished_cat, uom='pcs', min_stock_level=20)

        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))
