from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/decrease/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_api, name='update_profile_api'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('delivery/login/', views.delivery_login, name='delivery_login'),
    path('delivery/logout/', views.delivery_logout, name='delivery_logout'),
    path(
        'delivery/dashboard/',
        views.delivery_dashboard,
        name='delivery_dashboard',
    ),
    path(
        'delivery/accept/<int:order_id>/',
        views.accept_order,
        name='accept_order',
    ),
    path(
        'delivery/complete/<int:order_id>/',
        views.complete_order,
        name='complete_order',
    ),
]