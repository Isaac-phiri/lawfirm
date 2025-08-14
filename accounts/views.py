# views.py - Updated with APIView classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import ContactSubmission
from .serializers import ContactSubmissionSerializer
import logging
import json


logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ContactSubmissionView(APIView):
    """
    Handle contact form submissions
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create a new contact submission"""
        try:
            serializer = ContactSubmissionSerializer(data=request.data)
            
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
        submissions = ContactSubmission.objects.all().order_by('-created_at')
        serializer = ContactSubmissionSerializer(submissions, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def send_contact_notification(self, contact):
        """Send notification email to law firm"""
        subject = f"New Contact Form Submission - {contact.get_practice_area_display()}"
        
        # Create HTML email content
        html_message = render_to_string('emails/contact_notification.html', {
            'contact': contact,
            'practice_area_display': contact.get_practice_area_display(),
            'preferred_contact_display': contact.get_preferred_contact_display(),
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
        subject = "Thank you for contacting Anderson & Associates"
        
        # Create HTML email content
        html_message = render_to_string('emails/client_confirmation.html', {
            'contact': contact,
            'practice_area_display': contact.get_practice_area_display(),
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


