from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'username', 'type', 'is_active', 'avatar')
    list_filter = ('type', 'is_active')
    search_fields = ('email', 'username')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('type', 'company', 'position', 'avatar')}),
    )