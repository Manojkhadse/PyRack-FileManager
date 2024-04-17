from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'created_at']

class CustomUserAdmin(BaseUserAdmin):
	fieldsets = (
		(None, {'fields': ('id', 'username', 'password', 'company', 'user_type', 'is_staff','last_login')}),
		('Permissions', {'fields': (
			'is_superuser',
			'groups', 
			'user_permissions',
		)}),
	)
	add_fieldsets = (
		(
			None,
			{
				'classes': ('wide',),
				'fields': ('username', 'company', 'user_type', 'password1', 'password2')
			}
		),
	)

	list_display = ('id', 'username', 'company', 'fk_owner', 'user_type','is_staff','last_login')
	readonly_fields = ('id',)
	list_filter = ('is_staff', 'is_superuser', 'groups')
	search_fields = ('username',)
	ordering = ('-id',)

admin.site.register(MyUser, CustomUserAdmin)


@admin.register(FileManager)
class FileManagerAdmin(admin.ModelAdmin):
	list_display = ['id', 'fk_user', 'manger_type', 'name', 'file', 'fk_folder', 'created_at']