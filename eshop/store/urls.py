from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('', views.home, name='home'),
                  path('shop/<slug:slug>/', views.shop, name='shop'),
                  path('product/<slug:slug>/', views.product_detail, name='product_detail'),
                  path('user-profile', views.user_profile_home, name='user_profile'),
                  path('user-address', views.user_address, name='user_address'),
                  path('add-user-address', views.add_user_address, name='add_user_address'),
                  path('edit-address/<int:address_id>', views.edit_address, name='edit_address'),
                  path('delete-address/<int:address_id>', views.delete_address, name='delete_address'),
                  path('change-password', views.change_user_password, name='change_user_password'),
                  path('shop', views.search_product, name='search_product')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
