from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from backend.models.event.event import EventRepository
from backend.usecases.control_event import ControlEventUseCase
from backend.logger import NarukoLogging
import json


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def event_execute(request: Request):
    log = NarukoLogging(request)
    logger = log.get_logger(__name__)
    logger.info("START: event_execute")

    # リクエストがSNSからであるかを検証する
    use_case = ControlEventUseCase(log)
    body_data = json.loads(request.body)
    logger.info(body_data)
    use_case.verify_sns_notification(body_data)

    # SNSの種別ごとに分岐
    sns_type = body_data.get("Type")
    logger.info("Message Type is {}.".format(sns_type))
    if sns_type == "Notification":
        # 通知：アラームの内容に従って通知処理を実施する
        message = json.loads(body_data["Message"])
        event = EventRepository.get(message["id"])
        use_case.execute(event)
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

    logger.info("END: event_execute")
    return Response(status=status.HTTP_200_OK)
