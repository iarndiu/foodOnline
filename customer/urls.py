from django.urls import path, include
from . import views
from accounts import views as AccountViews


urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.c_profile, name='c_profile'),
    path('my_orders/', views.my_orders, name='c_my_orders'),
    path('order_detail/<int:order_no>/', views.order_detail, name='c_order_detail'),



]
