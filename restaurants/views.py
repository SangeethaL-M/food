from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Restaurant, FoodItem, Category
from orders.models import Order


def home_view(request):
    restaurants = Restaurant.objects.all()
    categories = Category.objects.all()
    query = request.GET.get('q')
    category_filter = request.GET.get('category')

    # Handle search query
    if query:
        restaurants = restaurants.filter(name__icontains=query)

    # Handle homepage category filtering
    if category_filter:
        if category_filter.isdigit():
            # If the category param is an ID (e.g. ?category=1)
            restaurants = restaurants.filter(food_items__category_id=category_filter).distinct()
        else:
            # If the category param is a name (e.g. ?category=biriyani)
            restaurants = restaurants.filter(food_items__category__name__iexact=category_filter).distinct()

    return render(request, 'restaurants/home.html', {
        'restaurants': restaurants,
        'categories': categories,
        'selected_category': int(category_filter) if category_filter and category_filter.isdigit() else category_filter,
    })


def restaurant_detail_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Start with all available food items for this restaurant
    food_items = restaurant.food_items.filter(is_available=True)
    categories = Category.objects.all()

    # Read ?category= from the URL (e.g. /restaurant/1/?category=2)
    category_id = request.GET.get('category')

    # Apply filter ONLY if category_id exists and is not empty
    if category_id:
        food_items = food_items.filter(category_id=category_id)

    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'food_items': food_items,
        'categories': categories,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
    })


@login_required
def owner_dashboard_view(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at') if restaurant else []

    return render(request, 'restaurants/dashboard.html', {
        'restaurant': restaurant,
        'orders': orders,
    })


@login_required
def update_order_status_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}!")
    return redirect('restaurant_dashboard')  # <--- Changed from 'owner_dashboard'