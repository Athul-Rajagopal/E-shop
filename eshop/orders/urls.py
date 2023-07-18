from django.urls import path
from . import views

urlpatterns = [
    path('shipping-address', views.shipping_address, name='shipping_address'),
    path('checkout/<int:address_id>', views.checkout, name='checkout'),
    path('place-order/<int:address_id>', views.place_order, name='place_order'),
    path('view-orders',views.view_order,name='view_orders'),
    path('cancel-order/<int:order_id>',views.cancel_order,name='cancel_order'),
    path('order-details/<int:order_id>', views.order_detail, name='order_details'),
    path('add-address', views.add_address, name='add_address'),
    path('initiate_payment', views.initiate_payment, name='initiate_payment'),
    path('online_payment_order/<int:address_id>', views.online_payment_order, name='online_payment_order'),
    path('order_success', views.order_success, name='order_success')
]