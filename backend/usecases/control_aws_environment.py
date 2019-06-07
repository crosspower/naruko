from django.core.exceptions import PermissionDenied
from backend.models import UserModel, AwsEnvironmentModel, TenantModel, OperationLogModel
from backend.logger import NarukoLogging
from backend.externals.iam import Iam
from backend.models.monitor import MonitorGraph
from backend.externals.cloudwatch import CloudWatch


class ControlAwsEnvironment:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    @staticmethod
    def target_info(aws_env: AwsEnvironmentModel):
        return "{}_{}".format(aws_env.name, aws_env.aws_account_id)

    def fetch_aws_environments(self, request_user: UserModel, tenant: TenantModel):
        self.logger.info("START: fetch_aws_environments")
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user can't fetch aws_environments. user_id:{} tenant_id: {}".
                                   format(request_user.id, tenant.id))

        if not request_user.can_control_aws():
            raise PermissionDenied("request user can't fetch aws_environments. id:{}".format(request_user.id))

        aws_environments = AwsEnvironmentModel.objects.filter(tenant_id=tenant.id)

        self.logger.info("END: fetch_aws_environments")
        return aws_environments

    @OperationLogModel.operation_log(executor_index=1, target_method=target_info, target_arg_index_list=[2])
    def save_aws_environment(self, request_user: UserModel, aws_environment: AwsEnvironmentModel):
        self.logger.info("START: save_aws_environment")
        if not request_user.is_belong_to_tenant(aws_environment.tenant):
            raise PermissionDenied("request user can't save aws_environments. user_id:{} tenant_id: {}".
                                   format(request_user.id, aws_environment.tenant.id))

        if not request_user.can_control_aws():
            raise PermissionDenied("request user can't save aws_environments. id:{}".format(request_user.id))

        # ロールの確認
        iam = Iam(aws_environment, None)
        iam.validate_role(aws_environment.aws_account_id, aws_environment.aws_role)

        # 保存
        aws_environment.save()

        # SCHEDULERにAWS環境を登録する
        scheduler = UserModel.get_scheduler(aws_environment.tenant)
        scheduler.aws_environments.add(aws_environment)
        scheduler.save()

        self.logger.info("END: save_aws_environment")
        return aws_environment

    @OperationLogModel.operation_log(executor_index=1, target_method=target_info, target_arg_index_list=[2])
    def delete_aws_environment(self, request_user: UserModel, aws_environment: AwsEnvironmentModel):
        self.logger.info("START: delete_aws_environment")
        if not request_user.is_belong_to_tenant(aws_environment.tenant):
            raise PermissionDenied("request user can't delete aws_environments. user_id:{} tenant_id: {}".
                                   format(request_user.id, aws_environment.tenant.id))

        if not request_user.can_control_aws():
            raise PermissionDenied("request user can't delete aws_environments. id:{}".format(request_user.id))

        # 削除
        aws_environment.delete()
        self.logger.info("END: delete_aws_environment")

    def billing_graph(self, request_user: UserModel, aws: AwsEnvironmentModel, monitor_graph: MonitorGraph):
        self.logger.info("START: graph")

        # 使用できるAWSアカウントか
        if not request_user.has_aws_env(aws):
            raise PermissionDenied("request user can't use aws account. user_id: {}, aws_id: {}"
                                   .format(request_user.id, aws.id))
        
        # 請求情報を取得する権限を持っているか
        if not request_user.can_fetch_billing():
            raise PermissionDenied("request user can't fetch aws_environments. id:{}".format(request_user.id))

        # APIの引数を充足
        monitor_graph.service_name = 'AWS/Billing'
        monitor_graph.dimensions.append(
            dict(
                Name='Currency',
                Value='USD'
            ))
        monitor_graph = CloudWatch(aws, 'us-east-1').get_chart(monitor_graph)

        self.logger.info("END: graph")
        return monitor_graph
