from django.shortcuts import render, get_object_or_404
from .models import CategoryTable, ProductTable, ProductVariant, VariantImage, Size, Brands
from django.core.paginator import Paginator



# Create your views here.
def home(request):
    categories = CategoryTable.objects.all()
    print(categories)
    return render(request, 'homepage/home.html', {'categories': categories})


def shop(request, slug):
    size = Size.objects.all()
    brands  = Brands.objects.all()
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
        'size':size,
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