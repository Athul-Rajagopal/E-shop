from datetime import timedelta, datetime

from _decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import *
from orders.models import *
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from cart.models import Coupon


# Create your views here.
def admin_login(request):
    if request.user.is_superuser and request.user.is_authenticated:
        return redirect('admin_home')
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
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if not start_date and not end_date:
            # Calculate the current date
            current_date = timezone.now().date()

            # Calculate the date 30 days back from the current date
            default_start_date = current_date - timedelta(days=30)
            default_end_date = current_date

            # Convert to string format (YYYY-MM-DD)
            start_date = default_start_date.strftime('%Y-%m-%d')
            end_date = default_end_date.strftime('%Y-%m-%d')

        if start_date and end_date:
            order_count_date = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__time__isnull=True)
            ).exclude(payment_status='CANCELLED').count()

            total_price_date = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__time__isnull=True)
            ).exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            daily_totals = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__time__isnull=True)
            ).exclude(payment_status='CANCELLED').annotate(date=TruncDate('order_date')).values('date').annotate(
                total=Sum('total_price')).order_by('date')
            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']
            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)
            recent_orders = Order.objects.order_by('-order_date')[:3]
            top_selling_products = OrderItem.objects.values('product__product__name').annotate(
                total_quantity=Count('product')
            ).order_by('-total_quantity')[:5]

            categories = CategoryTable.objects.all()
            data = []

            for category in categories:
                product_count = ProductTable.objects.filter(category=category).count()
                data.append(product_count)

            context = {
                'order_count_date': order_count_date,
                'total_price_date': total_price_date,
                'start_date': start_date,
                'end_date': end_date,
                'daily_totals': daily_totals,
                'order_count': order_count,
                'total_price': total_price,
                'categories': categories,
                'data': data,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,

            }

            return render(request, 'admin_panel/adminHome.html', context)

        else:
            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)

            categories = CategoryTable.objects.all()
            data = []

            for category in categories:
                product_count = ProductTable.objects.filter(category=category).count()
                data.append(product_count)

            recent_orders = Order.objects.order_by('-order_date')[:5]
            top_selling_products = OrderItem.objects.values('product__product__name').annotate(
                total_quantity=Count('product')).order_by('-total_quantity')[:5]

            context = {
                'order_count': order_count,
                'total_price': total_price,
                'start_date': start_date,
                'end_date': end_date,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'categories': categories,
                'data': data,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,
            }

            return render(request, 'admin_panel/adminHome.html', context)

    return HttpResponseBadRequest("Invalid request method.")


def download_sales_report(request):
    today = datetime.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's totals
    today_orders = Order.objects.filter(order_date__date=today)
    order_count_today = today_orders.count()
    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Weekly totals
    week_orders = Order.objects.filter(order_date__date__range=[week_ago, today])
    order_count_week = week_orders.count()
    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Monthly totals
    month_orders = Order.objects.filter(order_date__date__range=[month_ago, today])
    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Top-selling products
    top_selling_products_today = OrderItem.objects.values('product__product__name').annotate(
        total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_week = OrderItem.objects.filter(order_id__order_date__date__range=[week_ago, today]).values(
        'product__product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_month = OrderItem.objects.filter(order_id__order_date__date__range=[month_ago, today]).values(
        'product__product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    context = {
        'order_count_today': order_count_today,
        'total_price_today': total_price_today,
        'order_count_week': order_count_week,
        'total_price_week': total_price_week,
        'order_count_month': order_count_month,
        'total_price_month': total_price_month,
        'top_selling_products_today': top_selling_products_today,
        'top_selling_products_week': top_selling_products_week,
        'top_selling_products_month': top_selling_products_month,
    }

    # Render the HTML content using the 'sales.html' template and the provided context
    html_content = render_to_string('admin_panel/sales-report.html', context)

    # Set the response content type as 'application/pdf' to indicate that it's a PDF file
    response = HttpResponse(content_type='application/pdf')

    # Set the filename for the downloaded file
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Generate the PDF content from the HTML using xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), response)

    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


