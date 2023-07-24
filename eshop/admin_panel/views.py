from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from store.models import CategoryTable, ProductTable, ProductVariant, Brands, Size, VariantImage
from orders.models import *
from image_cropping.utils import get_backend
from PIL import Image

# Create your views here.
def admin_login(request):
    if request.user.is_superuser and request.user.is_authenticated:
        return render(request, 'admin_panel/adminHome.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass1']

        admin = authenticate(username=username, password=password)
        print(admin)
        if admin is not None:
            if admin.is_superuser:
                login(request, admin)
                return render(request, 'admin_panel/adminHome.html')
        else:
            messages.error(request, "sorry, you are not a admin")
            return redirect('admin_login')
    return render(request, 'admin_panel/adminlogin.html')


def home(request):
    last_orders = Order.objects.order_by('-order_date')[:5]

    return render(request, 'admin_panel/adminHome.html', {
        'last_orders': last_orders})


def userdetails(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'admin_panel/userdetails.html', context)


def block_user(request, id):
    if request.user.is_superuser:

        user = get_object_or_404(User, id=id, is_superuser=False)
        user.is_active = False
        user.save()
        return redirect('user_details')
    else:
        return redirect('user_details')


def unblock_user(request, id):
    if request.user.is_superuser:
        user = get_object_or_404(User, id=id, is_superuser=False)
        user.is_active = True
        user.save()
        return redirect('user_details')
    else:
        return redirect('user_details')


def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('admin_login')


def category(request):
    if request.user.is_superuser:
        categories = CategoryTable.objects.all()
        context = {
            'categories': categories
        }
        return render(request, 'admin_panel/category.html', context)


def add_category(request):
    if request.user.is_superuser:
        if request.method == "POST":
            category_name = request.POST['category_name']
            image = request.FILES['image']

            new_category = CategoryTable.objects.create(name=category_name, image=image)
            new_category.save()

            return redirect('category')
        else:
            return redirect('category')


def disable_category(request, id):
    if request.user.is_superuser:
        cat = CategoryTable.objects.get(id=id)
        cat.is_active = False
        cat.save()
        return redirect('category')


def enable_category(request, id):
    if request.user.is_superuser:
        cat = CategoryTable.objects.get(id=id)
        cat.is_active = True
        cat.save()
        return redirect('category')


def products(request):
    if request.user.is_superuser:
        products = ProductTable.objects.all()
        context = {
            'products': products
        }
    return render(request, 'admin_panel/product.html', context)


def view_product(request, product_id):
    if request.user.is_superuser:
        product = ProductTable.objects.get(id=product_id)
        variants = product.productvariant_set.all
        var = product.productvariant_set.first()
        context = {
            'product': product,
            'variants': variants,
            'var': var
        }
        return render(request, 'admin_panel/view_product.html', context)


