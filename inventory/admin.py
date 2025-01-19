from django.contrib import admin

# Register your models here.
from inventory.models import Supplier, Product, SaleOrder, StockMovement

admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(SaleOrder)
admin.site.register(StockMovement)

