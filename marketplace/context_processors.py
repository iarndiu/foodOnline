from django.template.defaultfilters import slugify
from django.conf import settings
from menu.models import FoodItem
from .models import Cart, Tax


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
    total = 0
    tax = 0
    tax_dic = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.pk)
            subtotal += (fooditem.price * item.quantity)

    get_tax = Tax.objects.filter(is_active=True)
    for i in get_tax:
        tax_type = i.tax_type
        tax_slug = slugify(tax_type)
        tax_rate = i.tax_rate
        tax_amount = round(tax_rate * subtotal / 100, 2)
        tax_dic[tax_type] = {
            'slug': tax_slug,
            'rate': tax_rate,
            'amount': tax_amount,
        }
        # tax_dic[tax_type] = {tax_slug: {str(tax_rate): tax_amount}}
        tax += tax_amount
        total += tax_amount

    total += subtotal

    return dict(subtotal=subtotal, total=total, tax=tax, tax_dic=tax_dic)
