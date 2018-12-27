from django.core.exceptions import PermissionDenied
from backend.models import UserModel, TenantModel, AwsEnvironmentModel, Schedule, Resource
from backend.models.event.event import EventRepository
from backend.logger import NarukoLogging


class ControlScheduleUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    def fetch_schedules(self, request_user: UserModel, tenant: TenantModel, aws_environment: AwsEnvironmentModel,
                        resource: Resource):
        self.logger.info("START: fetch_schedules")
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        schedules = EventRepository.fetch_schedules_by_resource(resource, aws_environment)

        self.logger.info("END: fetch_schedules")
        return schedules

    def save_schedule(self, request_user: UserModel, tenant: TenantModel, aws_environment: AwsEnvironmentModel,
                      schedule: Schedule):
        self.logger.info("START: save_schedule")
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        save_schedule = EventRepository.save(schedule)

        self.logger.info("END: save_schedule")
        return save_schedule

    def delete_schedule(self, request_user: UserModel, tenant: TenantModel, aws_environment: AwsEnvironmentModel,
                        event_id: int):
        self.logger.info("START: delete")
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user is not belong to tenant. user_id:{} tenant_id:{}"
                                   .format(request_user.id, tenant.id))

        if not request_user.has_aws_env(aws_environment):
            raise PermissionDenied("request user doesn't have aws environments. id:{}".format(request_user.id))

        EventRepository.delete(event_id)

        self.logger.info("END: delete")
