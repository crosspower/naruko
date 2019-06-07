from rest_framework.viewsets import ViewSet
from backend.models import TenantModel, RoleModel
from backend.serializers.tenant_model_serializer import TenantModelDetailSerializer, TenantModelSerializer
from backend.serializers.user_model_serializer import UserModelSerializer, UserModelDetailSerializer
from backend.usecases.control_tenant import ControlTenantUseCase
from rest_framework.response import Response
from backend.logger import NarukoLogging
from rest_framework import status
from django.db import transaction


class TenantModelViewSet(ViewSet):
    queryset = TenantModel.objects.all()
    serializer_class = TenantModelDetailSerializer

    def list(self, request):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        tenants = ControlTenantUseCase(log).fetch_tenants(request.user)
        logger.info("END: list")
        return Response(data={"tenants": [TenantModelDetailSerializer(tenant).data for tenant in tenants]})

    @transaction.atomic
    def create(self, request):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        # バリデーション：Company
        tenant_serializer = TenantModelSerializer(data=request.data["tenant"])
        tenant_serializer.is_valid(raise_exception=True)
        tenant_serializer_save = tenant_serializer.save()

        # バリデーション：User
        data_user = request.data["user"]
        data_user["tenant"] = tenant_serializer_save.id
        data_user["role"] = RoleModel.ADMIN_ID
        user_serializer = UserModelSerializer(data=data_user)
        user_serializer.is_valid(raise_exception=True)
        user_serializer_save = user_serializer.save()

        # 作成
        tenant, user = ControlTenantUseCase(log).create_tenant(
            request.user,
            tenant_serializer_save,
            user_serializer_save
        )
        logger.info("END: create")
        return Response(
            data={
                "tenant": TenantModelDetailSerializer(tenant).data,
                "user": UserModelDetailSerializer(user).data
            },
            status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: destroy")
        tenant = TenantModel.objects.get(id=int(pk))
        ControlTenantUseCase(log).delete_tenant(request.user, tenant)
        logger.info("END: destroy")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def update(self, request, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: update")
        # バリデーション
        target_tenant = TenantModel.objects.get(pk=pk)
        serializer = TenantModelSerializer(instance=target_tenant, data=request.data)
        serializer.is_valid(raise_exception=True)

        # 更新
        tenant = ControlTenantUseCase(log).update_tenant(request.user, serializer.save())
        data = TenantModelSerializer(tenant).data
        logger.info("END: update")
        return Response(data=data, status=status.HTTP_200_OK)