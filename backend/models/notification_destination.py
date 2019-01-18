from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel
from backend.models.soft_deletion_model import SoftDeletionModel
from backend.models.tenant import TenantModel
from backend.models.resource.resource import Resource
from backend.models.aws_environment import AwsEnvironmentModel
from backend.externals.ses import Ses
from backend.externals.connect import Connect
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import phonenumbers


class NotificationDestinationModel(PolymorphicModel, SoftDeletionModel):

    class Meta:
        db_table = "notification_destination"

    name = models.CharField(max_length=50)
    tenant = models.ForeignKey('TenantModel', on_delete=models.CASCADE, related_name='notification_destinations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def all(cls):
        return cls.objects.all().filter(deleted=0)

    @classmethod
    def get(cls, pk, tenant_pk):
        query_set = cls.objects.filter(id=pk, tenant_id=tenant_pk).filter(deleted=0)
        if not query_set:
            raise models.ObjectDoesNotExist("id: {}, tenant_id: {}".format(pk, tenant_pk))
        return query_set[0]

    @staticmethod
    @receiver(pre_save, sender=TenantModel)
    def company_soft_delete_cascade(instance: TenantModel, **kwargs):
        if instance.deleted:
            for notification_destination in instance.notification_destinations.all():
                notification_destination.delete()

    class NotificationMessage:

        LEVEL = {
            "CAUTION": "警告",
            "DANGER": "危険"
        }

        def __init__(self, alarm_message):
            region = alarm_message["Region"]
            service_type = alarm_message["Trigger"]["Namespace"].replace("AWS/", "")
            resource_id = alarm_message["Trigger"]["Dimensions"][0]["value"]
            level = alarm_message["AlarmName"].rsplit('-', 1)[1]
            time_str = alarm_message["StateChangeTime"]
            time_date = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            # CloudWatchアラームからの時刻はUTC
            time_date += timedelta(hours=settings.TIME_DIFFERENCE)

            self.resource = Resource.get_service_resource(
                region, service_type, resource_id)
            self.metric = alarm_message["Trigger"]["MetricName"]
            self.level = self.LEVEL.get(level, level)  # DANGER or CAUTION
            self.aws = AwsEnvironmentModel.objects.get(aws_account_id=alarm_message["AWSAccountId"])
            self.time = time_date.strftime('%Y{}%m{}%d{} %H{}%M{}%S{}').format("年", "月", "日", "時", "分", "秒")

    def notify(self, message: NotificationMessage):
        raise NotImplementedError

    def result_schedule(self, schedule, result: bool):
        raise NotImplementedError


class EmailDestination(NotificationDestinationModel, SoftDeletionModel):

    class Meta:
        db_table = "email_destination"

    address = models.EmailField(max_length=200)

    def notify(self, message: NotificationDestinationModel.NotificationMessage):
        try:
            ses = Ses(settings.SES_ADDRESS, settings.SES_ADDRESS)
            ses.send_notify_mail(message, self.address)
        except ClientError as e:
            return e.response["Error"]["Message"]
        else:
            return "SUCCESS."

    def result_schedule(self, schedule, result: bool):
        try:
            ses = Ses(settings.SES_ADDRESS, settings.SES_ADDRESS)
            ses.send_schedule_result(schedule, self.address, result)
        except ClientError as e:
            return e.response["Error"]["Message"]
        else:
            return "SUCCESS."


class TelephoneDestination(NotificationDestinationModel, SoftDeletionModel):

    class Meta:
        db_table = "telephone_destination"

    phone_number = models.CharField(max_length=15)

    def notify(self, message: NotificationDestinationModel.NotificationMessage):
        try:
            connect = Connect(settings.CONNECT_PHONE_NUMBER)
            e164_number = phonenumbers.format_number(
                phonenumbers.parse(self.phone_number, 'JP'),
                phonenumbers.PhoneNumberFormat.E164
            )
            connect.start_outbound_voice_contact(message, e164_number)
        except ClientError as e:
            return e.response["Error"]["Message"]
        else:
            return "SUCCESS."

    def result_schedule(self, schedule, result: bool):
        # スケジュール実行時による電話通知はしない
        pass
