from django.contrib import admin

from .models import Ticket, TicketCategory


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )

    list_filter = ("is_active",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "priority",
        "status",
        "reporter",
        "assignee",
        "created_at",
    )

    list_filter = (
        "priority",
        "status",
        "category",
    )

    search_fields = (
        "title",
        "description",
        "reporter__username",
        "assignee__username",
    )