def user_details(request):
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
            discount_percent = request.POST['discount']
            if int(discount_percent) < 0:
                messages.error(request, 'enter a valid discount')
                return redirect('add_product')
            # variant side
            size = request.POST['size']
            price = request.POST['price']

            stock = request.POST['stock']
            variant_image = request.FILES.get['variant_image']
            variant_images = request.FILES.getlist('variant_images')

            category_id = CategoryTable.objects.get(id=category)
            brand_id = Brands.objects.get(id=brand)
            size_id = Size.objects.get(id=size)

            product = ProductTable.objects.create(name=product_name, description=description, category=category_id,
                                                  brandName=brand_id, discount_percent=discount_percent)
            product.save()
            product_variant = ProductVariant.objects.create(product=product, size=size_id, price=price, stock=stock,
                                                            display_image=variant_image)
            product_variant.save()

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
            discount_percent = request.POST['discount']

            category_id = CategoryTable.objects.get(name=category)
            brand_id = Brands.objects.get(name=brand)

            product.name = product_name
            product.category = category_id
            product.brandName = brand_id
            product.description = description
            product.discount_percent = discount_percent

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
            variant_image = request.FILES.get('variant_image')
            variant_images = request.FILES.getlist('variant_images')

            size_id = Size.objects.get(size=size)

            variant.stock += int(stock)
            variant.size = size_id
            variant.price = price
            if variant_image:
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
            order.payment_status = str(status)
            order.save()

            return redirect('orders')

        context = {
            'order': order
        }
        return render(request, 'admin_panel/change-status.html', context)


def user_order_invoice(request, order_id):
    if request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        order_items = order.orderitem_set.all

        context = {
            'order': order,
            'items': order_items
        }
        return render(request, 'admin_panel/user-order-invoice.html', context)


def download_user_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items = order.orderitem_set.all()

    # Render the PDF template with CSS styles
    template = 'admin_panel/user-order-invoice.html'
    context = {'order': order, 'items': items}
    html = render_to_string(template, context)

    # Create a PDF document using xhtml2pdf
    pdf_file = BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)

    # Set the response with the PDF content as an attachment
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_invoice.pdf"'
    return response


def add_coupon(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            coupon_code = request.POST['coupon_code']
            discount_price = request.POST['discount_price']
            expiry_date = request.POST['expiry_date']
            minimum_amount = request.POST['minimum_amount']
            if int(minimum_amount) <= int(discount_price):
                messages.error(request, 'enter a valid amount')
                return redirect('add_coupon')

            coupon = Coupon.objects.create(coupon_code=coupon_code, discount_price=discount_price,
                                           expiry_date=expiry_date, minimum_amount=minimum_amount)
            coupon.save()

            return redirect('coupons')

        return render(request, 'admin_panel/add-coupon.html')


def list_coupon(request):
    if request.user.is_superuser:
        coupons = Coupon.objects.all()
        context = {
            'coupons': coupons
        }
        return render(request, 'admin_panel/coupons.html', context)


def edit_coupon(request, coupon_id):
    if request.user.is_superuser:
        coupon = Coupon.objects.get(id=coupon_id)
        if request.method == 'POST':
            coupon_code = request.POST['coupon_code']
            discount_price = request.POST['discount_price']
            expiry_date = request.POST['expiry_date']
            minimum_amount = request.POST['minimum_amount']
            if int(minimum_amount) <= int(discount_price):
                messages.error(request, 'enter a valid amount')
                return redirect('coupons')

            coupon = Coupon.objects.get(id=coupon_id)
            coupon.coupon_code = coupon_code
            coupon.discount_price = discount_price
            coupon.expiry_date = expiry_date
            coupon.minimum_amount = minimum_amount
            coupon.save()

            return redirect('coupons')

        return render(request, 'admin_panel/edit-coupon.html', {'coupon': coupon})


def user_order_returned(request, order_id):
    if request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        user = order.user
        try:
            get_wallet = UserWallet.objects.get(user=user)
            get_wallet.wallet_amount = get_wallet.wallet_amount + Decimal(str(order.total_price))
            get_wallet.save()
            order.delete()
        except ObjectDoesNotExist:
            user_wallet = UserWallet.objects.create(user=user, wallet_amount=order.total_price)
            user_wallet.save()

        return redirect('orders')

    return render(request, 'admin_panel/orders.html')


def add_brand(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            brand_name = request.POST['brand']
            new_brand = Brands.objects.create(name=brand_name)
            new_brand.save()
            return redirect('brands')


def brands(request):
    if request.user.is_superuser:
        brand_list = Brands.objects.all()
        return render(request, 'admin_panel/brands.html', {'brands': brand_list})
