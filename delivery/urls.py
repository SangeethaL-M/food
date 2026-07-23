from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('accept/<int:order_id>/', views.accept_delivery, name='accept_delivery'),

]
