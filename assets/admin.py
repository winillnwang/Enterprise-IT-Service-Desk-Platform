from django.contrib import admin

from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "asset_no",
        "name",
        "asset_type",
        "status",
        "assigned_to",
        "department",
        "warranty_end",
    )

    list_filter = (
        "asset_type",
        "status",
        "department",
    )

    search_fields = (
        "asset_no",
        "name",
        "serial_number",
        "assigned_to__username",
    )

    ordering = ("asset_no",)
