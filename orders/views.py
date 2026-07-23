import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from restaurants.models import FoodItem
from accounts.models import UserProfile
from .models import Cart, Order, OrderItem, Payment

@login_required
def add_to_cart(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, food_item=food_item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added {food_item.name} to cart!")
    return redirect('restaurant_detail', restaurant_id=food_item.restaurant.id)

@login_required
def increase_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

@login_required
def decrease_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.total_price() for item in cart_items)
    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('view_cart')

from .models import Coupon  # Ensure Coupon is imported

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Your cart is empty!")
        return redirect('home')

    raw_total = sum(item.total_price() for item in cart_items)
    discount = 0
    applied_coupon = request.session.get('coupon_code', None)

    if applied_coupon:
        try:
            coupon_obj = Coupon.objects.get(code=applied_coupon, active=True)
            discount = (raw_total * coupon_obj.discount_percentage) / 100
        except Coupon.DoesNotExist:
            request.session['coupon_code'] = None

    total_amount = raw_total - discount
    restaurant = cart_items.first().food_item.restaurant
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Apply Coupon action
        if 'apply_coupon' in request.POST:
            code = request.POST.get('coupon_code', '').strip()
            try:
                coupon = Coupon.objects.get(code__iexact=code, active=True)
                request.session['coupon_code'] = coupon.code
                messages.success(request, f"Coupon '{coupon.code}' applied! ({coupon.discount_percentage}% OFF)")
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid or expired coupon code.")
            return redirect('checkout')

        # Place Order action
        payment_method = request.POST.get('payment_method', 'COD')
        delivery_address = request.POST.get('address', profile.address or 'Standard Address')

        order = Order.objects.create(
            user=request.user,
            restaurant=restaurant,
            total_amount=total_amount,
            delivery_address=delivery_address,
            status='Pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                food_item=item.food_item,
                quantity=item.quantity,
                price=item.food_item.price
            )

        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            is_paid=(payment_method in ['Wallet', 'MobiKwik', 'RazorPay'])
        )

        # Clear cart and coupon
        cart_items.delete()
        if 'coupon_code' in request.session:
            del request.session['coupon_code']

        messages.success(request, f"Order #{order.id} placed successfully with {payment_method}!")
        return redirect('order_detail', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'raw_total': raw_total,
        'discount': discount,
        'total_amount': total_amount,
        'applied_coupon': applied_coupon,
        'user_address': profile.address or 'Standard Address',
        'wallet_balance': profile.wallet_balance,
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_dummy_key'),
        'razorpay_amount': int(total_amount * 100),
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})