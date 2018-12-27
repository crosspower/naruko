from django.core.exceptions import PermissionDenied
from django.test import TestCase
from backend.usecases.control_notification import ControlNotificationUseCase
from backend.exceptions import InvalidNotificationException
from unittest import mock


class ControlNotificationTestCase(TestCase):

    # 通知先取得：正常系
    @mock.patch('backend.usecases.control_notification.NotificationDestinationModel')
    def test_fetch_destinations(self, mock_dest):
        mock_dest1 = mock.Mock()
        mock_dest2 = mock.Mock()
        mock_dest3 = mock.Mock()
        expected_value = [mock_dest1, mock_dest2, mock_dest3]
        mock_tenant = mock.Mock()

        value_filter = mock_dest.all.return_value.filter
        value_filter.return_value = expected_value

        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        response = ControlNotificationUseCase(mock.Mock()).fetch_destinations(mock_user, mock_tenant)

        value_filter.assert_called_once_with(tenant=mock_tenant)
        self.assertEqual(response, expected_value)

    # 通知先取得：リクエストユーザーが指定されたテナントに属していない場合
    @mock.patch('backend.usecases.control_notification.NotificationDestinationModel')
    def test_fetch_destinations_not_belong_to_tenant(self, mock_dest):

        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_user.is_belong_to_tenant.return_value = False

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).fetch_destinations(mock_user, mock.Mock())

        mock_dest.assert_not_called()

    # 通知先取得：リクエストユーザーがUSER権限の場合
    @mock.patch('backend.usecases.control_notification.NotificationDestinationModel')
    def test_fetch_destinations_user_role(self, mock_dest):

        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = False
        mock_user.is_belong_to_tenant.return_value = False

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).fetch_destinations(mock_user, mock.Mock())

        mock_dest.assert_not_called()

    # 通知先設定：正常系
    def test_create_destination(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_dest = mock.Mock()

        res = ControlNotificationUseCase(mock.Mock()).create_destination(mock_user, mock_dest)

        self.assertEqual(res, mock_dest)
        mock_dest.save.assert_called_once()

    # 通知先設定：リクエストユーザーが指定されたテナントに属していない場合
    def test_create_destination_not_belong_to_tenant(self):
        mock_user = mock.Mock()
        mock_user.is_belong_to_tenant.return_value = False
        mock_dest = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).create_destination(mock_user, mock_dest)

        mock_dest.save.assert_not_called()

    # 通知先設定：リクエストユーザーがUSER権限の場合
    def test_create_destination_user_role(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = False
        mock_user.is_belong_to_tenant.return_value = False
        mock_dest = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).create_destination(mock_user, mock_dest)

        mock_dest.save.assert_not_called()

    # 通知先削除：正常系
    def test_delete_destination(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_dest = mock.Mock()

        ControlNotificationUseCase(mock.Mock()).delete_destination(mock_user, mock_dest)

        mock_dest.delete.assert_called_once()

    # 通知先削除：リクエストユーザーが指定されたテナントに属していない場合
    def test_delete_destination_not_belong_to_tenant(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_user.is_belong_to_tenant.return_value = False
        mock_dest = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).delete_destination(mock_user, mock_dest)

        mock_dest.delete.assert_not_called()

    # 通知先削除：リクエストユーザーがUSER権限の場合
    def test_delete_destination_user_role(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = False
        mock_user.is_belong_to_tenant.return_value = False
        mock_dest = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).delete_destination(mock_user, mock_dest)

        mock_dest.delete.assert_not_called()

    # 通知グループ取得：正常系
    @mock.patch('backend.usecases.control_notification.NotificationGroupModel')
    def test_fetch_groups(self, mock_group):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_tenant = mock.Mock()

        mock_group1 = mock.Mock()
        mock_group2 = mock.Mock()
        mock_group3 = mock.Mock()
        expected_value = [mock_group1, mock_group2, mock_group3]
        objects_filter = mock_group.objects.filter
        objects_filter.return_value = expected_value

        res = ControlNotificationUseCase(mock.Mock()).fetch_groups(mock_user, mock_tenant)

        objects_filter.assert_called_once_with(tenant=mock_tenant)
        self.assertEqual(res, expected_value)

    # 通知グループ取得：リクエストユーザーがUSER権限の場合
    @mock.patch('backend.usecases.control_notification.NotificationGroupModel')
    def test_fetch_groups_user_role(self, mock_group):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = False
        mock_tenant = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).fetch_groups(mock_user, mock_tenant)

    # 通知グループ取得：リクエストユーザーが指定されたテナントに属していない場合
    @mock.patch('backend.usecases.control_notification.NotificationGroupModel')
    def test_fetch_groups_no_tenant(self, mock_group):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_user.is_belong_to_tenant.return_value = False
        mock_tenant = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).fetch_groups(mock_user, mock_tenant)

    # 通知グループ作成：正常系
    def test_create_group(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_group = mock.Mock()

        res = ControlNotificationUseCase(mock.Mock()).save_group(mock_user, mock_group)

        mock_group.save.assert_called_once()
        self.assertEqual(res, mock_group)

    # 通知グループ作成：リクエストユーザーがUSER権限の場合
    def test_create_group_user_role(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = False
        mock_group = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).save_group(mock_user, mock_group)

        mock_group.save.assert_not_called()

    # 通知グループ作成：リクエストユーザーが指定のテナントに属していない場合
    def test_create_group_no_tenant(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_user.is_belong_to_tenant.return_value = False
        mock_group = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).save_group(mock_user, mock_group)

        mock_group.save.assert_not_called()

    # 通知グループ削除：正常系
    def test_delete_group(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_group = mock.Mock()

        ControlNotificationUseCase(mock.Mock()).delete_group(mock_user, mock_group)

        mock_group.delete.assert_called_once()

    # 通知グループ削除: リクエストユーザーがUSER権限の場合
    def test_delete_group_user_role(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = False
        mock_group = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).delete_group(mock_user, mock_group)

        mock_group.delete.assert_not_called()

    # 通知グループ削除: リクエストユーザーが指定のテナントに属していない場合
    def test_delete_group_no_tenant(self):
        mock_user = mock.Mock()
        mock_user.can_control_notification.return_value = True
        mock_user.is_belong_to_tenant.return_value = False
        mock_group = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlNotificationUseCase(mock.Mock()).delete_group(mock_user, mock_group)

        mock_group.delete.assert_not_called()

    # SNS購読確認：正常系
    @mock.patch('backend.usecases.control_notification.Sns')
    def test_confirm_subscription(self, mock_sns):
        ControlNotificationUseCase(mock.Mock()).confirm_subscription(
            dict(
                Token="token",
                TopicArn="topicarn"
            )
        )

        mock_sns.assert_called_with(arn="topicarn")
        mock_sns.return_value.confirm_subscription.assert_called_with("token")

    # SNS通知検証：正常系
    @mock.patch('backend.usecases.control_notification.Sns')
    def test_verify_sns_notification(self, mock_sns):
        mock_sns.return_value.verify_notification.return_value = True
        data = dict()
        ControlNotificationUseCase(mock.Mock()).verify_sns_notification(
            data
        )

        mock_sns.verify_notification.assert_called_with(data)

    # SNS通知検証：検証失敗
    @mock.patch('backend.usecases.control_notification.Sns')
    def test_verify_sns_notification_fail(self, mock_sns):
        mock_sns.verify_notification.return_value = False
        data = dict()

        with self.assertRaises(InvalidNotificationException):
            ControlNotificationUseCase(mock.Mock()).verify_sns_notification(
                data
            )

        mock_sns.verify_notification.assert_called_with(data)

    # 通知：正常系
    def test_notify(self):
        mock_message = mock.Mock()
        mock_group = mock.Mock()
        mock_dest = mock.Mock()
        mock_group.destinations.filter.return_value = [mock_dest]
        mock_message.aws.notification_groups.filter.return_value = [mock_group]

        ControlNotificationUseCase(mock.Mock()).notify(
            mock_message
        )
