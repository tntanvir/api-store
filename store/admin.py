from django.contrib import admin
from .models import Category,Product,Review,Cart,CartItems,Order,OrderItem

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}
    list_display = ['name','slug']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'ordered_at']
    list_filter = ['status', 'ordered_at']

admin.site.register(Order, OrderAdmin)

admin.site.register(Category,CategoryAdmin)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(OrderItem)

