from django.contrib import admin

from .models import (
    Ticket,
    TicketCategory,
    TicketHistory,
)


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

@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "ticket",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "created_at",
    )

    list_filter = (
        "field_name",
        "created_at",
    )

    search_fields = (
        "ticket__ticket_no",
        "changed_by__username",
        "old_value",
        "new_value",
    )

    readonly_fields = (
        "ticket",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "created_at",
    )
