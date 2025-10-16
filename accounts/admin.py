from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from accounts.forms import UserChangeForm, UserCreationForm
from accounts.models import CustomUserModel, SocialAccountModel, EmailConfirmOtpModel, PasswordResetTokenModel, \
    PictureModel


@admin.register(CustomUserModel)
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUserModel
    search_fields = ("email", "first_name", "last_name")
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_blocked",
        "created_at",
    )
    ordering = ("created_at",)

    list_filter = (
        "role",
        "is_active",
        "is_blocked",
    )
    add_fieldsets = (
        (
            "Personal info",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                )
            }
        ),
        (
            "Set password",
            {
                "fields": (
                    "password1",
                    "password2"
                ),
            },
        )
    )

    fieldsets = (
        (
            'Status',
            {
                'fields': (
                    'role',
                    'is_active',
                    'is_blocked',
                ),
            },
        ),
        (
            'Auth method',
            {
                'fields': (
                    'regular_auth',
                    'google_auth',
                    'facebook_auth',
                ),
            },
        ),
        (
            'Permissions',
            {
                'fields': (
                    'user_permissions',
                    'groups'
                ),
            },
        ),
        (
            'Important dates',
            {
                'fields': (
                    'last_login',
                )
            }
        )
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == "admin":
            return qs.exclude(role__in=["admin", "superadmin"])
        return qs.exclude(role="superadmin")

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "user_permissions":
            if request.user.role != "superadmin":
                kwargs["queryset"] = request.user.user_permissions.all() | Permission.objects.filter(
                    group__user=request.user)
            else:
                kwargs["queryset"] = Permission.objects.all()

        if db_field.name == "groups":
            if request.user.role != "superadmin":
                kwargs["queryset"] = Group.objects.filter(user=request.user)
            else:
                kwargs["queryset"] = Group.objects.all()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        if obj.role == "user":
            obj.user_permissions.clear()
            obj.groups.clear()


@admin.register(SocialAccountModel)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "provider",
        "provider_user_id"
    )

@admin.register(EmailConfirmOtpModel)
class EmailConfirmOtpAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "code",
        "remaining_attempts",
        "remaining_resends",
        "status"
    )

@admin.register(PasswordResetTokenModel)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token",
        "created_at"
    )

@admin.register(PictureModel)
class PictureAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "portrait",
        "created_at"
    )


admin.site.site_header = "Xazna ai"
admin.site.index_title = "Features area"
