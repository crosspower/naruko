from django.test import TestCase
from backend.exceptions import InvalidNotificationException
from unittest import mock
# デコレーターをmock化
with mock.patch('backend.models.OperationLogModel.operation_log', lambda executor_index=None, target_method=None, target_arg_index_list=None: lambda func: func):
    from backend.usecases.control_event import ControlEventUseCase


class ControlEventTestCase(TestCase):

    # SNS購読確認：正常系
    @mock.patch('backend.usecases.control_event.Sns')
    def test_confirm_subscription(self, mock_sns):
        ControlEventUseCase(mock.Mock()).confirm_subscription(
            dict(
                Token="token",
                TopicArn="topicarn"
            )
        )

        mock_sns.assert_called_with(arn="topicarn")
        mock_sns.return_value.confirm_subscription.assert_called_with("token")

    # SNS通知検証：正常系
    @mock.patch('backend.usecases.control_event.Sns')
    def test_verify_sns_notification(self, mock_sns):
        mock_sns.return_value.verify_notification.return_value = True
        data = dict()
        ControlEventUseCase(mock.Mock()).verify_sns_notification(
            data
        )

        mock_sns.verify_notification.assert_called_with(data)

    # SNS通知検証：検証失敗
    @mock.patch('backend.usecases.control_event.Sns')
    def test_verify_sns_notification_fail(self, mock_sns):
        mock_sns.verify_notification.return_value = False
        data = dict()

        with self.assertRaises(InvalidNotificationException):
            ControlEventUseCase(mock.Mock()).verify_sns_notification(
                data
            )

        mock_sns.verify_notification.assert_called_with(data)

    # スケジュール実行：正常系
    def test_execute(self):
        mock_event = mock.Mock()
        ControlEventUseCase(mock.Mock()).execute(
            mock_event
        )
        mock_event.execute.assert_called_once()

