from django.contrib import admin
from .models import ProductTable, CategoryTable, Size, ProductVariant, Brands, VariantImage,State,UserAddress,UserWallet

# Register your models here.
admin.site.register(CategoryTable)
admin.site.register(ProductTable)
admin.site.register(ProductVariant)
admin.site.register(Size)
admin.site.register(Brands)
admin.site.register(VariantImage)
admin.site.register(State)
admin.site.register(UserAddress)
admin.site.register(UserWallet)