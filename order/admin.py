from django.contrib import admin
from .models import Order, Payment, OrderedFood


class PaymentAdmin(admin.ModelAdmin):
    models = Payment
    list_display = ('transaction_id', 'payment_method', 'amount', 'status')


class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('fooditem', 'order', 'quantity', 'price', 'amount', 'user', 'payment')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'payment', 'status', 'is_ordered', 'created_at')
    inlines = [OrderedFoodInline]


class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ('fooditem', 'order', 'quantity', 'price', 'amount')


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood, OrderedFoodAdmin)
