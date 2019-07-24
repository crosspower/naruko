from rest_framework.viewsets import ViewSet
from backend.models import AwsEnvironmentModel, TenantModel
from backend.serializers.aws_environment_model_serializer import (AwsEnvironmentModelGetDetailSerializer,
                                                                  AwsEnvironmentModelCreateSerializer,
                                                                  AwsEnvironmentModelUpdateSerializer)
from backend.usecases.control_aws_environment import ControlAwsEnvironment
from rest_framework.response import Response
from rest_framework import status
from backend.logger import NarukoLogging
from django.db import transaction
from rest_framework.decorators import action


class AwsEnvironmentModelViewSet(ViewSet):
    queryset = AwsEnvironmentModel.objects.all()
    serializer_class = AwsEnvironmentModelGetDetailSerializer

    def list(self, request, tenant_pk=None, detail=True):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        tenant = TenantModel.objects.get(id=tenant_pk)
        aws_environments = ControlAwsEnvironment(log).fetch_aws_environments(request.user, tenant)
        return Response(data={"aws_environments": [
            AwsEnvironmentModelGetDetailSerializer(aws_environment).data for aws_environment in aws_environments]})

    @transaction.atomic
    def create(self, request, tenant_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        request.data['tenant'] = tenant_pk
        create_serializer = AwsEnvironmentModelCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        model = create_serializer.save()
        ControlAwsEnvironment(log).save_aws_environment(request.user, model)
        data = AwsEnvironmentModelGetDetailSerializer(model).data
        logger.info("END: create")
        return Response(data=data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, tenant_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: update")
        model = AwsEnvironmentModel.objects.get(id=pk, tenant_id=tenant_pk)
        serializer = AwsEnvironmentModelUpdateSerializer(
            instance=model,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        updated_model = serializer.save()

        ControlAwsEnvironment(log).save_aws_environment(request.user, updated_model)
        data = AwsEnvironmentModelGetDetailSerializer(updated_model).data
        logger.info("END: update")
        return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, tenant_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: destroy")
        model = AwsEnvironmentModel.objects.get(id=pk, tenant_id=tenant_pk)
        ControlAwsEnvironment(log).delete_aws_environment(request.user, model)
        logger.info("END: destroy")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def billing(self, request, tenant_pk=None, pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: billing")
        aws_environment = AwsEnvironmentModel.objects.get(id=pk, tenant_id=tenant_pk)
        billing_graph = ControlAwsEnvironment(log).billing_graph(request.user, aws_environment, **request.data)
        logger.info("END: billing")
        return Response(data=billing_graph, status=status.HTTP_200_OK)
