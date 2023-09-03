from django.contrib import admin
from myapp.models import CustomUser, OTP, UserToken
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff','mail_verified')
    # Customize other admin settings as needed

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP)
admin.site.register(UserToken)