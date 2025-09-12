from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from accounts.forms import UserChangeForm, UserCreationForm
from accounts.models import CustomUserModel, SocialAccountModel, EmailConfirmOtpModel, PasswordResetTokenModel, UserPictureModel


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUserModel
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('pk',)
    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_blocked',
        'created_at',
    )
    list_filter = (
        'role',
        'is_active',
        'is_blocked',
    )
    add_fieldsets = (
        (
            _('Personal info'),
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                )
            }
        ),
        (
            _('Set password'),
            {
                'fields': (
                    'password1',
                    'password2'
                ),
            },
        ),
    )
    fieldsets = (
        (
            _('Personal info'),
            {'fields': (
                'email',
                'first_name',
                'last_name',
            )
            }
        ),
        (
            _('Status'),
            {
                'fields': (
                    'role',
                    'is_active',
                    'is_blocked',
                ),
            },
        ),
        (
            _('Auth method'),
            {
                'fields': (
                    'regular_auth',
                    'google_auth',
                    'facebook_auth',
                ),
            },
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'user_permissions',
                    'groups'
                ),
            },
        ),
        (
            _('Important dates'),
            {
                'fields': (
                    'last_login',
                )
            }
        )
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.exclude(role='superadmin')

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "user_permissions":
            if not request.user.is_superuser:
                kwargs["queryset"] = request.user.user_permissions.all() | Permission.objects.filter(
                    group__user=request.user)
            else:
                kwargs["queryset"] = Permission.objects.all()

        if db_field.name == "groups":
            if not request.user.is_superuser:
                kwargs["queryset"] = Group.objects.filter(user=request.user)
            else:
                kwargs["queryset"] = Group.objects.all()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        if obj.role == 'user':
            obj.user_permissions.clear()
            obj.groups.clear()


class SocialAccountAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'provider',
        'provider_user_id'
    )


class EmailConfirmOtpAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'code',
        'remaining_attempts',
        'remaining_resends',
        'status'
    )

class PasswordResetAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'token',
        'created_at'
    )

class UserPictureAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'portrait',
        'created_at'
    )

admin.site.register(CustomUserModel, CustomUserAdmin)
admin.site.register(SocialAccountModel, SocialAccountAdmin)
admin.site.register(UserPictureModel, UserPictureAdmin)
admin.site.register(EmailConfirmOtpModel, EmailConfirmOtpAdmin)
admin.site.register(PasswordResetTokenModel, PasswordResetAdmin)
admin.site.site_header = 'My project'
admin.site.index_title = 'Features area'
