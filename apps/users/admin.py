from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'role', 'college', 'email', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'college']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('role', 'college')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('role', 'college')}),
    )
