from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail_view, name='restaurant_detail'),
    path('owner/dashboard/', views.owner_dashboard_view, name='restaurant_dashboard'),  # <-- Updated name here!
    path('owner/order/<int:order_id>/update/', views.update_order_status_view, name='update_order_status'),
]