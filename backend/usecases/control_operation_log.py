from django.core.exceptions import PermissionDenied
from backend.models import UserModel, TenantModel, OperationLogModel
from backend.logger import NarukoLogging


class ControlOperationLog:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    def fetch_logs(self, request_user: UserModel, tenant: TenantModel):
        self.logger.info("START: fetch_logs")
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user can't fetch aws_environments. user_id:{} tenant_id: {}".
                                   format(request_user.id, tenant.id))

        if request_user.can_control_other_user():
            # 他のユーザーを管理できる権限ならばテナント内のログを取得
            logs = OperationLogModel.objects.filter(tenant=tenant)
        else:
            # そうでなければ自身のログを取得
            logs = OperationLogModel.objects.filter(tenant=tenant, executor=request_user)

        self.logger.info("END: fetch_logs")
        return logs
