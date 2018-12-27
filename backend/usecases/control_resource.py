from django.core.exceptions import PermissionDenied
from backend.models import AwsEnvironmentModel, UserModel, Resource
from backend.externals.cloudwatch import CloudWatch
from backend.externals.resource_group_tagging import ResourceGroupTagging
from backend.logger import NarukoLogging


class ControlResourceUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    def fetch_resources(self, request_user: UserModel, aws_environment: AwsEnvironmentModel, region: str) -> list:
        self.logger.info("START: fetch resources")
        if not request_user.is_belong_to_tenant(aws_environment.tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, aws_environment.tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        tagging = ResourceGroupTagging(aws_environment=aws_environment, region=region)
        self.logger.info("ResourceGroupTagging Client Created.")

        resources = []

        resources_status = None
        for get_resources in tagging.get_resources(Resource.get_all_services()):
            self.logger.info("got resource tags")
            if resources_status is None and get_resources:
                resources_status = CloudWatch(aws_environment=aws_environment, region=region).get_resources_status()
                self.logger.info("got cloudwatch alarms")
            for get_resource in get_resources:
                self.logger.info("resource tag convert response")
                # アラームがなければ未設定とする
                get_resource.status = resources_status[get_resource.get_service_name()].\
                    get(get_resource.resource_id, "UNSET")
                resources.append(get_resource)

        self.logger.info("END: fetch resources")
        return resources

    def start_resource(self, request_user: UserModel, aws_environment: AwsEnvironmentModel, resource: Resource):
        self.logger.info("START: start_resource")
        tenant = aws_environment.tenant
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        resource.start(aws_environment)
        self.logger.info("END: start_resource")

    def reboot_resource(self, request_user: UserModel, aws_environment: AwsEnvironmentModel, resource: Resource):
        self.logger.info("START: reboot_resource")
        tenant = aws_environment.tenant
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        resource.reboot(aws_environment)
        self.logger.info("END: reboot_resource")

    def stop_resource(self, request_user: UserModel, aws_environment: AwsEnvironmentModel, resource: Resource):
        self.logger.info("START: stop_resource")
        tenant = aws_environment.tenant
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        resource.stop(aws_environment)
        self.logger.info("END: stop_resource")

    def describe_resource(self, request_user: UserModel, aws_environment: AwsEnvironmentModel, resource: Resource):
        self.logger.info("START: describe_resource")
        tenant = aws_environment.tenant
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        resource_describe = resource.describe(aws_environment)
        self.logger.info("END: describe_resource")

        return resource_describe

    def fetch_backups(self, request_user: UserModel, aws_environment: AwsEnvironmentModel, resource: Resource):
        self.logger.info("START: fetch_backups")
        tenant = aws_environment.tenant
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        backups = resource.fetch_backups(aws_environment)

        self.logger.info("END: fetch_backups")
        return backups

    def create_backup(self, request_user: UserModel, aws_environment: AwsEnvironmentModel, resource: Resource,
                      no_reboot: bool):
        self.logger.info("START: create_backup")
        tenant = aws_environment.tenant
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        backup_id = resource.create_backup(aws_environment, no_reboot=no_reboot)
        self.logger.info("END: create_backup")
        return backup_id
