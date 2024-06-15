from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Profile, Image,TempPassword


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_name')
    inlines = [ImageInline]


class CustomUserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('pin_code', 'recovery_password', 'balance', 'freeze_balance', 'PGP_key')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(TempPassword)
