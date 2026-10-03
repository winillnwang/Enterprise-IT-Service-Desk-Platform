from django.utils import timezone

from django.conf import settings
from django.db import models


class TicketCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    ticket_no = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.PROTECT,
        related_name="tickets",
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_tickets",
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new and not self.ticket_no:
            year = timezone.now().year
            self.ticket_no = f"INC-{year}-{self.pk:06d}"

            super().save(
                update_fields=["ticket_no"]
            )

    def __str__(self):
        return f"{self.ticket_no} - {self.title}"
