from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from backend.usecases.control_resource import ControlResourceUseCase
from backend.models.aws_environment import AwsEnvironmentModel
from backend.models.resource.resource import Resource
from backend.models.resource.command import Command, Document, Parameter
from backend.logger import NarukoLogging


class ResourceViewSet(ViewSet):

    def list(self, request, tenant_pk=None, aws_env_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        region = request.GET.get("region")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resources = ControlResourceUseCase(log).fetch_resources(
            request.user,
            aws_environment,
            region
        )
        logger.info("END: list")
        return Response(data=[resource.serialize(aws_environment) for resource in resources],
                        status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def start(self, request, tenant_pk=None, aws_env_pk=None,
              region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: start")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, pk)
        ControlResourceUseCase(log).start_resource(request.user, aws_environment, resource)
        logger.info("END: start")
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def reboot(self, request, tenant_pk=None, aws_env_pk=None,
               region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: reboot")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, pk)
        ControlResourceUseCase(log).reboot_resource(request.user, aws_environment, resource)
        logger.info("END: reboot")
        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def stop(self, request, tenant_pk=None, aws_env_pk=None,
             region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: stop")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, pk)
        ControlResourceUseCase(log).stop_resource(request.user, aws_environment, resource)
        logger.info("END: stop")
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, tenant_pk=None, aws_env_pk=None,
                 region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: retrieve")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = ControlResourceUseCase(log).describe_resource(
            request.user,
            aws_environment,
            Resource.get_service_resource(region_pk, service_pk, pk))
        logger.info("END: retrieve")
        return Response(data=resource.serialize(aws_environment),
                        status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def run_command(self, request, tenant_pk=None, aws_env_pk=None,
                    region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: run_command")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, pk)
        command = Command(
            Document(
                request.data["name"],
                [Parameter(**param) for param in request.data["parameters"]]),
            resource)
        command = ControlResourceUseCase(log).run_command(request.user, aws_environment, command)
        logger.info("END: run_command")
        return Response(status=status.HTTP_200_OK, data=command.serialize())


class RegionViewSet(ViewSet):
    pass


class ServiceViewSet(ViewSet):
    pass

