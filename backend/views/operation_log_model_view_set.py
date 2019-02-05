from rest_framework.viewsets import ViewSet
from backend.models import TenantModel
from backend.serializers.operation_log_model_serializer import OperationLogModelSerializer, OperationLogModelSerializerDetail
from backend.usecases.control_operation_log import ControlOperationLog
from rest_framework.response import Response
from rest_framework import status
from backend.logger import NarukoLogging
from django.db.models import ObjectDoesNotExist


class OperationLogModelViewSet(ViewSet):

    def list(self, request, tenant_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        try:
            tenant = TenantModel.objects.get(id=tenant_pk)
            logs = ControlOperationLog(log).fetch_logs(request.user, tenant)
        except (TypeError, ValueError, ObjectDoesNotExist) as e:
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: list")
            return Response(data=[OperationLogModelSerializerDetail(operation_log).data for operation_log in logs])

