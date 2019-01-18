from django.conf import settings
import boto3


class Connect:

    def __init__(self, source):
        self.client = boto3.client('connect', region_name=settings.CONNECT_REGION)
        self.source = source

    def start_outbound_voice_contact(self, notification_message, phone_number):
        # メッセージは固定
        self.client.start_outbound_voice_contact(
            DestinationPhoneNumber=phone_number,
            ContactFlowId=settings.CONNECT_NOTIFY_FLOW_ID,
            InstanceId=settings.CONNECT_NOTIFY_INSTANCE_ID,
            SourcePhoneNumber=self.source,
            Attributes=dict(
                message=settings.NOTIFY_TEXT_MESSAGE.format(
                    timestamp=notification_message.time,
                    aws_name=notification_message.aws.name,
                    aws_account_id=notification_message.aws.aws_account_id,
                    region="{}リージョン".format(notification_message.resource.get_region_japanese()),
                    service=notification_message.resource.get_service_name(),
                    resource_id=notification_message.resource.resource_id,
                    metrics=notification_message.resource.get_metrics_japanese(notification_message.metric),
                    level=notification_message.level
                ),
                loop_count="3",
                status="call"
            )
        )