from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import *
from store.models import ProductVariant, ProductTable, CategoryTable
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Sum
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
def cart(request):
    if request.user.is_authenticated:
        try:
            user_cart = Cart.objects.get(user=request.user)
            cart_item = user_cart.cartitem_set.all()
            categories = CategoryTable.objects.all()
            total_price = sum(cart_item.price for cart_item in cart_item)
            coupons = Coupon.objects.filter(minimum_amount__lte=total_price)
            user_cart.total_price = total_price
            user_cart.save()
        except ObjectDoesNotExist:
            user_cart = Cart.objects.create(user=request.user)
            cart_item = user_cart.cartitem_set.all
            categories = CategoryTable.objects.all()
            total_price = sum(cart_item.price for cart_item in cart_item)
            user_cart.total_price = total_price
            user_cart.save()
        # user_cart = Cart.objects.get(user=request.user)
        # items = user_cart.cartitem_set.all

        context = {
            'cart': cart_item,
            'user_cart': user_cart,
            'categories': categories,
            'total_price': total_price,
            # 'coupons': coupons

        }
        return render(request, 'cart/cart.html', context)
    else:
        return redirect('signin')


def add_to_cart(request, variant_id):
    if request.user.is_authenticated:
        variant = ProductVariant.objects.get(id=variant_id)
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)

        try:
            cart_item = CartItem.objects.get(cart=cart, variant=variant)
            if cart_item.quantity < variant.stock:
                cart_item.quantity += 1
                cart_item.price = cart_item.get_item_price()
                cart_item.save()

            elif cart_item.quantity > variant.stock:
                messages.error(request, 'maximum quantity reached')

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart=cart, variant=variant,
                                                price=variant.price - (
                                                        variant.price * variant.product.discount_percent) / 100)
            cart_item.save()
        return redirect('cart')
    else:
        return redirect('signin')


def remove_cart_item(request, id):
    if request.user.is_authenticated:
        CartItem.objects.get(id=id).delete()
        return redirect('cart')


# views.py
def quantity_update(request, cart_item_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            quantity = request.POST.get('quantity')
            cart_item = CartItem.objects.get(id=cart_item_id)
            product_variant = cart_item.variant
            discount_price = product_variant.price - (
                    product_variant.price * product_variant.product.discount_percent) / 100

            if int(quantity) <= product_variant.stock:
                cart_item.quantity = int(quantity)
                cart_item.price = discount_price * int(quantity)
                cart_item.save()
                print("Cart item updated successfully.")
            else:
                messages.warning(request, 'Requested quantity exceeds available stock.')
                print("Requested quantity exceeds available stock.")
        return redirect('cart')


# wishlist
def wishlist(request):
    if request.user.is_authenticated:
        try:
            user_wishlist = Cart.objects.get(user=request.user)
            wishlist_item = user_wishlist.wishlist_set.all()

        except ObjectDoesNotExist:
            user_wishlist = Cart.objects.create(user=request.user)
            wishlist_item = user_wishlist.wishlist_set.all()
        categories = CategoryTable.objects.all()
        context = {
            'wishlist': wishlist_item,
            'user_cart': user_wishlist,
            'categories': categories

        }
        return render(request, 'cart/wishlist.html', context)
    else:
        return redirect('signin')


def add_to_wishlist(request, variant_id):
    if request.user.is_authenticated:
        variant = ProductVariant.objects.get(id=variant_id)
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)

        # except WishList.DoesNotExist:
        wishlist_item = WishList.objects.create(wishlist=cart, variant=variant,
                                                price=variant.price - (
                                                        variant.price * variant.product.discount_percent) / 100)
        wishlist_item.save()
        return redirect('wishlist')
    else:
        return redirect('signin')


def remove_wishlist_item(request, id):
    WishList.objects.get(id=id).delete()
    return redirect('wishlist')


def wishlist_to_cart(request, item_id):
    item = WishList.objects.get(id=item_id)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=item.variant, price=item.price)
    if not created:
        if cart_item.quantity < item.variant.stock:
            cart_item.quantity += item.quantity

            cart_item.price = cart_item.get_item_price()
            cart_item.save()
        elif cart_item.quantity > item.variant.stock:
            messages.error(request, 'maximum limit reached')
    return redirect('cart')


def apply_coupon(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        total_price = sum(cart_item.price for cart_item in cart_items)
        print("###########################")
        if request.method == 'POST':
            coupon_code = request.POST.get('coupon')
            print('$$$$$$$$$$$$$$$$$$$$$$$$$', coupon_code)
            try:
                print("^^^^^^^^^^^^^^^^^^^^^^^^")
                coupon = Coupon.objects.get(coupon_code=coupon_code, is_expired=False, minimum_amount__lte=total_price)
                print("^^^^^^^^^^^^^^^^^^^^^", coupon.id)
                print("^^^^^^^^^^^^^^^^^^^^^", coupon.discount_price)
                # Add a new condition to check if the user has already applied the coupon
                user_coupon = UserCoupon.objects.filter(user=request.user, coupon=coupon.id).first()
                print(user_coupon)
                if user_coupon is None:
                    # User has not already applied the coupon
                    cart.coupon = coupon.id
                    # cart.save()
                    # print("#############################",cart.coupon)
                    total_price -= coupon.discount_price
                    cart.total_price = total_price
                    print("total_....................................price")

                    print(total_price)
                    cart.save()

                else:
                    coupon_status = 'already_used'  # Set the coupon status as 'already_used'
                    print("already used this coupon for this user")
                    # User has already applied the coupon
            except Coupon.DoesNotExist:
                coupon_status = 'invalid'  # Set the coupon status as 'invalid'
                # Coupon not valid
        used_coupon = Coupon.objects.get(id=cart.coupon)
        print(used_coupon)
        categories = CategoryTable.objects.all()
        context = {
            'categories': categories,
            'cart': cart_items,
            'user_cart': cart,
            'total_price': total_price,
            'used_coupon': used_coupon,

        }
        return render(request, 'cart/cart.html', context)

