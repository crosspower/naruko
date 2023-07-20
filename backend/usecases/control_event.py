from backend.models import Event, OperationLogModel
from backend.exceptions import InvalidNotificationException
from backend.logger import NarukoLogging
from backend.externals.sns import Sns


class ControlEventUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    @staticmethod
    def target_info(event: Event):
        return event.identifier_for_log()

    def confirm_subscription(self, confirmation_data: dict):
        self.logger.info("START: confirm_subscription")

        token = confirmation_data["Token"]
        arn = confirmation_data["TopicArn"]

        self.logger.info("Confirm SNS Arn: {}".format(arn))

        sns = Sns(arn=arn)
        sns.confirm_subscription(token)
        self.logger.info("END: confirm_subscription")

    def verify_sns_notification(self, notification_data: dict):
        self.logger.info("START: verify_sns_notification")

        verify = Sns.verify_notification(notification_data)

        self.logger.info("Verify Result: {}".format(verify))
        if not verify:
            raise InvalidNotificationException(notification_data)

        self.logger.info("END: verify_sns_notification")

    def execute(self, event: Event):
        self.logger.info("START: execute")

        event.execute()

        self.logger.info("END: execute")
