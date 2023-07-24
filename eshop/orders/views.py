from django.shortcuts import redirect, render
from cart.models import *
from store.models import *
from .models import *
import razorpay
from django.conf import settings
from django.http import JsonResponse


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
    if request.user.is_authenticated:
        user_details = UserAddress.objects.get(id=address_id)
        user_cart = Cart.objects.get(user=request.user)
        context = {
            'details': user_details,
            'user_cart': user_cart
        }

        return render(request, 'order/checkout.html', context)


def place_order(request, address_id):
    if request.user.is_authenticated:
        address = UserAddress.objects.get(id=address_id)
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(cart_item.price for cart_item in cart_items)
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

        cart_items.delete()
        return render(request, 'order/order-placed.html',{'order':order,'order_item':order_item})


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
        order.delete()

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
        total_price = sum(item.price for item in items)
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        payment = client.order.create({'amount': int(total_price * 100), 'currency': 'INR', 'payment_capture': 1})
        print('#######################################',payment)
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
        total_price = sum(item.price * item.quantity for item in cart_items)

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

            cart_items.delete()

        return JsonResponse({'orderid': order.id})
    else:
        # Handle invalid request method (GET, etc.)
        return JsonResponse({'error': 'Invalid request method'})


def order_success(request,order_id):
    order = Order.objects.get(id=order_id)
    return render(request,'order/order-success.html',{'order':order})