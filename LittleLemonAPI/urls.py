from django.urls import path 
from . import views 
from rest_framework.authtoken.views import obtain_auth_token
  
urlpatterns = [ 
    path('menu-items', views.menu_items, name='menu-items'), 
    path('api-token-auth/', obtain_auth_token),
    path('menu-items/<int:menuItem>', views.menu_item, name='menu-item'),
    path('groups/manager/users', views.managers_group_view, name='managers-group'),
    path('groups/manager/users/<int:userId>', views.manager_view, name='managers-view'),
    path('groups/delivery-crew/users', views.delivery_crew_view, name='delivery-crew-view'),
    path('cart/menu-items', views.cart_management_view, name='cart-management-view'),
] 