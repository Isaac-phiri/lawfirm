from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('user/', UserView.as_view(), name="user"),
    path('logout/', LogoutView.as_view(), name="logout"),

    path('services/', ServicesViewSet.as_view({'get': 'list'})),
    path('service/<int:pk>/', ServicesViewSet.as_view({'get': 'retrieve'})),

    path('bookings/', BookingViewSet.as_view({'get': 'list','post': 'create',})),
    path('booking/<int:pk>/', BookingViewSet.as_view({'get': 'retrieve','put': 'update','patch': 'partial_update','delete': 'destroy'})),



]
