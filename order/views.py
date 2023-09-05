from .utils import order_total_by_vendor
from django.contrib.sites.shortcuts import get_current_site
from accounts.utils import send_notification
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amount
from .forms import OrderForm
from .models import Payment, Order, OrderedFood
from menu.models import FoodItem
import simplejson as json
from .utils import generate_order_number
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_pks = set()
    for i in cart_items:
        vendors_pks.add(i.fooditem.vendor.pk)
    vendors_pks = list(vendors_pks)

    # {vendor_id: {subtotal: {tax_data}}}
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.pk, vendor_id__in=vendors_pks)
        v_id = fooditem.vendor.pk
        k[v_id] = k.get(v_id, 0) + (fooditem.price * i.quantity)

    # tax
    for v_id, subtotal in k.items():
        tax_dic = {}
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
        total_data.update({v_id: {str(subtotal): tax_dic}})

    total = get_cart_amount(request)['total']
    total_tax = get_cart_amount(request)['tax']
    tax_data = get_cart_amount(request)['tax_dic']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.user = request.user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.total = total
            order.total_tax = total_tax
            order.tax_data = json.dumps(tax_data)
            order.payment_method = request.POST['payment_method']
            order.total_data = json.dumps(total_data)
            order.save()
            order.order_number = generate_order_number(order.pk)
            order.vendors.add(*vendors_pks)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'order/place_order.html', context)
        else:
            print(form.errors)

    return render(request, 'order/place_order.html')


@login_required(login_url='login')
def payment(request):
    # check if the request is ajax
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            # store the payment details in payment model
            order_number = request.POST.get('order_number')
            transaction_id = request.POST.get('transaction_id')
            payment_method = request.POST.get('payment_method')
            status = request.POST.get('status')

            order = Order.objects.get(user=request.user, order_number=order_number)
            payment = Payment(
                user=request.user,
                transaction_id=transaction_id,
                payment_method=payment_method,
                amount=order.total,
                status=status
            )
            payment.save()

            # update the order model
            order.payment = payment
            order.is_ordered = True
            order.save()

            # move the cart items to ordered food model
            cart_items = Cart.objects.filter(user=request.user)
            for item in cart_items:
                ordered_food = OrderedFood(
                    order=order,
                    payment=payment,
                    user=request.user,
                    fooditem=item.fooditem,
                    quantity=item.quantity,
                    price=item.fooditem.price,
                    amount=item.fooditem.price * item.quantity
                )
                ordered_food.save()

            # send order confirmation email to customer
            mail_subject = 'Thank you for ordering with us.'
            mail_template = 'order/emails/order_confirmation_email.html'
            ordered_food = OrderedFood.objects.filter(order=order)
            customer_subtotal = 0
            for item in ordered_food:
                customer_subtotal += (item.price * item.quantity)
            tax_data = json.loads(order.tax_data)
            context = {
                'user': request.user,
                'order': order,
                'to_email': order.email,
                'ordered_food': ordered_food,
                'customer_subtotal': customer_subtotal,
                'tax_data': tax_data,
                'domain': get_current_site(request),
            }
            send_notification(mail_subject, mail_template, context)

            # send order received email to vendor
            mail_subject = 'You have recieved a new order.'
            mail_template = 'order/emails/new_order_received.html'
            to_emails = []
            for item in cart_items:
                if item.fooditem.vendor.user.email not in to_emails:
                    to_emails.append(item.fooditem.vendor.user.email)
                    ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=item.fooditem.vendor)
                    context = {
                        'order': order,
                        'to_email': item.fooditem.vendor.user.email,
                        'domain': get_current_site(request),
                        'ordered_food_to_vendor': ordered_food_to_vendor,
                        'vendor_subtotal': order_total_by_vendor(order, item.fooditem.vendor.pk)['subtotal'],
                        'tax_data': order_total_by_vendor(order, item.fooditem.vendor.pk)['tax_dict'],
                        'vendor_total': order_total_by_vendor(order, item.fooditem.vendor.pk)['total'],
                    }
                    send_notification(mail_subject, mail_template, context)

            # clear the cart if the payment is success
            cart_items.delete()

            # return back to ajax with the status success/fail
            return JsonResponse({
                'order_number': order_number,
                'transaction_id': transaction_id,
            })

    return HttpResponse('payment')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.fooditem.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'order/order_complete.html', context)
    except:
        return redirect('home')
