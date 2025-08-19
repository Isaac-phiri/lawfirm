from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from .serializers import *
from .models import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework import permissions, status
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .auth import JWTAuthentication
import jwt
import datetime
from django.core.mail import send_mail
import logging
from django.template.loader import render_to_string
from django.utils.html import strip_tags


logger = logging.getLogger(__name__)

class RegisterView(APIView):
    authentication_classes = []  # No authentication for registration
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    authentication_classes = []  # No authentication for login
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.check_password(password):
            return Response({'error': 'Incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        
        response = Response()
        response.set_cookie(
            key='jwt', 
            value=token, 
            httponly=True, 
            secure=settings.DEBUG,  # Use secure cookies in production
            samesite='Lax'
        )
        response.data = {
            'message': 'Login successful',
            'user': UserSerializer(user).data
        }
        return response

class CSRFView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({'csrfToken': get_token(request)})

class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logout successful'
        }
        return response
    

@method_decorator(csrf_exempt, name='dispatch')
class ContactView(APIView):
    """
    Handle contact form submissions
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create a new contact submission"""
        try:
            serializer = ContactSerializer(data=request.data)
            
            if serializer.is_valid():
                # Save the contact submission
                contact = serializer.save()
                print(contact)
                
                # Send notification email to law firm
                try:
                    self.send_contact_notification(contact)
                except Exception as e:
                    logger.error(f"Failed to send notification email: {str(e)}")
                    # Don't fail the API call if email fails
                
                # Send confirmation email to client
                try:
                    self.send_client_confirmation(contact)
                except Exception as e:
                    logger.error(f"Failed to send confirmation email: {str(e)}")
                    # Don't fail the API call if email fails
                
                return Response({
                    'success': True,
                    'message': 'Thank you for your message. We will contact you within 24 hours.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Please check your input and try again.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Contact submission error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while processing your request. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """List all contact submissions (for admin use)"""
        submissions = Contact.objects.all().order_by('-created_at')
        serializer = ContactSerializer(submissions, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def send_contact_notification(self, contact):
        """Send notification email to law firm"""
        subject = f"KGMLP Website"
        
        # Create HTML email content
        html_message = render_to_string('emails/contact_notification.html', {
            'contact': contact,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.CONTACT_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
    
    def send_client_confirmation(self, contact):
        """Send confirmation email to client"""
        subject = "Thank you for contacting KGM Legal practitioners"
        
        # Create HTML email content
        html_message = render_to_string('emails/client_confirmation.html', {
            'contact': contact,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[contact.email],
            html_message=html_message,
            fail_silently=False,
        )




# Bookings Views

class ServicesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving services.
    No authentication needed (can be public).
    """
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can view services


class BookingViewSet(APIView):
    """
    API view for listing and creating bookings.
    Only authenticated users can create/read their bookings.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get all bookings for the logged-in user
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save booking with the current user
            booking = serializer.save(user=request.user)
            
            # Send confirmation emails
            self.send_confirmation_emails(booking, request)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_confirmation_emails(self, booking, request):
        """
        Send confirmation emails to client and admin
        """
        # Email to client
        self.send_client_confirmation(booking, request)
        
        # Email to admin/office
        self.send_admin_notification(booking, request)

    def send_client_confirmation(self, booking, request):
        """Send confirmation email to the client"""
        subject = f"Booking Confirmation - {booking.service.name}"
        
        # Create HTML email content
        html_message = render_to_string('emails/booking_confirmation.html', {
            'booking': booking,
            'user': booking.user,
            'service': booking.service,
            'site_url': request.get_host(),
        })
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send client confirmation email: {e}")

    def send_admin_notification(self, booking, request):
        """Send notification email to admin/office"""
        subject = f"New Booking Received - {booking.service.name}"
        
        # Create HTML email content
        html_message = render_to_string('emails/admin_booking_notification.html', {
            'booking': booking,
            'user': booking.user,
            'service': booking.service,
            'site_url': request.get_host(),
        })
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],  # Add your admin email in settings
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send admin notification email: {e}")
