from rest_framework.viewsets import ViewSet
from django.db.models import ObjectDoesNotExist
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
        try:
            tenant = TenantModel.objects.get(id=tenant_pk)
            destinations = ControlNotificationUseCase(log).fetch_destinations(request.user, tenant)
            data = serialize_destinations_detail(destinations)
        except (TypeError, ValueError, TenantModel.DoesNotExist) as e:
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: list")
            return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, tenant_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        try:
            with transaction.atomic():
                # バリデーション
                data_dest = request.data
                data_dest["tenant"] = tenant_pk
                dest_serializer = get_serializer(data_dest)
                dest_serializer.is_valid(raise_exception=True)

                # 作成
                destination = ControlNotificationUseCase(log).create_destination(request.user, dest_serializer.save())
                data = serialize_destination(destination)
        except (TypeError, ValueError, TenantModel.DoesNotExist) as e:
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: create")
            return Response(data=data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, tenant_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        try:
            with transaction.atomic():
                destination = NotificationDestinationModel.get(pk, tenant_pk)
                ControlNotificationUseCase(log).delete_destination(request.user, destination)
        except (TypeError, ValueError, ObjectDoesNotExist) as e:
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: create")
            return Response(status=status.HTTP_204_NO_CONTENT)
