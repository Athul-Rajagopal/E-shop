from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.core.paginator import Paginator
from django.contrib.auth.models import User


# Create your views here.
def home(request):
    categories = CategoryTable.objects.all()
    return render(request, 'homepage/home.html', {'categories': categories})


def shop(request, slug):
    size = Size.objects.all()
    brands = Brands.objects.all()
    categories = CategoryTable.objects.all()
    category_id = CategoryTable.objects.get(slug=slug)
    products = ProductTable.objects.filter(category=category_id)

    variants = []

    # filters
    size_filter = request.GET.getlist('size')
    brand_filter = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    print(size_filter)
    print(brand_filter)
    print(min_price, max_price)

    if brand_filter:
        products = products.filter(brandName__name__in=brand_filter)

    if min_price and max_price and size_filter:
        variants = ProductVariant.objects.filter(product__in=products, size__size__in=size_filter, price__gte=min_price,
                                                 price__lte=max_price)

    elif min_price and max_price:
        variants = ProductVariant.objects.filter(price__gte=min_price, price__lte=max_price)

    elif size_filter:
        variants = ProductVariant.objects.filter(product__in=products, size__size__in=size_filter)

    else:
        variants = [ProductVariant.objects.filter(product=product).first() for product in products]

    # Instantiate the Paginator object
    paginator = Paginator(variants, 12)  # Show 9 variants per page

    # Get the current page number from the request
    page_number = request.GET.get('page')

    # Get the Page object for the requested page
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'products': products,
        'variants': variants,
        'size': size,
        'brands': brands,
        'page_obj': page_obj,
    }
    return render(request, 'homepage/shop.html', context)


def product_detail(request, slug):
    categories = CategoryTable.objects.all()
    variant = ProductVariant.objects.get(slug=slug)
    product = get_object_or_404(ProductTable, slug=variant.product.slug)
    images = VariantImage.objects.filter(product_variant=variant)
    variants = product.productvariant_set.all()

    context = {
        'categories': categories,
        'product': product,
        'variants': variant,
        'images': images,
        'size': variants
    }
    return render(request, 'homepage/product_detail.html', context)


# user profile
def user_profile_home(request):
    if request.user.is_authenticated:
        user_details = UserAddress.objects.filter(user_id=request.user).first()
        context = {
            'details': user_details
        }
        return render(request, 'homepage/user-profile.html', context)
    return render(request, 'homepage/user-profile.html')


def user_address(request):
    if request.user.is_authenticated:
        user_details = UserAddress.objects.filter(user_id=request.user)
        context = {
            'details': user_details
        }
        return render(request, 'homepage/user-address.html', context)
    return render(request, 'homepage/user-address.html')


def add_user_address(request):
    states = State.objects.all()
    if request.user.is_authenticated:
        if request.method == 'POST':
            first_name = request.POST['firstname']
            last_name = request.POST['lastname']
            phone = request.POST['phone']
            area = request.POST['area']
            state = request.POST['state']
            pincode = request.POST['pincode']
            house = request.POST['house']

            state_id = State.objects.get(id=state)
            new_address = UserAddress.objects.create(user_id=request.user,
                                                     first_name=first_name,
                                                     last_name=last_name,
                                                     area=area,
                                                     phone=phone,
                                                     pincode=pincode,
                                                     house_name=house,
                                                     state=state_id)
            new_address.save()

            return redirect('user_address')

    return render(request, 'homepage/add-user-address.html', {'states': states})


def edit_address(request, address_id):
    address = UserAddress.objects.get(id=address_id)
    state = State.objects.all()

    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        phone = request.POST['phone']
        area = request.POST['area']
        state = request.POST['state']
        pincode = request.POST['pincode']
        house = request.POST['house']
        state_id = State.objects.get(state=state)

        address.first_name = first_name
        address.last_name = last_name
        address.area = area
        address.house_name = house
        address.phone = phone
        address.pincode = pincode
        address.state = state_id
        address.save()

        return redirect('user_address')

    context = {'address': address,
               'states': state
               }

    return render(request, 'homepage/edit-address.html', context)


def delete_address(request, address_id):
    if request.user.is_authenticated:
        UserAddress.objects.get(id=address_id).delete()
        return redirect('user_address')


# change password
def change_user_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            old_password = request.POST.get('password')
            new_password = request.POST.get('password1')
            confirm_new_password = request.POST.get('password2')
            user = request.user

            if user.check_password(old_password) and new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully')
                return redirect('signin')

            else:
                messages.error(request, 'Password does not match or invalid input')

        return render(request, 'homepage/change-password.html')

    else:
        return redirect('signin')


def search_product(request):
    if request.method == 'POST':
        item_name = request.POST['item_name']
        print(item_name, type(item_name))
        products = ProductTable.objects.filter(name__icontains=item_name)
        variants = []

        for product in products:
            variant = ProductVariant.objects.filter(product=product).first()
            variants.append(variant)

        size = Size.objects.all()
        brands = Brands.objects.all()
        categories = CategoryTable.objects.all()

        paginator = Paginator(variants, 9)  # Show 9 variants per page

        # Get the current page number from the request
        page_number = request.GET.get('page')

        # Get the Page object for the requested page
        page_obj = paginator.get_page(page_number)

        context = {
            'categories': categories,
            'products': products,
            'variants': variants,
            'size': size,
            'brands': brands,
            'page_obj': page_obj,
        }

        return render(request, 'homepage/search-product.html', context)

    return redirect('home')


def user_wallet(request):
    wallet,_ = UserWallet.objects.get_or_create(user=request.user)
    context = {
        'wallet': wallet
    }
    return render(request, 'homepage/user-wallet.html', context)
