from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from backend.serializers.user_model_serializer import UserModelDetailSerializer
from backend.serializers.reset_password_serializer import ResetPasswordSerializer
from backend.models import UserModel
from backend.usecases.reset_password import ResetPasswordUseCase
from backend.logger import NarukoLogging


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def reset_password(request):
    log = NarukoLogging(request)
    logger = log.get_logger(__name__)
    logger.info("START: reset password")
    data = request.data
    user = UserModel.objects.get(email=data["email"])
    serializer = ResetPasswordSerializer(
        instance=user,
        data=data)
    serializer.is_valid(raise_exception=True)
    user = ResetPasswordUseCase(log).reset_password(user)

    logger.info("END: reset password")
    return Response(data=UserModelDetailSerializer(user).data, status=status.HTTP_200_OK)
