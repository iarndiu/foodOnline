from django.conf import settings
from menu.models import FoodItem
from .models import Cart


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            for i in cart_items:
                cart_count += i.quantity
        except:
            cart_count = 0

    return dict(cart_count=cart_count)


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.pk)
            subtotal += (fooditem.price * item.quantity)
        total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, total=total)
