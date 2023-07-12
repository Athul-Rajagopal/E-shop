from django.urls import path
from . import views

urlpatterns = [
    path('cart', views.cart, name='cart'),
    path('add-to-cart/<int:variant_id>', views.add_to_cart, name='add_to_cart'),
    path('remove-cart-item/<int:id>', views.remove_cart_item, name='remove_cart_item'),
    path('quantity_update/<int:cart_item_id>/', views.quantity_update, name='quantity_update'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:variant_id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-wishlist-item/<int:id>', views.remove_wishlist_item, name='remove_wishlist_item'),
    path('shift-to-cart/<int:item_id>', views.wishlist_to_cart, name='wishlist_to_cart'),
    path('quantity_update_wishlist/<int:cart_item_id>/', views.quantity_update_wishlist, name='quantity_update_wishlist'),
]
