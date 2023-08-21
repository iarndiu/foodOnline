from accounts.utils import send_notification
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount
from .forms import OrderForm
from .models import Payment, Order, OrderedFood
import simplejson as json
from .utils import generate_order_number
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

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
            order.save()
            order.order_number = generate_order_number(order.pk)
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

            #     try:
            #         hour = get_object_or_404(OpeningHour, pk=pk)
            #         hour.delete()
            #         return JsonResponse({
            #             'status': 'success',
            #             'message': 'Opening hour has been deleted',
            #             'pk': pk,
            #         })
            #     except:
            #         return JsonResponse({
            #             'status': 'failed',
            #             'message': 'Opening hour does not exist'
            #         })
            # else:
            #     return JsonResponse({
            #         'status': 'failed',
            #         'message': 'Invalid request'
            #     })

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
            context = {
                'user': request.user,
                'order': order,
                'to_email': order.email,
            }
            send_notification(mail_subject, mail_template, context)

            # send order received email to vendor
            mail_subject = 'You have recieved a new order.'
            mail_template = 'order/emails/new_order_received.html'
            to_emails = set()
            for item in cart_items:
                to_emails.add(item.fooditem.vendor.user.email)
            to_emails = list(to_emails)
            context = {
                'order': order,
                'to_email': to_emails,
            }
            send_notification(mail_subject, mail_template, context)

            # clear the cart if the payment is success
            # cart_items.delete()

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
