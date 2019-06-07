from rest_framework.viewsets import ViewSet
from backend.usecases.control_notification import ControlNotificationUseCase
from backend.serializers.notification_destination_serializer import serialize_destinations_detail, get_serializer,\
    serialize_destination
from backend.models import TenantModel, NotificationDestinationModel
from rest_framework.response import Response
from rest_framework import status
from backend.logger import NarukoLogging
from django.db import transaction


class NotificationDestinationViewSet(ViewSet):

    def list(self, request, tenant_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        tenant = TenantModel.objects.get(id=tenant_pk)
        destinations = ControlNotificationUseCase(log).fetch_destinations(request.user, tenant)
        data = serialize_destinations_detail(destinations)
        logger.info("END: list")
        return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, tenant_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        # バリデーション
        data_dest = request.data
        data_dest["tenant"] = tenant_pk
        dest_serializer = get_serializer(data_dest)
        dest_serializer.is_valid(raise_exception=True)

        # 作成
        destination = ControlNotificationUseCase(log).create_destination(request.user, dest_serializer.save())
        data = serialize_destination(destination)
        logger.info("END: create")
        return Response(data=data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, tenant_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        destination = NotificationDestinationModel.get(pk, tenant_pk)
        ControlNotificationUseCase(log).delete_destination(request.user, destination)
        return Response(status=status.HTTP_204_NO_CONTENT)
