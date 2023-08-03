from django.shortcuts import redirect, render
from cart.models import *
from io import BytesIO

from django.urls import NoReverseMatch
from django.views.decorators.cache import cache_control
from store.models import *
from .models import *
import razorpay
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from django.template.loader import render_to_string
from xhtml2pdf import pisa


# Create your views here.


def shipping_address(request):
    if request.user.is_authenticated:
        user_details = UserAddress.objects.filter(user_id=request.user)
        states = State.objects.all()
        context = {
            'details': user_details,
            'states': states
        }

        return render(request, 'order/shipping-address.html', context)
    else:
        return redirect('signin')


def add_address(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            first_name = request.POST['firstname']
            last_name = request.POST['lastname']
            phone = request.POST['phone']
            area = request.POST['area']
            state = request.POST['state']
            pincode = request.POST['pincode']
            house = request.POST['house']

            state_id = State.objects.get(id=state)
            new_address = UserAddress.objects.create(user_id=request.user,
                                                     first_name=first_name,
                                                     last_name=last_name,
                                                     area=area,
                                                     phone=phone,
                                                     pincode=pincode,
                                                     house_name=house,
                                                     state=state_id)
            new_address.save()

            return redirect('shipping_address')


def checkout(request, address_id):
    cart = Cart.objects.get(user=request.user)
    user_wallet = UserWallet.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if cart_items:
        if request.user.is_authenticated:
            user_details = UserAddress.objects.get(id=address_id)
            user_cart = Cart.objects.get(user=request.user)
            context = {
                'details': user_details,
                'user_cart': user_cart,
                'wallet':user_wallet
            }

            return render(request, 'order/checkout.html', context)

    return redirect('home')


@cache_control(no_cache=True, must_validate=True, no_store=True)
def place_order(request, address_id):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if cart_items:
        if request.user.is_authenticated:
            try:

                address = UserAddress.objects.get(id=address_id)
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                # total_price = sum(cart_item.price for cart_item in cart_items)
                total_price = cart.total_price
                print("********************************************")
                print(total_price)

                order = Order.objects.create(user=request.user, address=address,
                                             payment_status='PENDING',
                                             payment_method='CASH_ON_DELIVERY', total_price=total_price)

                for items in cart_items:
                    order_item = OrderItem.objects.create(order=order,
                                                          product=items.variant,
                                                          price=items.variant.price,
                                                          quantity=items.quantity)
                    variant = items.variant
                    variant.stock -= items.quantity
                    variant.save()
                    order_item.save()
                if cart.coupon:
                    coupon = Coupon.objects.get(id=cart.coupon)
                    user_coupon = UserCoupon.objects.create(user=request.user, coupon=coupon)
                    user_coupon.save()
                cart_items.delete()
                return render(request, 'order/order-placed.html', {'order': order, 'order_item': order_item})

            except NoReverseMatch:
                return HttpResponse('Please select a valid payment method!')
            except UnboundLocalError:
                return redirect('checkout')

        return redirect('shipping_address')
    return redirect('home')


def view_order(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
        context = {
            'orders': orders
        }
        return render(request, 'order/view-orders.html', context)


def cancel_order(request, order_id):
    if request.user.is_authenticated:
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)

        for item in order_items:
            variant = item.product
            variant.stock += item.quantity
            variant.save()

        if order.payment_status == 'PENDING':
            order.payment_status = 'CANCELLED'
            order.save()

        elif order.payment_status == 'PAID':
            try:
                get_wallet = UserWallet.objects.get(user=request.user)
                get_wallet.wallet_amount = get_wallet.wallet_amount + Decimal(str(order.total_price))
                get_wallet.save()
                order.payment_status = 'CANCELLED'
                order.save()
            except ObjectDoesNotExist:
                user_wallet = UserWallet.objects.create(user=request.user, wallet_amount=order.total_price)
                user_wallet.save()
                order.payment_status = 'CANCELLED'
                order.save()

        return redirect('view_orders')


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.orderitem_set.all

    context = {
        'order': order,
        'items': order_items
    }
    return render(request, 'order/order-details.html', context)


def initiate_payment(request):
    if request.method == 'POST':
        # Retrieve the total price and other details from the backend
        carts = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=carts)
        # total_price = sum(item.price for item in items)
        total_price = carts.total_price
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        payment = client.order.create({'amount': int(total_price * 100), 'currency': 'INR', 'payment_capture': 1})
        print('#######################################', payment)
        print(total_price)
        response_data = {
            'order_id': payment['id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'key': settings.RAZORPAY_API_KEY
        }
        return JsonResponse(response_data)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'})


def online_payment_order(request, address_id):
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        address = UserAddress.objects.get(id=address_id)
        carts = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=carts)
        # total_price = sum(item.price * item.quantity for item in cart_items)
        total_price = carts.total_price

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_status='PAID',
            payment_method='PAYPAL',
            online_payment_id=payment_id,
            online_payment_signature=signature,
            online_payment_order_id=orderId,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.variant,
                price=item.variant.price,
                quantity=item.quantity

            )
            variant = item.variant
            variant.stock -= item.quantity
            variant.save()
        if carts.coupon:
            coupon = Coupon.objects.get(id=carts.coupon)
            user_coupon = UserCoupon.objects.create(user=request.user, coupon=coupon)
            user_coupon.save()

        cart_items.delete()

        return JsonResponse({'orderid': order.id})
    else:
        # Handle invalid request method (GET, etc.)
        return JsonResponse({'error': 'Invalid request method'})


