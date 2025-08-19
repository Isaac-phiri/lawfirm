from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

class User(AbstractUser):
    email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email



class Services(models.Model):
    name = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=3)

    def __str__(self):
        return f"{self.name}, {self.price}"
    


HOURS = (
    ('09:00', '09:00'),
    ('10:00', '10:00'),
    ('11:00', '11:00'),
    ('12:00', '12:00'),
    ('13:00', '13:00'),
    ('14:00', '14:00'),
    ('15:00', '15:00'),
    ('16:00', '16:00'),
    ('17:00', '17:00'),
    ('18:00', '18:00'),
    ('19:00', '19:00'),
)


class Booking(models.Model):
    user =      models.ForeignKey(User, verbose_name="Client", on_delete=models.CASCADE)
    service =   models.ForeignKey(Services, null=True, on_delete=models.SET_NULL)
    name =      models.CharField(max_length=200, verbose_name="Client Name")
    email =     models.EmailField(blank=True, null=True)
    time =      models.CharField(max_length=50, choices=HOURS, default="09:00")
    date =      models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date', 'time', 'service')

    def __str__(self):
        return self.name

class Contact(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_responded = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
    
    def __str__(self):
        return f"{self.name}"