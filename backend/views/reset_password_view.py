from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models.base import ObjectDoesNotExist
from backend.serializers.user_model_serializer import UserModelDetailSerializer
from backend.serializers.reset_password_serializer import ResetPasswordSerializer
from backend.models import UserModel
from backend.usecases.reset_password import ResetPasswordUseCase
from backend.exceptions import NarukoException
from backend.logger import NarukoLogging


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def reset_password(request):
    log = NarukoLogging(request)
    logger = log.get_logger(__name__)
    logger.info("START: reset password")
    try:
        data = request.data
        user = UserModel.objects.get(email=data["email"])
        serializer = ResetPasswordSerializer(
            instance=user,
            data=data)
        serializer.is_valid(raise_exception=True)
        user = ResetPasswordUseCase(log).reset_password(user)

    except (TypeError, ValueError, KeyError, NarukoException) as e:
        # リクエストデータが不正
        logger.exception(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist as e:
        # ユーザーが存在しない
        logger.exception(e)
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(e)
        raise
    else:
        logger.info("END: reset password")
        return Response(data=UserModelDetailSerializer(user).data, status=status.HTTP_200_OK)
