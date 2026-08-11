from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from quotations.models import CustomUser, Bill

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('display_name', 'phone_primary', 'phone_secondary', 'profile_picture', 'profile_picture_url')}),
    )
    list_display = ('username', 'email', 'display_name', 'phone_primary', 'is_staff')

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'client_name', 'client_phone', 'project_title', 'grand_total', 'bill_date', 'user')
    search_fields = ('bill_number', 'client_name', 'client_phone', 'project_title')
    list_filter = ('bill_date', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
