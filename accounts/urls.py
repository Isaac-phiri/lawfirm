from django.urls import path
from .views import *

urlpatterns = [
   path('contact/', ContactSubmissionView.as_view(), name='contact_submission'),
]
