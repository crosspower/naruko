from rest_framework.viewsets import ViewSet
from backend.models import TenantModel
from backend.serializers.operation_log_model_serializer import OperationLogModelSerializerDetail
from backend.usecases.control_operation_log import ControlOperationLog
from rest_framework.response import Response
from backend.logger import NarukoLogging


class OperationLogModelViewSet(ViewSet):

    def list(self, request, tenant_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        tenant = TenantModel.objects.get(id=tenant_pk)
        logs = ControlOperationLog(log).fetch_logs(request.user, tenant)
        logger.info("END: list")
        return Response(data=[OperationLogModelSerializerDetail(operation_log).data for operation_log in logs])

