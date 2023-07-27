

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import  User
from phone_field import PhoneField


# Create your models here.

class CategoryTable(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category/')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop', kwargs={'slug': self.slug})

    class Meta:
        db_table = 'store_categorytable'


class Brands(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class ProductTable(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(CategoryTable,on_delete=models.CASCADE)
    brandName = models.ForeignKey(Brands,on_delete=models.CASCADE,null=True)
    slug = models.SlugField(blank=True)
    is_active = models.BooleanField(default=True)
    discount_percent = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('shop',kwargs={'slug': self.slug})

class Size(models.Model):
    size = models.CharField(max_length=15)

    def __str__(self):
        return self.size

class ProductVariant(models.Model):
    product = models.ForeignKey(ProductTable,on_delete=models.CASCADE)
    size = models.ForeignKey(Size,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    display_image = models.ImageField(upload_to='product_image/',null=True)
    slug = models.SlugField(blank=True,unique=True)
    is_active = models.BooleanField(default=True)
    # discount_percent = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        if not self.slug:
            slug_str = f"{self.product.name} {self.size}"
            self.slug=slugify(slug_str)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} {self.size}"

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class VariantImage(models.Model):
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    display_image = models.ImageField(upload_to='product_image/variant_image/', null=True)

    def __str__(self):
        return self.product_variant.product.name




## user profile

class State(models.Model):
    state = models.CharField(max_length=50)
    def __str__(self):
        return self.state
class UserAddress(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50,null=True)
    phone = models.CharField(max_length=15,blank=True)
    area = models.TextField()
    house_name = models.TextField()
    city = models.CharField()
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    pincode = models.CharField()

    def __str__(self):
        return f"{self.user_id.username}"



class UserWallet(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    wallet_amount = models.DecimalField(max_digits=8,decimal_places=2,default=0)

    def __str__(self):
        return self.user.username