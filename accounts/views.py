from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from .serializers import *
from .models import *
from django.views.decorators.csrf import csrf_exempt

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not Found')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password')
        
        payload = {
            "id" : user.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat' : datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt' : token
        }
        return response
   
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)



class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Sucess'
            }
        return response
        

# Bookings Views

class ServicesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving services.
    No authentication needed (can be public).
    """
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can view services


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and managing bookings.
    Only authenticated users can create/read their bookings.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return bookings belonging to the logged-in user
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set the user automatically to the logged-in user
        serializer.save(user=self.request.user)