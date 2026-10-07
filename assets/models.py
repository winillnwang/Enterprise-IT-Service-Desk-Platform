from django.conf import settings
from django.db import models

from accounts.models import Department


class Asset(models.Model):
    class AssetType(models.TextChoices):
        LAPTOP = "laptop", "筆記型電腦"
        DESKTOP = "desktop", "桌上型電腦"
        MONITOR = "monitor", "螢幕"
        PHONE = "phone", "手機"
        PRINTER = "printer", "印表機"
        NETWORK = "network", "網路設備"
        OTHER = "other", "其他"

    class Status(models.TextChoices):
        AVAILABLE = "available", "可用"
        IN_USE = "in_use", "使用中"
        MAINTENANCE = "maintenance", "維修中"
        RETIRED = "retired", "已報廢"

    asset_no = models.CharField(
        max_length=30,
        unique=True,
    )

    name = models.CharField(
        max_length=150,
    )

    asset_type = models.CharField(
        max_length=20,
        choices=AssetType.choices,
    )

    serial_number = models.CharField(
        max_length=100,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_assets",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )

    purchase_date = models.DateField(
        null=True,
        blank=True,
    )

    warranty_end = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.asset_no} - {self.name}"
