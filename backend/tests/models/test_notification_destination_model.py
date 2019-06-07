from django.test import TestCase
from backend.models.notification_destination import NotificationDestinationModel, EmailDestination, TenantModel, \
    TelephoneDestination
from backend.models import AwsEnvironmentModel, TenantModel
from backend.models.resource.ec2 import Ec2
from datetime import datetime
from unittest import mock
from botocore.exceptions import ClientError


class NotificationDestinationModelTestCase(TestCase):

    # 通知先が登録されていないことを確認する
    def test_is_empty(self):
        objects_all = NotificationDestinationModel.objects.all()
        self.assertEqual(objects_all.count(), 0)

    # 通知先が登録できることを確認する
    def test_create(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = NotificationDestinationModel.objects.create(
            name="test", tenant=tenant_model, created_at=now, updated_at=now)

        objects_create.save()

        objects_all = NotificationDestinationModel.all()
        self.assertEqual(objects_all.count(), 1)

    # 登録した通知先が削除できることを確認する
    def test_delete(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = NotificationDestinationModel.objects.create(
            name="test", tenant=tenant_model, created_at=now, updated_at=now)

        objects_create.save()

        objects_all = NotificationDestinationModel.all()
        self.assertEqual(objects_all.count(), 1)

        objects_all.all().delete()

        model_objects_all = NotificationDestinationModel.all()
        self.assertEqual(model_objects_all.count(), 0)

    # 登録した通知先の更新ができることを確認する
    def test_update(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = NotificationDestinationModel.objects.create(
            name="test", tenant=tenant_model, created_at=now, updated_at=now)

        objects_create.save()

        objects_all = NotificationDestinationModel.all()
        self.assertEqual(objects_all.count(), 1)

        notification_destination_model = objects_all[0]
        notification_destination_model.name = "update"
        notification_destination_model.save()

        objects_get = NotificationDestinationModel.objects.get(name="update")
        self.assertEqual(objects_get.name, "update")

    # Emailとして登録できるか確認する
    def test_email(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = EmailDestination.objects.create(
            name="test", tenant=tenant_model, address="test@test.com", created_at=now, updated_at=now)

        objects_create.save()

        # 通知先として取得したときに区別できているか
        objects_all = NotificationDestinationModel.all()
        self.assertTrue(isinstance(objects_all[0], EmailDestination))

        # Email通知先として取得したときに区別できているか
        destination_objects_all = EmailDestination.all()
        self.assertTrue(isinstance(destination_objects_all[0], EmailDestination))

    # Telephoneとして登録できるか確認する
    def test_telephone(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = TelephoneDestination.objects.create(
            name="test", tenant=tenant_model, phone_number="080-1234-5678", country_code=81, created_at=now, updated_at=now)

        objects_create.save()

        # 通知先として取得したときに区別できているか
        objects_all = NotificationDestinationModel.all()
        self.assertTrue(isinstance(objects_all[0], TelephoneDestination))

        # Telephone通知先として取得したときに区別できているか
        destination_objects_all = TelephoneDestination.all()
        self.assertTrue(isinstance(destination_objects_all[0], TelephoneDestination))

    # テナントを削除したときに紐づく通知先が削除されることを確認する
    def test_delete_cascade_tenant(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = NotificationDestinationModel.objects.create(
            name="test", tenant=tenant_model, created_at=now, updated_at=now)

        objects_create.save()

        objects_all = NotificationDestinationModel.all()
        self.assertEqual(objects_all.count(), 1)

        tenant_model.delete()
        model_objects_all = NotificationDestinationModel.all()
        self.assertEqual(model_objects_all.count(), 0)

    # NotificationMessageクラス
    def test_notification_message(self):
        tenant_model = TenantModel.objects.create(
            tenant_name="test_name",
            email="test@test.com",
            tel="03-1234-5678")
        tenant_model.save()
        aws_environment_model = AwsEnvironmentModel.objects.create(
            aws_account_id="1234567890",
            name="test_name",
            aws_role="test_role",
            aws_external_id="test_external",
            tenant=tenant_model)
        aws_environment_model.save()
        alarm_message = {
            "Region": "Asia Pacific (Tokyo)",
            "Trigger": {
                "Namespace": "AWS/EC2",
                "Dimensions": [
                    {"name": "InstanceId", "value": "i-1234567890123456"}
                ],
                "MetricName": "NetworkOut"
            },
            "AlarmName": "NARUKO-EC2-i-1234567890123456-NetworkOut-DANGER",
            "StateChangeTime": "2018-12-01T00:00:00.000+0000",
            "AWSAccountId": "1234567890",
            "NewStateValue": "ALARM"
        }

        message = NotificationDestinationModel.NotificationMessage(alarm_message)

        self.assertEqual(message.resource.region, "Asia Pacific (Tokyo)")
        self.assertEqual(message.resource.resource_id, "i-1234567890123456")
        self.assertEqual(message.metric, "NetworkOut")
        self.assertEqual(message.level, "危険")
        self.assertEqual(message.aws.aws_account_id, "1234567890")
        self.assertEqual(message.time, "2018年12月01日 09時00分00秒")
        self.assertTrue(isinstance(message.resource, Ec2))

    # メール通知：正常系
    @mock.patch('backend.models.notification_destination.Ses')
    def test_email_notify(self, mock_ses):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = EmailDestination.objects.create(
            name="test", tenant=tenant_model, address="test@test.com", created_at=now, updated_at=now)

        objects_create.save()

        mock_message = mock.Mock()
        res = objects_create.notify(mock_message)

        mock_ses.return_value.send_notify_mail.assert_called_with(mock_message, "test@test.com")
        self.assertEqual(res, "SUCCESS.")

    # メール通知：通知失敗
    @mock.patch('backend.models.notification_destination.Ses')
    def test_email_notify_exception(self, mock_ses):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = EmailDestination.objects.create(
            name="test", tenant=tenant_model, address="test@test.com", created_at=now, updated_at=now)

        objects_create.save()

        mock_ses.return_value.send_notify_mail.side_effect = ClientError(
            error_response=dict(Error=dict(Message="TEST_MESSAGE")),
            operation_name="TEST"
        )

        mock_message = mock.Mock()
        res = objects_create.notify(mock_message)

        mock_ses.return_value.send_notify_mail.assert_called_with(mock_message, "test@test.com")
        self.assertEqual(res, "TEST_MESSAGE")

    # 電話通知：正常系
    @mock.patch('backend.models.notification_destination.Connect')
    def test_telephone_notify(self, mock_connect):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = TelephoneDestination.objects.create(
            name="test", tenant=tenant_model, phone_number="080-1234-5678", country_code=81, created_at=now, updated_at=now)

        objects_create.save()

        mock_message = mock.Mock()
        res = objects_create.notify(mock_message)

        mock_connect.return_value.start_outbound_voice_contact.assert_called_with(mock_message, "+818012345678")
        self.assertEqual(res, "SUCCESS.")

    # 電話通知：Connectとの接続でエラーが起きた場合
    @mock.patch('backend.models.notification_destination.Connect')
    def test_telephone_notify_exception(self, mock_connect):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = TelephoneDestination.objects.create(
            name="test", tenant=tenant_model, phone_number="080-1234-5678", country_code=81, created_at=now, updated_at=now)

        objects_create.save()

        mock_message = mock.Mock()
        mock_connect.return_value.start_outbound_voice_contact.side_effect = ClientError(
            error_response=dict(Error=dict(Message="TEST_MESSAGE")),
            operation_name="TEST"
        )

        res = objects_create.notify(mock_message)

        mock_connect.return_value.start_outbound_voice_contact.assert_called_with(mock_message, "+818012345678")
        self.assertEqual(res, "TEST_MESSAGE")

    # 電話通知：不正な電話番号の場合
    @mock.patch('backend.models.notification_destination.Connect')
    def test_telephone_notify_invalid_number(self, mock_connect):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        objects_create = TelephoneDestination.objects.create(
            name="test", tenant=tenant_model, phone_number="080-1234-5678", country_code=1000, created_at=now, updated_at=now)

        objects_create.save()

        mock_message = mock.Mock()
        res = objects_create.notify(mock_message)

        mock_connect.return_value.start_outbound_voice_contact.assert_not_called()
        self.assertEqual(res, "Destination's Country Code is invalid. 1000 Id: {}".format(objects_create.pk))