def add_product(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            product_name = request.POST['product_name']
            category = request.POST['category']
            brand = request.POST['brand']
            description = request.POST['description']

            # variant side
            size = request.POST['size']
            price = request.POST['price']

            stock = request.POST['stock']
            variant_image = request.FILES['variant_image']
            variant_images = request.FILES.getlist('variant_images')

            print(product_name, category, brand, size, price, stock)

            category_id = CategoryTable.objects.get(id=category)
            brand_id = Brands.objects.get(id=brand)
            size_id = Size.objects.get(id=size)

            product = ProductTable.objects.create(name=product_name, description=description, category=category_id,
                                                  brandName=brand_id)
            product.save()
            product_variant = ProductVariant.objects.create(product=product, size=size_id, price=price, stock=stock,
                                                            display_image=variant_image)
            product_variant.save()

            # image cropping
            # cropping = request.POST.get('eshop_productvariant_display_image')
            # if cropping:
            #     image = Image.open(variant_image)
            #     backend = get_backend()
            #     image = backend.crop(image, *map(float, cropping.split(',')))
            #     image.save(product_variant.display_image.path)

            for image in variant_images:
                variant_images = VariantImage.objects.create(product_variant=product_variant, display_image=image)
                variant_images.save()

            return redirect('products')

        catagories = CategoryTable.objects.all()
        brands = Brands.objects.all()
        sizes = Size.objects.all()

        context = {
            'brands': brands,
            'catagories': catagories,
            'sizes': sizes
        }

        return render(request, 'admin_panel/add_product.html', context)


def edit_product(request, product_id):
    if request.user.is_superuser:
        product = ProductTable.objects.get(id=product_id)
        catagories = CategoryTable.objects.all()
        brands = Brands.objects.all()
        sizes = Size.objects.all()

        context = {
            'brands': brands,
            'catagories': catagories,
            'sizes': sizes,
            'product': product
        }

        if request.method == "POST":
            product_name = request.POST['product_name']
            category = request.POST['category']
            brand = request.POST['brand']
            description = request.POST['description']

            category_id = CategoryTable.objects.get(name=category)
            brand_id = Brands.objects.get(name=brand)

            product.name = product_name
            product.category = category_id
            product.brandName = brand_id
            product.description = description

            product.save()
            return redirect('products')

        return render(request, 'admin_panel/edit-product.html', context)
    else:
        return redirect('admin_home')


def add_variant(request, product_id):
    if request.user.is_superuser:
        if request.method == 'POST':
            stock = request.POST['stock']
            size = request.POST['size']
            price = request.POST['price']
            variant_image = request.FILES['variant_image']
            variant_images = request.FILES.getlist('variant_images')
            product = ProductTable.objects.get(id=product_id)
            size_id = Size.objects.get(id=size)
            new_variant = ProductVariant.objects.create(product=product, size=size_id, price=price, stock=stock,
                                                        display_image=variant_image)
            new_variant.save()

            for image in variant_images:
                variant_images = VariantImage.objects.create(product_variant=new_variant, display_image=image)
                variant_images.save()

            return render(request, 'admin_panel/view-product.html')
        sizes = Size.objects.all()
        context = {
            'sizes': sizes,
            'product_id': product_id
        }
        return render(request, 'admin_panel/add-variant.html', context)
    else:
        return redirect('admin_home')


def disable_variant(request, variant_id):
    if request.user.is_superuser:
        variant = ProductVariant.objects.get(id=variant_id)
        variant.is_active = False
        variant.save()
        return redirect('products')


def enable_variant(request, variant_id):
    if request.user.is_superuser:
        variant = ProductVariant.objects.get(id=variant_id)
        variant.is_active = True
        variant.save()
        return redirect('products')


def disable_product(request, product_id):
    if request.user.is_superuser:
        product = ProductTable.objects.get(id=product_id)
        product.is_active = False
        product.save()
        return redirect('products')


def enable_product(request, product_id):
    if request.user.is_superuser:
        product = ProductTable.objects.get(id=product_id)
        product.is_active = True
        product.save()
        return redirect('products')


def edit_category(request, category_id):
    if request.user.is_superuser:
        category = CategoryTable.objects.get(id=category_id)

        if request.method == 'POST':
            category_name = request.POST['category_name']
            image = request.FILES['image']

            category.name = category_name
            category.image = image
            category.save()

            return redirect('category')

        return render(request, 'admin_panel/edit-category.html', {'category': category})
    else:
        return redirect('admin_home')


def edit_variant(request, variant_id):
    if request.user.is_superuser:
        variant = ProductVariant.objects.get(id=variant_id)

        if request.method == 'POST':
            stock = request.POST['stock']
            size = request.POST['size']
            price = request.POST['price']
            variant_image = request.FILES['variant_image']
            variant_images = request.FILES.getlist('variant_images')

            size_id = Size.objects.get(size=size)

            variant.stock = stock
            variant.size = size_id
            variant.price = price
            variant.display_image = variant_image
            variant.save()
            if variant_images:
                VariantImage.objects.filter(product_variant=variant).delete()

                for image in variant_images:
                    variant_image = VariantImage.objects.create(product_variant=variant, display_image=image)
                    variant_image.save()

            return redirect('products')

        return render(request, 'admin_panel/edit-variant.html', {'variant': variant})


def orders(request):
    if request.user.is_superuser:
        orders = Order.objects.order_by('-id')
        context = {
            'orders': orders
        }

        return render(request, 'admin_panel/orders.html', context)


def user_order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.orderitem_set.all

    context = {
        'order': order,
        'items': order_items
    }
    return render(request, 'admin_panel/user-order-details.html', context)


def user_order_cancellation(request, order_id):
    if request.user.is_superuser:
        Order.objects.get(id=order_id).delete()

        return redirect('orders')


def change_status(request, order_id):
    if request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        if request.method == 'POST':
            status = request.POST['status']
            print('%%%%%%%%%%%%%%%',status)
            order.payment_status = str(status)
            order.save()

            return redirect('orders')

        context = {
            'order': order
        }
        return render(request, 'admin_panel/change-status.html', context)
