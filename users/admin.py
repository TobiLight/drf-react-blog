from django.contrib import admin
from .models import User
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    actions = ('verify_user', 'ban_user', 'suspend_user')
    list_display = ('email', 'verified', 'username', 'created_at', 'delete')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'is_verified')
    list_per_page = 10
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    # list_editable = ('username',)
    
    def verify_user(self, modeladmin, request, queryset):
        queryset.update(is_verified=True)
    verify_user.short_description = "Mark selected users as verified"
    
    def ban_user(self, modeladmin, request, queryset):
        queryset.update(is_banned=True)
    ban_user.short_description = "Mark selected users as banned"
    
    def suspend_user(self, modeladmin, request, queryset):
        queryset.update(y)(is_suspended=True)
    suspend_user.short_description = "Mark selected users as suspended"
    
    def delete(self, obj):
        view_name = "admin:{}_{}_delete".format(obj._meta.app_label, obj._meta.model_name)
        link = reverse(view_name, args=[obj.id])
        html = '<input type="button" onclick="location.href=\'{}\'" value="Delete" />'.format(link)
        return format_html(html)
    
    def verified(self, obj):
        if obj.is_verified:
            color_code = '00FF00'
            html = '<span style="color: #{};">Yes</span>'.format(color_code, obj.email)
            return format_html(html)
            
        color_code = 'FF0000'
        html = '<span style="color: #{};">No</span>'.format(color_code, obj.email)
        return format_html(html)