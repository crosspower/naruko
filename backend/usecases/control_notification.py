from django.core.exceptions import PermissionDenied
from backend.models import TenantModel, NotificationDestinationModel, UserModel, NotificationGroupModel, OperationLogModel
from backend.exceptions import InvalidNotificationException
from backend.logger import NarukoLogging
from backend.externals.sns import Sns


class ControlNotificationUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    @staticmethod
    def target_dest_info(dest: NotificationDestinationModel):
        return dest.name

    @staticmethod
    def target_group_info(group: NotificationGroupModel):
        return group.name

    @staticmethod
    def target_notify_info(message: NotificationDestinationModel.NotificationMessage):
        return "{}_{}_{}_{}_{}_{}_{}".format(message.aws.name, message.aws.aws_account_id, message.resource.region,
                                             message.resource.get_service_name(), message.resource.resource_id,
                                             message.metric, message.level)

    def fetch_destinations(self, request_user: UserModel, tenant: TenantModel):
        self.logger.info("START: fetch_destinations")
        if not request_user.can_control_notification():
            raise PermissionDenied

        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user doesn't belong to tenant. user_id:{}, tenant_id: {}"
                                   .format(request_user.id, tenant.id))

        destinations = NotificationDestinationModel.all().filter(tenant=tenant)
        self.logger.info("END: fetch_destinations")
        return destinations

    @OperationLogModel.operation_log(executor_index=1, target_method=target_dest_info, target_arg_index_list=[2])
    def create_destination(self, request_user: UserModel, destination: NotificationDestinationModel):
        self.logger.info("START: create_destination")
        if not request_user.can_control_notification():
            raise PermissionDenied

        if not request_user.is_belong_to_tenant(destination.tenant):
            raise PermissionDenied("request user doesn't belong to tenant. user_id:{}, tenant_id: {}"
                                   .format(request_user.id, destination.tenant.id))
        # 保存
        destination.save()

        self.logger.info("END: create_destination")
        return destination

    @OperationLogModel.operation_log(executor_index=1, target_method=target_dest_info, target_arg_index_list=[2])
    def delete_destination(self, request_user: UserModel, destination: NotificationDestinationModel):
        self.logger.info("START: delete_destination")
        if not request_user.can_control_notification():
            raise PermissionDenied

        if not request_user.is_belong_to_tenant(destination.tenant):
            raise PermissionDenied("request user doesn't belong to tenant. user_id:{}, tenant_id: {}"
                                   .format(request_user.id, destination.tenant.id))

        # 削除
        destination.delete()

        self.logger.info("END: delete_destination")

    def fetch_groups(self, request_user: UserModel, tenant: TenantModel):
        self.logger.info("START: fetch_groups")
        if not request_user.can_control_notification():
            raise PermissionDenied

        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user doesn't belong to tenant. user_id:{}, tenant_id: {}"
                                   .format(request_user.id, tenant.id))

        destinations = NotificationGroupModel.objects.filter(tenant=tenant)

        self.logger.info("END: fetch_groups")
        return destinations

    @OperationLogModel.operation_log(executor_index=1, target_method=target_group_info, target_arg_index_list=[2])
    def save_group(self, request_user: UserModel, group: NotificationGroupModel):
        self.logger.info("START: save_group")
        if not request_user.can_control_notification():
            raise PermissionDenied

        if not request_user.is_belong_to_tenant(group.tenant):
            raise PermissionDenied("request user doesn't belong to tenant. user_id:{}, tenant_id: {}"
                                   .format(request_user.id, group.tenant.id))

        # 作成
        group.save()

        self.logger.info("END: save_group")
        return group

    @OperationLogModel.operation_log(executor_index=1, target_method=target_group_info, target_arg_index_list=[2])
    def delete_group(self, request_user: UserModel, group: NotificationGroupModel):
        self.logger.info("START: delete_group")
        if not request_user.can_control_notification():
            raise PermissionDenied

        if not request_user.is_belong_to_tenant(group.tenant):
            raise PermissionDenied("request user doesn't belong to tenant. user_id:{}, tenant_id: {}"
                                   .format(request_user.id, group.tenant.id))

        # 作成
        group.delete()

        self.logger.info("END: delete_group")

    def confirm_subscription(self, confirmation_data: dict):
        self.logger.info("START: confirm_subscription")

        token = confirmation_data["Token"]
        arn = confirmation_data["TopicArn"]

        self.logger.info("Confirm SNS Arn: {}".format(arn))

        sns = Sns(arn=arn)
        sns.confirm_subscription(token)
        self.logger.info("END: confirm_subscription")

    def verify_sns_notification(self, notification_data: dict):
        self.logger.info("START: verify_sns_notification")

        verify = Sns.verify_notification(notification_data)

        self.logger.info("Verify Result: {}".format(verify))
        if not verify:
            raise InvalidNotificationException(notification_data)

        self.logger.info("END: verify_sns_notification")

    def notify(self, message: NotificationDestinationModel.NotificationMessage):
        self.logger.info("START: notify")

        # AWSアカウント->通知グループ->通知先
        self.logger.info("Start Notification. Aws_env: {}".format(message.aws.id))
        for group in message.aws.notification_groups.filter(deleted=0):
            self.logger.info("Start Notification Group: {}".format(group.id))
            for dest in group.destinations.filter(deleted=0):
                self.logger.info("Start Notification Destination: {}".format(dest.id))
                result_message = dest.notify(message)
                self.logger.info("End Notification Destination: {} Msg: {}".format(dest.id, result_message))
            self.logger.info("End Notification Group: {}".format(group.id))

        self.logger.info("END: notify")
