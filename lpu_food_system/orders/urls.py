from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Student features
    path('menu/', views.menu, name='menu'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/place/', views.place_order, name='place_order'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('peak-times/', views.peak_times, name='peak_times'),

    # Admin/Staff
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/order/<int:order_id>/status/', views.update_order_status, name='update_order_status'),

    # AI API
    path('api/demand-chart/<int:item_id>/', views.demand_chart_data, name='demand_chart_data'),
]
