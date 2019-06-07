from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from backend.usecases.control_notification import ControlNotificationUseCase
from backend.models import NotificationDestinationModel
from backend.logger import NarukoLogging
import json


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def notify(request: Request):
    log = NarukoLogging(request)
    logger = log.get_logger(__name__)
    logger.info("START: notify")
    # リクエストがSNSからであるかを検証する
    use_case = ControlNotificationUseCase(log)
    body_data = json.loads(request.body)
    logger.info(body_data)
    use_case.verify_sns_notification(body_data)

    # SNSの種別ごとに分岐
    sns_type = body_data.get("Type")
    logger.info("Message Type is {}.".format(sns_type))
    if sns_type == "Notification":
        # 通知：アラームの内容に従って通知処理を実施する
        alarm_message = json.loads(body_data["Message"])
        use_case.notify(NotificationDestinationModel.NotificationMessage(alarm_message))
    elif sns_type == "SubscriptionConfirmation":

        # 購読開始：SNSトピック登録時に初期検証を実施する
        use_case.confirm_subscription(body_data)
    elif sns_type == "UnsubscribeConfirmation":
        # 購読解除：SNSトピック購読解除
        logger.info("UnsubscribeConfirmation. {}".format(body_data["Message"]))
    else:
        # 存在しない種別
        logger.warning("UnknownSnsMessageType.")
        logger.warning(body_data)

    logger.info("END: notify")
    return Response(status=status.HTTP_200_OK)
