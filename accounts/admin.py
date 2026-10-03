from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Department, User


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Service Desk",
            {
                "fields": (
                    "department",
                    "role",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Service Desk",
            {
                "fields": (
                    "department",
                    "role",
                )
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "department",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "department",
        "is_staff",
        "is_active",
    )
