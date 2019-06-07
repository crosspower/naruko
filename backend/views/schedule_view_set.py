from rest_framework.viewsets import ViewSet
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from backend.usecases.control_schedule import ControlScheduleUseCase
from backend.models import AwsEnvironmentModel, TenantModel, Resource
from backend.models.event.event import ScheduleFactory
from backend.logger import NarukoLogging


class ScheduleViewSet(ViewSet):

    def list(self, request, tenant_pk=None, aws_env_pk=None,
             region_pk=None, service_pk=None, resource_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        tenant = TenantModel.objects.get(id=tenant_pk)
        aws_env = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant=tenant)
        resource = Resource.get_service_resource(region_pk, service_pk, resource_pk)
        schedules = ControlScheduleUseCase(log).fetch_schedules(request.user, tenant, aws_env, resource)
        logger.info("END: list")
        return Response(data=[schedule.serialize() for schedule in schedules], status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, tenant_pk=None, aws_env_pk=None,
               region_pk=None, service_pk=None, resource_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        tenant = TenantModel.objects.get(id=tenant_pk)
        aws_env = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant=tenant)
        schedule = ScheduleFactory.create(
            resource_id=resource_pk,
            service=service_pk,
            region=region_pk,
            aws_id=aws_env_pk,
            **request.data)
        create_schedule = ControlScheduleUseCase(log).save_schedule(request.user, tenant, aws_env, schedule)
        logger.info("END: create")
        return Response(data=create_schedule.serialize(), status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, tenant_pk=None, aws_env_pk=None,
               region_pk=None, service_pk=None, resource_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: update")
        tenant = TenantModel.objects.get(id=tenant_pk)
        aws_env = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant=tenant)
        schedule = ScheduleFactory.create(
            resource_id=resource_pk,
            service=service_pk,
            region=region_pk,
            aws_id=aws_env_pk,
            event_id=pk,
            **request.data)
        create_schedule = ControlScheduleUseCase(log).save_schedule(request.user, tenant, aws_env, schedule)
        logger.info("END: update")
        return Response(data=create_schedule.serialize(), status=status.HTTP_201_CREATED)

    @transaction.atomic
    def delete(self, request, tenant_pk=None, aws_env_pk=None,
               region_pk=None, service_pk=None, resource_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: delete")
        tenant = TenantModel.objects.get(id=tenant_pk)
        aws_env = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant=tenant)
        ControlScheduleUseCase(log).delete_schedule(request.user, tenant, aws_env, pk)
        logger.info("END: delete")
        return Response(status=status.HTTP_204_NO_CONTENT)
