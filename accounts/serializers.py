from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name', 'email','phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['id', 'name', 'price']  # id for easy frontend referencing

    def validate_price(self, value):
        """
        Ensure price is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    service = ServicesSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Services.objects.all(), 
        source='service', 
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'service',      # for reading
            'service_id',   # for writing
            'name',
            'email',
            'time',
            'date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        service = attrs.get('service')
        date = attrs.get('date')
        time = attrs.get('time')

        if user and Booking.objects.filter(user=user, service=service, date=date, time=time).exists():
            raise serializers.ValidationError(
                "You have already booked this service at the selected date and time."
            )
        return attrs