from django.shortcuts import render, get_object_or_404, redirect
from .models import CategoryTable, ProductTable, ProductVariant, VariantImage, Size, Brands, UserAddress, State
from django.core.paginator import Paginator


# Create your views here.
def home(request):
    categories = CategoryTable.objects.all()
    print(categories)
    return render(request, 'homepage/home.html', {'categories': categories})


def shop(request, slug):
    size = Size.objects.all()
    brands = Brands.objects.all()
    categories = CategoryTable.objects.all()
    category_id = CategoryTable.objects.get(slug=slug)
    products = ProductTable.objects.filter(category=category_id)
    variants = []
    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        variants.append(variant)

    # Instantiate the Paginator object
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
