from django.urls import path
from . import views

urlpatterns = [
    path('_admin', views.admin_login, name='admin_login'),
    path('admin-home', views.home, name='admin_home'),
    path('user-details', views.userdetails, name='user_details'),
    path('block-user/<int:id>/', views.block_user, name='block_user'),
    path('unblock-user/<int:id>/', views.unblock_user, name='unblock_user'),
    path('admin-logout', views.admin_logout, name='admin_logout'),
    path('category', views.category, name='category'),
    path('add-category', views.add_category, name='add_category'),
    path('disable-category/<int:id>', views.disable_category, name='disable_category'),
    path('enable-category/<int:id>', views.enable_category, name='enable_category'),
    path('products', views.products, name='products'),
    path('view-product/<int:product_id>', views.view_product, name='view_product'),
    path('add-product', views.add_product, name='add_product'),
    path('add-variant/<int:product_id>', views.add_variant, name='add_variant'),
    path('disable-variant/<int:variant_id>', views.disable_variant, name='disable_variant'),
    path('enable-variant/<int:variant_id>', views.enable_variant, name='enable_variant'),
    path('disable-product/<int:product_id>', views.disable_product, name='disable_product'),
    path('enable-product/<int:product_id>', views.enable_product, name='enable_product'),
    path('edit-category/<int:category_id>', views.edit_category, name='edit_category'),
    path('edit-product/<int:product_id>', views.edit_product, name='edit_product'),
    path('edit-variant/<int:variant_id>', views.edit_variant, name='edit_variant')
]
