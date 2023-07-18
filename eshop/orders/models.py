from datetime import timedelta, timezone
from django.db import models
from django.utils import timezone
from store.models import *
from django.contrib.auth.models import User


# Create your models here.

class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'pending'),
        ('PAID', 'paid'),
        ('CANCELLED', 'cancelled'),
        ('DELIVERED', 'Delivered'),
        ('SHIPPED', 'Shipped'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('RAZORPAY', 'razorpay'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE)
    total_price = models.FloatField(null=False)
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='ordered')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    message = models.TextField(null=True)
    tracking_no = models.CharField(max_length=150, null=True)
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateTimeField(blank=True, null=True)

    online_payment_id = models.CharField(max_length=100,blank=True,null=True)
    online_payment_order_id = models.CharField(max_length=100,null=True,blank=True)
    online_payment_signature = models.CharField(max_length=100,null=True,blank=True)

    def _str_(self):
        return f"{self.id, self.tracking_no}"

    def str(self):
        return f"{self.id}  {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_date:
            self.order_date = timezone.now()  # Set the order date to the current time if it's not set
        if not self.delivery_date:
            self.delivery_date = self.order_date + timedelta(hours=24)
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.IntegerField(null=False)

    def _str_(self):
        return f"{self.order.id, self.order.tracking_no}"


# class Coupon(models.Model):
#     code = models.CharField(max_length=50, unique=True)
#     discount = models.FloatField()
#     valid_from = models.DateTimeField(default=timezone.now)
#     valid_to = models.DateTimeField()
#     active = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.code
