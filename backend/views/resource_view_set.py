from botocore.exceptions import ClientError
from django.db.models.base import ObjectDoesNotExist
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from backend.usecases.control_resource import ControlResourceUseCase
from backend.models.aws_environment import AwsEnvironmentModel
from backend.models.resource.resource import Resource
from backend.models.resource.command import Command, Document, Parameter
from backend.exceptions import NarukoException
from backend.logger import NarukoLogging


class ResourceViewSet(ViewSet):

    def list(self, request, tenant_pk=None, aws_env_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        try:
            region = request.GET.get("region")
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            resources = ControlResourceUseCase(log).fetch_resources(
                request.user,
                aws_environment,
                region
            )
        except (TypeError, ValueError, KeyError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            # AWS環境が存在しない
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: list")
            return Response(data=[resource.serialize(aws_environment) for resource in resources],
                            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def start(self, request, tenant_pk=None, aws_env_pk=None,
              region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: start")
        try:
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            resource = Resource.get_service_resource(region_pk, service_pk, pk)
            ControlResourceUseCase(log).start_resource(request.user, aws_environment, resource)
        except (TypeError, ValueError, KeyError, ClientError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            # AWS環境が存在しない
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: start")
            return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def reboot(self, request, tenant_pk=None, aws_env_pk=None,
               region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: reboot")
        try:
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            resource = Resource.get_service_resource(region_pk, service_pk, pk)
            ControlResourceUseCase(log).reboot_resource(request.user, aws_environment, resource)
        except (TypeError, ValueError, KeyError, ClientError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            # AWS環境が存在しない
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: reboot")
            return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def stop(self, request, tenant_pk=None, aws_env_pk=None,
             region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: stop")
        try:
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            resource = Resource.get_service_resource(region_pk, service_pk, pk)
            ControlResourceUseCase(log).stop_resource(request.user, aws_environment, resource)
        except (TypeError, ValueError, KeyError, ClientError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            # AWS環境が存在しない
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: stop")
            return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, tenant_pk=None, aws_env_pk=None,
                 region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: retrieve")
        try:
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            resource = ControlResourceUseCase(log).describe_resource(
                request.user,
                aws_environment,
                Resource.get_service_resource(region_pk, service_pk, pk))
        except (TypeError, ValueError, KeyError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            # AWS環境が存在しない
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: retrieve")
            return Response(data=resource.serialize(aws_environment),
                            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def run_command(self, request, tenant_pk=None, aws_env_pk=None,
                    region_pk=None, service_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: run_command")
        try:
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            resource = Resource.get_service_resource(region_pk, service_pk, pk)
            command = Command(
                Document(
                    request.data["name"],
                    [Parameter(**param) for param in request.data["parameters"]]),
                resource)
            command = ControlResourceUseCase(log).run_command(request.user, aws_environment, command)
        except (TypeError, ValueError, KeyError, ClientError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            # AWS環境が存在しない
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: run_command")
            return Response(status=status.HTTP_200_OK, data=command.serialize())


class RegionViewSet(ViewSet):
    pass


class ServiceViewSet(ViewSet):
    pass
