from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.utils import timezone
from django.core.validators import EmailValidator



class ContactSubmission(models.Model):
    PRACTICE_AREA_CHOICES = [
        ('criminal-defense', 'Criminal Defense'),
        ('family-law', 'Family Law'),
        ('personal-injury', 'Personal Injury'),
        ('corporate-law', 'Corporate Law'),
        ('immigration', 'Immigration'),
        ('real-estate', 'Real Estate'),
        ('wills-estates', 'Wills & Estates'),
        ('other', 'Other'),
    ]
    
    PREFERRED_CONTACT_CHOICES = [
        ('phone', 'Phone Call'),
        ('email', 'Email'),
        ('text', 'Text Message'),
        ('any', 'Any Method'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True, null=True)
    practice_area = models.CharField(max_length=50, choices=PRACTICE_AREA_CHOICES)
    preferred_contact = models.CharField(max_length=20, choices=PREFERRED_CONTACT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_responded = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
    
    def __str__(self):
        return f"{self.name} - {self.get_practice_area_display()}"