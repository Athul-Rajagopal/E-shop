from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Cart, CartItem, WishList
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
            cart_item = user_cart.cartitem_set.all
            categories = CategoryTable.objects.all()

        except ObjectDoesNotExist:
            user_cart = Cart.objects.create(user=request.user)
            cart_item = user_cart.cartitem_set.all
            categories = CategoryTable.objects.all()

        # user_cart = Cart.objects.get(user=request.user)
        # items = user_cart.cartitem_set.all

        context = {
            'cart': cart_item,
            'user_cart': user_cart,
            'categories': categories

        }
        return render(request, 'cart/cart.html', context)
    else:
        return render(request, 'cart/cart.html')


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
                                                price=variant.price - (variant.price * variant.discount_percent) / 100)
            cart_item.save()
        return redirect('cart')


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

            if int(quantity) <= product_variant.stock:
                cart_item.quantity = int(quantity)
                cart_item.price = product_variant.price * int(quantity)
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
            wishlist_item = user_wishlist.wishlist_set.all

        except ObjectDoesNotExist:
            user_wishlist = Cart.objects.create(user=request.user)
            wishlist_item = user_wishlist.wishlist_set.all
        categories = CategoryTable.objects.all()
        context = {
            'wishlist': wishlist_item,
            'user_cart': user_wishlist,
            'categories': categories

        }
        return render(request, 'cart/wishlist.html', context)
    else:
        return redirect('home')


def add_to_wishlist(request, variant_id):
    if request.user.is_authenticated:
        variant = ProductVariant.objects.get(id=variant_id)
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)

        # try:
        #     wishlist_item = WishList.objects.get(wishlist=cart, variant=variant)
        #     if wishlist_item.quantity < variant.stock:
        #         wishlist_item.quantity += 1
        #         wishlist_item.price = wishlist_item.get_item_price()
        #         wishlist_item.save()
        #
        #     else:
        #         messages.warning(request,'stock limit reached')

        # except WishList.DoesNotExist:
        wishlist_item = WishList.objects.create(wishlist=cart, variant=variant, price=variant.price)
        wishlist_item.save()
        return redirect('wishlist')


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


def quantity_update_wishlist(request, cart_item_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        wishlist_item = WishList.objects.get(id=cart_item_id)
        product_variant = wishlist_item.variant

        if int(quantity) <= product_variant.stock:
            wishlist_item.quantity = int(quantity)
            wishlist_item.price = product_variant.price * int(quantity)
            wishlist_item.save()
            print("Cart item updated successfully.")
        else:
            print("Requested quantity exceeds available stock.")
    return redirect('wishlist')
