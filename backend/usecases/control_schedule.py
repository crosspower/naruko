from django.core.exceptions import PermissionDenied
from backend.models import UserModel, TenantModel, AwsEnvironmentModel, Schedule, Resource, OperationLogModel,\
    ScheduleModel
from backend.models.event.event import EventRepository
from backend.logger import NarukoLogging


class ControlScheduleUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    @staticmethod
    def target_schedule_info(schedule: Schedule):
        environment = schedule.event_model.aws_environment
        return "{}_{}_{}_{}_{}_{}".format(environment.name, environment.aws_account_id, schedule.event_model.region,
                                          schedule.event_model.service, schedule.event_model.resource_id,
                                          schedule.event_model.name)

    @staticmethod
    def target_schedule_info_by_id(schedule_id: int):
        event_model = ScheduleModel.all_objects.get(id=schedule_id)
        environment = event_model.aws_environment
        return "{}_{}_{}_{}_{}_{}".format(environment.name, environment.aws_account_id, event_model.region,
                                          event_model.service, event_model.resource_id,
                                          event_model.name)

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

    @OperationLogModel.operation_log(executor_index=1, target_method=target_schedule_info, target_arg_index_list=[4])
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

    @OperationLogModel.operation_log(executor_index=1, target_method=target_schedule_info_by_id, target_arg_index_list=[4])
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
