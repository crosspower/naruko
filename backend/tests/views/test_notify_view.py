from django.test import TestCase
from rest_framework.test import APIClient
from unittest import mock


@mock.patch('backend.views.notify_view.NotificationDestinationModel.NotificationMessage')
@mock.patch('backend.views.notify_view.ControlNotificationUseCase')
class NotifyViewTestCase(TestCase):

    api_path = "/api/notify/"

    # 正常系：認証せずに使用できることを確認する：通知
    def test_notify_not_login(self, use_case, message_mock):
        client = APIClient()

        data = {
            "Type": "Notification",
            "Message": "{\"TEST\": \"test\"}"
        }
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        message_mock.assert_called_with(dict(TEST="test"))
        use_case.return_value.verify_sns_notification.assert_called_with(data)
        use_case.return_value.notify.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # 正常系：購読確認
    def test_notify_confirm(self, use_case, message_mock):
        client = APIClient()

        data = {
            "Type": "SubscriptionConfirmation",
            "Message": "{\"TEST\": \"test\"}"
        }
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        message_mock.assert_not_called()
        use_case.return_value.verify_sns_notification.assert_called_with(data)
        use_case.return_value.confirm_subscription.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # 正常系：購読解除
    def test_notify_unsubscribe(self, use_case, message_mock):
        client = APIClient()

        data = {
            "Type": "UnsubscribeConfirmation",
            "Message": "{\"TEST\": \"test\"}"
        }
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        message_mock.assert_not_called()
        use_case.return_value.verify_sns_notification.assert_called_with(data)
        self.assertEqual(response.status_code, 200)

    # 不正なリクエスト
    def test_notify_invalid_params(self, use_case, message_mock):
        client = APIClient()

        data = {
            "Type": "Notification",
            "Message": ""
        }
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        message_mock.assert_not_called()
        use_case.return_value.verify_sns_notification.assert_called_with(data)
        use_case.return_value.notify.assert_not_called()
        self.assertEqual(response.status_code, 400)
