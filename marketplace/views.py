from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amount


# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_cnt = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_cnt': vendor_cnt,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if food exists
            try:
                fooditem = FoodItem.objects.get(pk=food_pk)
                # check if the food is already in cart
                try:
                    # yes - increase
                    cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    cart.quantity += 1
                    cart.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Increased the cart quantity',
                        'cart_counter': get_cart_counter(request),
                        'qty': cart.quantity,
                        'cart_amount': get_cart_amount(request),
                    })
                except:
                    # no - create cart
                    cart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Added the food item to cart',
                        'cart_counter': get_cart_counter(request),
                        'qty': cart.quantity,
                        'cart_amount': get_cart_amount(request),
                    })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Food item does not exist'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })


def decrease_cart(request, food_pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if food exists
            try:
                fooditem = FoodItem.objects.get(pk=food_pk)
                # check if the food is already in cart
                try:
                    # yes - decrease
                    cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if cart.quantity > 1:
                        cart.quantity -= 1
                        cart.save()
                    else:
                        cart.delete()
                        cart.quantity = 0  # ??
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Increased the cart quantity',
                        'cart_counter': get_cart_counter(request),
                        'qty': cart.quantity,
                        'cart_amount': get_cart_amount(request),
                    })
                except:
                    # no - message
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'You do not have this item in your cart',
                    })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Food item does not exist'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if cart exists
            try:
                cart_item = Cart.objects.get(user=request.user, pk=cart_pk)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Cart item has been deleted',
                        'cart_counter': get_cart_counter(request),
                        'cart_amount': get_cart_amount(request),
                    })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Cart item does not exist'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request'
            })
