from botocore.exceptions import ClientError
from django.db.models.base import ObjectDoesNotExist
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from backend.models.aws_environment import AwsEnvironmentModel
from backend.usecases.control_resource import ControlResourceUseCase
from backend.exceptions import NarukoException
from backend.logger import NarukoLogging


class DocumentViewSet(ViewSet):

    def list(self, request, tenant_pk=None, aws_env_pk=None, region_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        try:
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            documents = ControlResourceUseCase(log).fetch_documents(request.user, aws_environment, region_pk)
        except (TypeError, ValueError, KeyError, NarukoException, ClientError) as e:
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
            return Response(data=[doc.serialize() for doc in documents],
                            status=status.HTTP_200_OK)

    def retrieve(self, request, tenant_pk=None, aws_env_pk=None, region_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: retrieve")
        try:
            aws_environment = AwsEnvironmentModel.objects.get(id=aws_env_pk, tenant_id=tenant_pk)
            document = ControlResourceUseCase(log).describe_document(request.user, aws_environment, region_pk, pk)
        except (TypeError, ValueError, KeyError, NarukoException, ClientError) as e:
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
            return Response(data=document.serialize(),
                            status=status.HTTP_200_OK)