@cache_control(no_cache=True, must_validate=True, no_store=True)
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order/order-success.html', {'order': order})


def return_order(request, order_id):
    if request.user.is_authenticated:
        order = Order.objects.get(id=order_id)
        if order.payment_status == 'DELIVERED':
            order.payment_status = 'RETURNED'
            order.save()

        return redirect('view_orders')

    return render(request, 'order/view-orders.html')


def order_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.orderitem_set.all

    context = {
        'order': order,
        'items': order_items
    }
    return render(request, 'order/order-invoice.html', context)


# download the invoice pdf
def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items = order.orderitem_set.all()

    # Render the PDF template with CSS styles
    template = 'order/order-invoice.html'
    context = {'order': order, 'items': items}
    html = render_to_string(template, context)

    # Create a PDF document using xhtml2pdf
    pdf_file = BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)

    # Set the response with the PDF content as an attachment
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_invoice.pdf"'
    return response

def wallet_pay(request,address_id):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if cart_items:
        if request.user.is_authenticated:
            try:

                address = UserAddress.objects.get(id=address_id)
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                # total_price = sum(cart_item.price for cart_item in cart_items)
                total_price = cart.total_price
                print("********************************************")
                print(total_price)

                order = Order.objects.create(user=request.user, address=address,
                                             payment_status='PAID',
                                             payment_method='PAY USING WALLET', total_price=total_price)

                for items in cart_items:
                    order_item = OrderItem.objects.create(order=order,
                                                          product=items.variant,
                                                          price=items.variant.price,
                                                          quantity=items.quantity)
                    variant = items.variant
                    variant.stock -= items.quantity
                    variant.save()
                    order_item.save()
                if cart.coupon:
                    coupon = Coupon.objects.get(id=cart.coupon)
                    user_coupon = UserCoupon.objects.create(user=request.user, coupon=coupon)
                    user_coupon.save()
                cart_items.delete()
                wallet = UserWallet.objects.get(user=request.user)
                print('#########################',wallet.wallet_amount)
                wallet.wallet_amount -= total_price
                print('#########################', wallet.wallet_amount)
                return render(request, 'order/order-placed.html', {'order': order, 'order_item': order_item})

            except NoReverseMatch:
                return HttpResponse('Please select a valid payment method!')
            except UnboundLocalError:
                return redirect('checkout')

        return redirect('shipping_address')
    return redirect('cart')
