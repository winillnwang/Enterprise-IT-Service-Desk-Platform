from rest_framework.permissions import BasePermission


class AssetPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # GET：
        # Employee 與 IT 都可以進入 API，
        # 實際能看到哪些資料由 queryset 控制。
        if request.method == "GET":
            return True

        # POST：
        # 只有 IT Staff 可以建立資產。
        return user.role in [
            "it_engineer",
            "it_manager",
            "admin",
        ]
