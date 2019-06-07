from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from backend.usecases.control_resource import ControlResourceUseCase
from backend.models.aws_environment import AwsEnvironmentModel
from backend.models.resource.resource import Resource
from backend.models.resource.ec2 import Ec2
from backend.logger import NarukoLogging


class BackupViewSet(ViewSet):

    def list(self, request, tenant_pk=None, aws_env_pk=None,
             region_pk=None, service_pk=None, resource_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, resource_pk)
        backups = ControlResourceUseCase(log).fetch_backups(request.user, aws_environment, resource)
        logger.info("END: list")
        return Response(data=[backup.serialize() for backup in backups], status=status.HTTP_200_OK)

    def create(self, request, tenant_pk=None, aws_env_pk=None,
               region_pk=None, service_pk=None, resource_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, resource_pk)
        no_reboot = request.data["no_reboot"] if isinstance(resource, Ec2) else None
        backup_id = ControlResourceUseCase(log).create_backup(request.user, aws_environment, resource, no_reboot)
        logger.info("END: create")
        return Response(data={"backup_id": backup_id}, status=status.HTTP_201_CREATED)
