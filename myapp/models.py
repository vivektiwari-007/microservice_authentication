from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


user_type_choice = (
    ('admin','admin'),
    ('manager','manager'),
    ('employee','employee'),
)


class CustomUser(AbstractUser, PermissionsMixin):
    user_type = models.CharField(choices=user_type_choice, max_length=128, default="admin")
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(max_length=128, unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    mail_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs): 
        self.username = self.email
        return super().save(*args, **kwargs)


class UserToken(models.Model):
    user = models.ForeignKey(CustomUser, related_name="user", on_delete=models.CASCADE)
    token = models.CharField(null=True, max_length=500)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return str(self.user)


otp_type_choice = (
    ('email','email'),
    ('sms','sms'),
    ('passwordreset','passwordreset'),
)

class OTP(models.Model):
    otp = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    otp_type = models.CharField(choices=otp_type_choice, max_length=128, default="email")
    otp_check = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
