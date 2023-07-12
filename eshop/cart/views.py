from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Cart, CartItem, WishList
from store.models import ProductVariant, ProductTable, CategoryTable
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Sum
from django.db.models import F


# Create your views here.
def cart(request):
    if request.user.is_authenticated:
        user_cart = Cart.objects.get(user=request.user)
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
        return redirect('home')


def add_to_cart(request, variant_id):
    variant = ProductVariant.objects.get(id=variant_id)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, price=variant.price)

    if not created:
        if cart_item.quantity < variant.stock:
            cart_item.quantity += 1
            cart_item.price = cart_item.get_item_price()
            cart_item.save()
        else:
            # Handle case when quantity exceeds stock
            # You can show an error message or take appropriate action
            pass
    else:
        cart_item.quantity = 1  # Set initial quantity to 1 for newly created item
        cart_item.price = cart_item.get_item_price()
        cart_item.save()

    return redirect('cart')


def remove_cart_item(request, id):
    CartItem.objects.get(id=id).delete()
    return redirect('cart')


# views.py
def quantity_update(request, cart_item_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        print("########################", quantity)
        cart_item = CartItem.objects.get(id=cart_item_id)
        product_variant = cart_item.variant

        if int(quantity) <= product_variant.stock:
            cart_item.quantity = int(quantity)
            cart_item.price = product_variant.price * int(quantity)
            cart_item.save()
            print("Cart item updated successfully.")
        else:
            print("Requested quantity exceeds available stock.")
    return redirect('cart')


# wishlist
def wishlist(request):
    if request.user.is_authenticated:
        user_wishlist = Cart.objects.get(user=request.user)
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
    variant = ProductVariant.objects.get(id=variant_id)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    wishlist_item, created = WishList.objects.get_or_create(wishlist=cart, variant=variant, price=variant.price)
    if not created:
        if wishlist_item.quantity < variant.stock:
            wishlist_item.quantity += 1

            wishlist_item.price = wishlist_item.get_item_price()
            wishlist_item.save()

        else:
            # Handle case when quantity exceeds stock
            # You can show an error message or take appropriate action
            pass

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
