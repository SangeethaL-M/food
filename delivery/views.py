from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order

@login_required
def delivery_dashboard(request):
    # Get 'Preparing' orders EXCLUDING ones this specific user already declined
    available_orders = Order.objects.filter(status='Preparing').exclude(declined_by=request.user).order_by('-created_at')
    
    # Active deliveries for this user
    my_deliveries = Order.objects.filter(status='Out for Delivery').order_by('-created_at')

    return render(request, 'delivery/dashboard.html', {
        'available_orders': available_orders,
        'my_deliveries': my_deliveries,
    })

@login_required
def accept_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            order.status = 'Out for Delivery'
            order.save()
            messages.success(request, f"Order #{order.id} accepted! It is now Out for Delivery.")
            
        elif action == 'reject':
            # Add current user to declined_by list so it disappears for them!
            order.declined_by.add(request.user)
            messages.info(request, f"You declined Order #{order.id}. It is now hidden for you.")
            
        elif action == 'delivered':
            order.status = 'Delivered'
            order.save()
            messages.success(request, f"Order #{order.id} marked as Delivered!")

    return redirect('delivery_dashboard')