from django.core.exceptions import PermissionDenied
from django.test import TestCase
from unittest.mock import Mock, patch
from backend.usecases.control_operation_log import ControlOperationLog


class ControlOperationLogTestCase(TestCase):

    # 正常系
    @patch('backend.usecases.control_operation_log.OperationLogModel')
    def test_fetch_logs(self, mock_log_model):
        mock_user = Mock()
        mock_tenant = Mock()
        objects_filter = mock_log_model.objects.filter

        res = ControlOperationLog(Mock()).fetch_logs(mock_user, mock_tenant)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_other_user.assert_called_once()
        objects_filter.assert_called_once_with(tenant=mock_tenant)
        self.assertEqual(res, objects_filter.return_value)

    # 正常系 他のユーザーを管理できない場合
    @patch('backend.usecases.control_operation_log.OperationLogModel')
    def test_fetch_logs_cant_control_other_user(self, mock_log_model):
        mock_user = Mock()
        mock_user.can_control_other_user.return_value = False
        mock_tenant = Mock()
        objects_filter = mock_log_model.objects.filter

        res = ControlOperationLog(Mock()).fetch_logs(mock_user, mock_tenant)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_other_user.assert_called_once()
        objects_filter.assert_called_once_with(tenant=mock_tenant, executor=mock_user)
        self.assertEqual(res, objects_filter.return_value)

    # テナントに属していない場合
    @patch('backend.usecases.control_operation_log.OperationLogModel')
    def test_fetch_logs_not_belong_to_tenant(self, mock_log_model):
        mock_user = Mock()
        mock_user.is_belong_to_tenant.return_value = False
        mock_tenant = Mock()
        objects_filter = mock_log_model.objects.filter

        with self.assertRaises(PermissionDenied):
            ControlOperationLog(Mock()).fetch_logs(mock_user, mock_tenant)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_other_user.assert_not_called()
        objects_filter.assert_not_called()
