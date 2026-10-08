from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import CartItem, Category, Order, Product, UserProfile, Invoice
import uuid
import json


def _filter_products(request):
    category_name = request.GET.get('category')
    query = request.GET.get('q', '')

    products = Product.objects.all()

    if category_name:
        products = products.filter(category__name=category_name)

    if query:
        products = products.filter(name__icontains=query)

    # Attach user cart quantity to each product for interactive buttons
    session_key = request.session.session_key
    for product in products:
        if request.user.is_authenticated:
            item = CartItem.objects.filter(user=request.user, product=product).first()
        elif session_key:
            item = CartItem.objects.filter(session_key=session_key, user=None, product=product).first()
        else:
            item = None
        product.user_cart_qty = item.quantity if item else 0

    return products, Category.objects.all()


def home(request):
    products, categories = _filter_products(request)
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    products, categories = _filter_products(request)
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/product_list.html', context)


def cart_view(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    elif session_key:
        cart_items = CartItem.objects.filter(session_key=session_key, user=None)
    else:
        cart_items = []
    
    total_price = sum(item.total_price() for item in cart_items) if cart_items else 0
    final_total = total_price + 5 if total_price > 0 else 5
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'final_total': final_total,
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request, product_id):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    else:
        cart_item, created = CartItem.objects.get_or_create(session_key=session_key, user=None, product=product)

    # If it was just created, quantity is already 1. 
    # Only increment if it already existed in the cart to prevent double-counting!
    if created:
        cart_item.quantity = 1
    else:
        cart_item.quantity += 1
    
    cart_item.save()
    new_qty = cart_item.quantity

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'qty': new_qty})
    
    next_url = request.GET.get('next', 'home')
    return redirect(next_url)


def decrease_cart(request, product_id):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(user=request.user, product=product).first()
    else:
        cart_item = CartItem.objects.filter(session_key=session_key, user=None, product=product).first()

    new_qty = 0
    if cart_item:
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            new_qty = 0
        else:
            cart_item.save()
            new_qty = cart_item.quantity

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'qty': new_qty})
    
    next_url = request.GET.get('next', 'home')
    return redirect(next_url)


def checkout_view(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        session_key = request.session.session_key
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        elif session_key:
            cart_items = CartItem.objects.filter(session_key=session_key, user=None)
        else:
            cart_items = []
        
        item_total = sum(item.total_price() for item in cart_items)
        delivery_fee = 15 if 0 < item_total < 199 else 0
        handling_fee = 4 if item_total > 0 else 0
        grand_total = item_total + delivery_fee + handling_fee
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_price=grand_total,
            address=address,
            status='Order Placed'
        )
        
        Invoice.objects.create(
            order=order,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            item_total=item_total,
            delivery_fee=delivery_fee,
            handling_fee=handling_fee,
            grand_total=grand_total
        )
        
        cart_items.delete()
        return redirect('track_order', order_id=order.id)
        
    return render(request, 'store/checkout.html')


def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/track_order.html', {'order': order})


def delivery_login(request):
    return render(request, 'store/delivery_login.html')


@login_required(login_url='delivery_login')
def delivery_dashboard(request):
    available_orders = Order.objects.filter(
        status__in=['Order Placed', 'Packing']
    )
    my_deliveries = Order.objects.filter(delivery_partner=request.user).exclude(
        status='Delivered'
    )

    return render(
        request,
        'store/delivery_dashboard.html',
        {'available_orders': available_orders, 'my_deliveries': my_deliveries},
    )


@login_required(login_url='delivery_login')
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delivery_partner = request.user
    order.status = 'Out for Delivery'
    order.save()
    return redirect('delivery_dashboard')


@login_required(login_url='delivery_login')
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, delivery_partner=request.user)
    order.status = 'Delivered'
    order.save()
    return redirect('delivery_dashboard')


def delivery_logout(request):
    logout(request)
    return redirect('delivery_login')


def user_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if phone:
            username = f"user_{phone}"
            user, created = User.objects.get_or_create(
                username=username, 
                defaults={'first_name': 'QuickBite User'}
            )
            login(request, user)
            UserProfile.objects.get_or_create(
                user=user, 
                defaults={'phone': phone, 'name': 'QuickBite User'}
            )
            request.session['user_phone'] = phone
            return redirect('profile')
            
    return render(request, 'store/profile.html')


def user_logout(request):
    logout(request)
    return redirect('home')


def profile_view(request):
    if not request.user.is_authenticated:
        return render(request, 'store/profile.html')

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        request.user.first_name = request.POST.get('name', request.user.first_name)
        request.user.save()
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.save()
        return redirect('profile')

    return render(
        request, 'store/profile.html', {'profile': profile, 'orders': orders}
    )


def update_profile_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if data.get('logout'):
                logout(request)
                if 'user_phone' in request.session:
                    del request.session['user_phone']
                return JsonResponse({'status': 'success'})

            phone = data.get('phone')
            name = data.get('name', 'QuickBite User')
            
            if phone:
                username = f"user_{phone}"
                user, created = User.objects.get_or_create(
                    username=username, 
                    defaults={'first_name': name}
                )
                
                if not created:
                    user.first_name = name
                    user.save()
                
                login(request, user)
                
                profile, _ = UserProfile.objects.update_or_create(
                    user=user,
                    defaults={'phone': phone, 'name': name}
                )
                request.session['user_phone'] = phone
                
                return JsonResponse({'status': 'success', 'name': profile.name, 'phone': profile.phone})
                
            return JsonResponse({'status': 'error', 'message': 'Phone required'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)