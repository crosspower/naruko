from django.conf import settings
import boto3


class Ses:

    def __init__(self, source, reply_to_address):
        self.client = boto3.client('ses', region_name=settings.SES_REGION)
        self.source = source
        self.reply_to_address = reply_to_address

    @staticmethod
    def build_destination(to_addresses: list, cc_addresses: list, bcc_addresses: list):
        return {
                'ToAddresses': to_addresses,
                'CcAddresses': cc_addresses,
                'BccAddresses': bcc_addresses
            }

    @staticmethod
    def build_message(subject, text):
        return {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': text,
                        'Charset': 'UTF-8'
                    }
                }
            }

    def send_password_reset_mail(self, user_mail, raw_new_password):
        self.send_mail(
            subject="【鳴子】パスワードリセット",
            text="パスワードをリセットしました。\n 新しいパスワードは {} です。\n このメールに心当たりのない方はメールを破棄していただくようお願いいたします。".format(raw_new_password),
            to_addresses=[user_mail]
        )

    def send_signup_user(self, user_mail, user_name, tenant_name, raw_new_password):
        self.send_mail(
            subject="【鳴子】新規登録",
            text="{} {} 様 \n 鳴子のご登録が完了いたしました。 以下のパスワードでログインしてご利用いただくことができます。 \n パスワード： {}".format(tenant_name, user_name, raw_new_password),
            to_addresses=[user_mail]
        )

    def send_notify_mail(self, notification_message, address: str):
        self.send_mail(
            subject=settings.NOTIFY_TEXT_SUBJECT,
            text=settings.NOTIFY_TEXT_MESSAGE.format(
                timestamp=notification_message.time,
                aws_name=notification_message.aws.name,
                aws_account_id=notification_message.aws.aws_account_id,
                region="{}リージョン".format(notification_message.resource.get_region_japanese()),
                service=notification_message.resource.get_service_name(),
                resource_id=notification_message.resource.resource_id,
                metrics=notification_message.resource.get_metrics_japanese(notification_message.metric),
                level=notification_message.level
            ),
            to_addresses=[address]
        )

    def send_schedule_result(self, schedule, address: str, result: bool):
        self.send_mail(
            subject="【鳴子】スケジュール実行結果 {}".format(schedule.event_model.name),
            text="スケジュール {} の実行に{}しました。".format(schedule.event_model.name, "成功" if result else "失敗"),
            to_addresses=[address]
        )

    def send_mail(self, subject, text, to_addresses: list, cc_addresses: list =[], bcc_addresses: list =[]):
        destination = Ses.build_destination(to_addresses, cc_addresses, bcc_addresses)
        message = Ses.build_message(subject, text)
        self._send_mail(destination, message)

    def _send_mail(self, destination, message):
        response = self.client.send_email(
            Source=self.source,
            Destination=destination,
            Message=message,
            ReplyToAddresses=[self.reply_to_address]
        )
