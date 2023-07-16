from django.shortcuts import redirect, render
from cart.models import *
from store.models import *
from .models import *


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
        return render(request, 'order/order-placed.html')


def view_order(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
        context = {
            'orders': orders
        }
        return render(request, 'order/view-orders.html', context)


def cancel_order(request, order_id):
    if request.user.is_authenticated:
        Order.objects.get(id=order_id).delete()

        return redirect('view_orders')


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.orderitem_set.all

    context = {
        'order': order,
        'items': order_items
    }
    return render(request, 'order/order-details.html', context)
