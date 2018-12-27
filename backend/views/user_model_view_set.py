from rest_framework.viewsets import ViewSet
from django.db import transaction
from django.db.models.base import ObjectDoesNotExist
from backend.models import UserModel, TenantModel, AwsEnvironmentModel
from backend.serializers.user_model_serializer import UserModelDetailSerializer, UserModelSerializer
from rest_framework.response import Response
from rest_framework import status
from backend.usecases.control_user import ControlUserUseCase
from backend.serializers.user_update_validation_serializer import UserModelUpdateValidationSerializer
from backend.exceptions import NarukoException
from rest_framework_jwt.settings import api_settings
from backend.logger import NarukoLogging


class UserModeViewSet(ViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserModelDetailSerializer

    def list(self, request, tenant_pk=None, detail=True):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: list")
        try:
            tenant = TenantModel.objects.get(id=tenant_pk)
            users = ControlUserUseCase(log).fetch_users(request.user, tenant)
        except (TypeError, ValueError, TenantModel.DoesNotExist) as e:
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: list")
            return Response(data={"users": [UserModelDetailSerializer(user).data for user in users]})

    @transaction.atomic
    def destroy(self, request, pk=None, tenant_pk=None):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: destroy")
        try:
            with transaction.atomic():
                target_user = UserModel.objects.get(id=pk, tenant_id=tenant_pk)
                ControlUserUseCase(log).delete_user(request.user, target_user)
        except (TypeError, ValueError, UserModel.DoesNotExist) as e:
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            logger.info("END: destroy")
            return Response(status=status.HTTP_204_NO_CONTENT)

    '''
    ユーザー作成メソッド：POST
    request.data={
        email: str,
        name: str,
        password: str,
        role: int,
        aws_environments: list(int)
    }
    '''
    @transaction.atomic
    def create(self, request, tenant_pk=None, detail=True):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: create")
        try:
            with transaction.atomic():
                # バリデーション
                data = request.data
                data["tenant"] = tenant_pk
                serializer = UserModelSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                # 作成
                user = ControlUserUseCase(log).create_user(
                    request.user,
                    serializer.save(),
                    AwsEnvironmentModel.objects.filter(id__in=data["aws_environments"]),
                    data["password"]
                )

        except (TypeError, ValueError, KeyError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            logger.exception(e)
            # ロールまたはテナントが存在しない
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            # 成功
            print(user)
            print(UserModelDetailSerializer(user))
            logger.info("END: create")
            return Response(data=UserModelDetailSerializer(user).data, status=status.HTTP_201_CREATED)

    '''
    ユーザー更新メソッド：PUT
    request.data={
        email: str,
        name: str,
        password: str,
        role: int,
        aws_environments: list(int)
    }
    '''
    @transaction.atomic
    def update(self, request, pk=None, tenant_pk=None, detail=True):
        log = NarukoLogging(request)
        logger = log.get_logger(__name__)
        logger.info("START: update")
        try:
            with transaction.atomic():
                # バリデーション
                target_user = UserModel.objects.get(pk=pk, tenant_id=tenant_pk)
                UserModelUpdateValidationSerializer(
                    instance=target_user,
                    data=request.data).is_valid(raise_exception=True)

                # 更新
                user = ControlUserUseCase(log).update_user(
                    request.data,
                    request.user,
                    target_user
                )
                data = dict()
                data["user"] = UserModelDetailSerializer(user).data
                if request.user.id == user.id:
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    data["token"] = token

        except (TypeError, ValueError, KeyError, NarukoException) as e:
            # リクエストデータが不正
            logger.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            logger.exception(e)
            # ロールまたはテナントが存在しない
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(e)
            raise
        else:
            # 成功
            logger.info("END: update")
            return Response(data=data, status=status.HTTP_200_OK)
