from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.marketplace, name='marketplace'),

    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    # cart
    path('add_to_cart/<int:food_pk>/', views.add_to_cart, name='add_to_cart'),
    path('decrease_cart/<int:food_pk>/', views.decrease_cart, name='decrease_cart'),
    path('delete_cart/<int:cart_pk>/', views.delete_cart, name='delete_cart'),






]
