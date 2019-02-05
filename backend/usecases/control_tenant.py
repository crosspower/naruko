from django.conf import settings
from backend.models import TenantModel, UserModel, RoleModel, OperationLogModel
from backend.logger import NarukoLogging
from backend.externals.ses import Ses
from backend.exceptions import InvalidRoleException


class ControlTenantUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    @staticmethod
    def target_info(tenant: TenantModel):
        return tenant.tenant_name

    def fetch_tenants(self, request_user: UserModel):
        self.logger.info("START: fetch_tenants")

        if not request_user.can_control_tenant():
            raise InvalidRoleException("request user can't create tenant. id:{}".format(request_user.id))

        response = [tenant_model for tenant_model in TenantModel.objects.all()]
        self.logger.info("END: fetch_tenants")
        return response

    @OperationLogModel.operation_log(executor_index=1, target_method=target_info, target_arg_index_list=[2])
    def create_tenant(self, request_user: UserModel, tenant: TenantModel, user: UserModel):
        self.logger.info("START: create_tenant")

        # 作成できるロールを持つか
        if not request_user.can_control_tenant():
            raise InvalidRoleException("request user can't create tenant. id:{}".format(request_user.id))

        # テナント追加
        tenant.save()

        # スケジューラーを登録する
        scheduler = UserModel(
            email=tenant.email,
            name="SCHEDULER",
            tenant=tenant,
            role=RoleModel.objects.get(id=RoleModel.SCHEDULER_ID),
        )
        scheduler.reset_password()
        scheduler.save()

        # ユーザー追加
        user.tenant = tenant
        # ランダムパスワード設定
        password = user.reset_password()
        user.save()

        # 新規登録メール送信
        self.logger.info("sending sign up email...")
        self.logger.debug("user_email: {}, user_name: {}, tenant_name: {}".format(
            user.email, user.name, tenant.tenant_name))
        ses = Ses(settings.SES_ADDRESS, settings.SES_ADDRESS)
        ses.send_signup_user(user.email, user.name, tenant.tenant_name, password)
        self.logger.info("sending sign up email... : DONE")

        self.logger.info("END: create_tenant")

        return tenant, user

    @OperationLogModel.operation_log(executor_index=1, target_method=target_info, target_arg_index_list=[2])
    def delete_tenant(self, request_user: UserModel, tenant: TenantModel):
        self.logger.info("START: delete_tenant")

        if not request_user.can_control_tenant():
            raise InvalidRoleException("request user can't create tenant. id:{}".format(request_user.id))

        tenant.delete()
        self.logger.info("END: delete_tenant")

    @OperationLogModel.operation_log(executor_index=1, target_method=target_info, target_arg_index_list=[2])
    def update_tenant(self, request_user: UserModel, tenant: TenantModel) -> TenantModel:
        self.logger.info("START: update_tenant")

        if not request_user.can_control_tenant():
            raise InvalidRoleException("request user can't create tenant. id:{}".format(request_user.id))

        tenant.save()
        self.logger.info("END: update_tenant")
        return tenant
