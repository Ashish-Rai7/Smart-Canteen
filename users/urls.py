from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('menu/', views.menu, name='menu'),
    path('payment/', views.payment, name='payment'),
    path('cart/', views.cart, name='cart'),
    path('logout/', views.logout, name='logout'),
    path('place_order/', views.place_order , name='place_order'),
    path('track_order',views.track_order, name='track_order'),
     # --- Cart URLs ---
    # path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<str:item_id>/', views.update_cart, name='update_cart'), # Use str for item_id if using dict keys
    path('remove_from_cart/<str:item_id>/', views.remove_from_cart, name='remove_from_cart') # Use str for item_id if using dict keys
]
