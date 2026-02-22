from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
import json
import datetime

from .models import (
    FoodStall, FoodItem, Order, OrderItem,
    BreakTimeSlot, StudentProfile, DemandRecord
)
from .forms import StudentRegistrationForm, OrderForm, CartItemForm
from .ai_predictor import DemandPredictor, get_weekly_demand_chart_data


# ─── Home Page ────────────────────────────────────────────────────────────────

def home(request):
    """Landing page"""
    stalls = FoodStall.objects.filter(is_open=True)
    return render(request, 'orders/home.html', {'stalls': stalls})


# ─── Authentication ───────────────────────────────────────────────────────────

def register(request):
    """Student registration"""
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to LPU Food System, {user.first_name}! 🎉')
            return redirect('menu')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = StudentRegistrationForm()

    return render(request, 'orders/register.html', {'form': form})


def login_view(request):
    """Student login"""
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}! 👋')
            return redirect(request.GET.get('next', 'menu'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'orders/login.html', {'form': form})


def logout_view(request):
    """Logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── Menu & Ordering ──────────────────────────────────────────────────────────

@login_required
def menu(request):
    """Browse all food stalls and their menu items"""
    stalls = FoodStall.objects.filter(is_open=True).prefetch_related('menu_items')
    category_filter = request.GET.get('category', '')
    stall_filter = request.GET.get('stall', '')

    items = FoodItem.objects.filter(is_available=True)
    if category_filter:
        items = items.filter(category=category_filter)
    if stall_filter:
        items = items.filter(stall__id=stall_filter)

    # Get cart from session
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0

    context = {
        'stalls': stalls,
        'items': items,
        'category_filter': category_filter,
        'stall_filter': stall_filter,
        'cart_count': cart_count,
        'categories': FoodItem.CATEGORY_CHOICES,
    }
    return render(request, 'orders/menu.html', context)


@login_required
def add_to_cart(request, item_id):
    """Add a food item to session cart"""
    if request.method == 'POST':
        food_item = get_object_or_404(FoodItem, id=item_id, is_available=True)
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})
        stall_id = request.session.get('cart_stall_id')

        # Ensure all items are from the same stall
        if stall_id and stall_id != food_item.stall.id:
            messages.warning(request, '⚠️ You can only order from one stall at a time. Clear your cart first.')
            return redirect('menu')

        cart[str(item_id)] = cart.get(str(item_id), 0) + quantity
        request.session['cart'] = cart
        request.session['cart_stall_id'] = food_item.stall.id
        messages.success(request, f'✅ {food_item.name} added to cart!')

    return redirect('menu')


@login_required
def cart(request):
    """View and manage cart"""
    cart_data = request.session.get('cart', {})
    cart_items = []
    total = 0

    for item_id, quantity in cart_data.items():
        try:
            food_item = FoodItem.objects.get(id=int(item_id))
            subtotal = food_item.price * quantity
            total += subtotal
            cart_items.append({
                'food_item': food_item,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except FoodItem.DoesNotExist:
            pass

    time_slots = BreakTimeSlot.objects.all()

    context = {
        'cart_items': cart_items,
        'total': total,
        'time_slots': time_slots,
        'order_form': OrderForm(),
    }
    return render(request, 'orders/cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        if not cart:
            request.session.pop('cart_stall_id', None)
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def place_order(request):
    """Place the final order from cart"""
    if request.method != 'POST':
        return redirect('cart')

    cart_data = request.session.get('cart', {})
    if not cart_data:
        messages.warning(request, 'Your cart is empty!')
        return redirect('menu')

    form = OrderForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please select a valid time slot.')
        return redirect('cart')

    time_slot = form.cleaned_data['time_slot']

    # Check slot availability
    if not time_slot.is_available():
        messages.error(request, f'⚠️ Sorry, {time_slot} is fully booked. Please choose another slot.')
        return redirect('cart')

    stall_id = request.session.get('cart_stall_id')
    stall = get_object_or_404(FoodStall, id=stall_id)

    # Create the Order
    order = Order.objects.create(
        student=request.user,
        stall=stall,
        time_slot=time_slot,
        special_instructions=form.cleaned_data.get('special_instructions', ''),
    )

    # Add OrderItems
    for item_id, quantity in cart_data.items():
        food_item = get_object_or_404(FoodItem, id=int(item_id))
        OrderItem.objects.create(
            order=order,
            food_item=food_item,
            quantity=quantity,
            price_at_order=food_item.price,
        )

    order.calculate_total()

    # Clear cart from session
    request.session.pop('cart', None)
    request.session.pop('cart_stall_id', None)

    messages.success(request, f'🎉 Order #{order.id} placed successfully! Pick up at {time_slot}.')
    return redirect('order_confirmation', order_id=order.id)


@login_required
def order_confirmation(request, order_id):
    """Show order confirmation page"""
    order = get_object_or_404(Order, id=order_id, student=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    """Student's order history"""
    orders = Order.objects.filter(student=request.user).order_by('-order_time')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    """Cancel a pending order"""
    order = get_object_or_404(Order, id=order_id, student=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.id} has been cancelled.')
    else:
        messages.warning(request, 'Only pending orders can be cancelled.')
    return redirect('my_orders')


# ─── Admin / Stall Owner Dashboard ────────────────────────────────────────────

@login_required
def dashboard(request):
    """Admin/stall owner dashboard with AI predictions"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')

    today = datetime.date.today()

    # Today's orders
    todays_orders = Order.objects.filter(order_date=today).order_by('-order_time')

    # Stats
    total_orders_today = todays_orders.count()
    revenue_today = todays_orders.filter(
        status__in=['confirmed', 'preparing', 'ready', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Peak slot analysis
    slot_demand = BreakTimeSlot.objects.annotate(
        order_count=Count('orders', filter=__import__('django.db.models', fromlist=['Q']).Q(
            orders__order_date=today
        ))
    )

    # AI Predictions for top food items
    top_items = FoodItem.objects.filter(is_available=True)[:5]
    ai_predictions = []

    for item in top_items:
        predictor = DemandPredictor()
        records = DemandRecord.objects.filter(food_item=item)
        predictor.train(records)
        predicted = predictor.predict(today.weekday(), 2)  # predict for lunch slot
        ai_predictions.append({
            'item': item,
            'predicted_demand': predicted,
        })

    context = {
        'todays_orders': todays_orders,
        'total_orders_today': total_orders_today,
        'revenue_today': revenue_today,
        'slot_demand': slot_demand,
        'ai_predictions': ai_predictions,
        'today': today,
    }
    return render(request, 'orders/dashboard.html', context)


@login_required
def update_order_status(request, order_id):
    """AJAX endpoint to update order status"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        return JsonResponse({'success': True, 'status': order.get_status_display()})

    return JsonResponse({'error': 'Invalid status'}, status=400)


# ─── AI Chart Data API ────────────────────────────────────────────────────────

@login_required
def demand_chart_data(request, item_id):
    """Returns Chart.js data for demand prediction of a food item"""
    food_item = get_object_or_404(FoodItem, id=item_id)
    chart_data = get_weekly_demand_chart_data(food_item)
    return JsonResponse(chart_data)


@login_required
def peak_times(request):
    """Shows peak ordering times with AI predictions"""
    today = datetime.date.today()
    slots = BreakTimeSlot.objects.all()

    predictor = DemandPredictor()

    slot_info = []
    for slot in slots:
        predicted = predictor.predict(today.weekday(), slot.id)
        current = slot.current_orders()
        slot_info.append({
            'slot': slot,
            'current_orders': current,
            'predicted': predicted,
            'percentage': min(100, int((current / slot.max_capacity) * 100)),
            'is_peak': predicted > 35 or current > 30,
        })

    return render(request, 'orders/peak_times.html', {
        'slot_info': slot_info,
        'today': today,
    })
