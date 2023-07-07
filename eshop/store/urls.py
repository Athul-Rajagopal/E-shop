from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('', views.home, name='home'),
                  path('shop/<slug:slug>/', views.shop, name='shop'),
                  path('product/<slug:slug>/', views.product_detail, name='product_detail'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
