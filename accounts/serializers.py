from rest_framework import serializers
from .models import *
    
class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'name', 'email', 'phone', 'practice_area', 
            'preferred_contact', 'message', 'created_at', 'is_responded'
        ]
        read_only_fields = ['id', 'created_at', 'is_responded']
    
    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Please enter a valid email address.")
        return value.lower()
    
    def validate_message(self, value):
        """Validate message length"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide more details about your legal matter.")
        return value.strip()
