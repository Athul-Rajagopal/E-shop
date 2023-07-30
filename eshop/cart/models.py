from datetime import date

from _decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from store.models import ProductVariant
from django.utils import timezone


# Create your models here.
# cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now())
    total_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    coupon = models.CharField(max_length=10, null=True)

    def _str_(self):
        return f"Cart #{self.pk} for {self.user.username}"

    def get_total_price(self):
        return self.cartitem_set.aggregate(total_price=Sum('price'))['total_price']


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def get_item_price(self):
        return Decimal(self.price) * Decimal(self.quantity)


class WishList(models.Model):
    wishlist = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def get_item_price(self):
        return Decimal(self.price) * Decimal(self.quantity)


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_price = models.IntegerField(default=150)
    expiry_date = models.DateField(default=date(2023, 1, 1))  # Use the date function directly

    minimum_amount = models.IntegerField(default=500)
    is_expired = models.BooleanField(default=False)

    def _str_(self):
        return self.coupon_code

    def check_expiry_status(self):
        if self.expiry_date < date.today():
            self.is_expired = True
        else:
            self.is_expired = False


class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    total_price = models.IntegerField(null=True)
