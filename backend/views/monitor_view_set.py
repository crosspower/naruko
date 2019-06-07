from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from backend.usecases.control_monitor import ControlMonitorUseCase
from backend.models import AwsEnvironmentModel, Monitor, Resource
from backend.logger import NarukoLogging
from backend.models.monitor import MonitorGraph


class MonitorViewSet(ViewSet):

    def list(self, request, tenant_pk=None, aws_env_pk=None,
             region_pk=None, service_pk=None, resource_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        aws = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, resource_pk)
        monitors = ControlMonitorUseCase(log).fetch_monitors(request.user, aws, resource)
        logger.info("END: list")
        return Response(data=[monitor.serialize() for monitor in monitors], status=status.HTTP_200_OK)

    def create(self, request, tenant_pk=None, aws_env_pk=None,
               region_pk=None, service_pk=None, resource_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, resource_pk)
        resource.monitors.append(Monitor(**request.data))
        resource = ControlMonitorUseCase(log).save_monitor(request.user, resource, aws_environment)
        logger.info("END: create")
        return Response(data=resource.monitors[0].serialize(), status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def graph(self, request, tenant_pk=None, aws_env_pk=None,
              region_pk=None, service_pk=None, resource_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: graph")
        aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
        resource = Resource.get_service_resource(region_pk, service_pk, resource_pk)
        monitor_graph = MonitorGraph(metric_name=pk, **request.data)
        monitor_graph = ControlMonitorUseCase(log).graph(request.user, resource, aws_environment, monitor_graph)
        logger.info("END: graph")
        return Response(data=monitor_graph.serialize(), status=status.HTTP_200_OK)
