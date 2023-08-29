import datetime
import simplejson as json


def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number


def order_total_by_vendor(order, vendor_pk):
    subtotal = 0
    total = 0
    tax = 0
    tax_dict = {}
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_pk))
    for subtotal, tax_dict in data.items():
        subtotal = float(subtotal)
        for k, v in tax_dict.items():
            tax += v['amount']
    total = subtotal + tax
    context = {
        'subtotal': subtotal,
        'tax_dict': tax_dict,
        'total': total,
    }
    return context
