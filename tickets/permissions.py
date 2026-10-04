from rest_framework.permissions import BasePermission


class IsTicketOwnerOrITStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role in ["it_engineer", "it_manager", "admin"]:
            return True

        return obj.reporter == user
