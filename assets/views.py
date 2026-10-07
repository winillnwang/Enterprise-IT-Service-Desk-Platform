from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from django.shortcuts import render
from .models import Asset
from .permissions import AssetPermission
from .serializers import AssetSerializer


class AssetListCreateAPIView(ListCreateAPIView):
    serializer_class = AssetSerializer
    permission_classes = [
        AssetPermission,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role in [
            "it_engineer",
            "it_manager",
            "admin",
        ]:
            queryset = Asset.objects.all()
        else:
            queryset = Asset.objects.filter(
                assigned_to=user
            )

        search = self.request.query_params.get(
            "search"
        )

        status = self.request.query_params.get(
            "status"
        )

        asset_type = self.request.query_params.get(
            "asset_type"
        )

        department = self.request.query_params.get(
            "department"
        )

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        if status:
            queryset = queryset.filter(
                status=status
            )

        if asset_type:
            queryset = queryset.filter(
                asset_type=asset_type
            )

        if department:
            queryset = queryset.filter(
                department_id=department
            )

        return queryset.order_by(
            "asset_no"
        )


class AssetDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = AssetSerializer
    permission_classes = [
        AssetPermission,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role in [
            "it_engineer",
            "it_manager",
            "admin",
        ]:
            return Asset.objects.all()

        return Asset.objects.filter(assigned_to=user)


def asset_list_page(request):
    return render(
        request,
        "assets/asset_list.html",
    )


def asset_detail_page(
    request,
    pk,
):
    return render(
        request,
        "assets/asset_detail.html",
        {
            "asset_id": pk,
        },
    )


def asset_create_page(request):
    return render(
        request,
        "assets/asset_create.html",
    )
