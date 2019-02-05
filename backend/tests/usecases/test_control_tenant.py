from django.test import TestCase
from backend.models import TenantModel
from backend.exceptions import InvalidRoleException
from unittest import mock
# デコレーターをmock化
with mock.patch('backend.models.OperationLogModel.operation_log', lambda executor_index=None, target_method=None, target_arg_index_list=None: lambda func: func):
    from backend.usecases.control_tenant import ControlTenantUseCase


class ControlTenantTestCase(TestCase):

    @mock.patch("backend.usecases.control_tenant.TenantModel")
    def test_fetch_tenants(self, mock_tenant):
        mock_user = mock.Mock()
        mock_tenant1 = mock.Mock(spec=TenantModel)
        mock_tenant2 = mock.Mock(spec=TenantModel)
        mock_tenant3 = mock.Mock(spec=TenantModel)
        expected_response = [mock_tenant1, mock_tenant2, mock_tenant3]
        mock_tenant.objects.all.return_value = expected_response
        response = ControlTenantUseCase(mock.Mock()).fetch_tenants(mock_user)

        mock_user.can_control_tenant.assert_called_once()
        self.assertEqual(response, expected_response)

    @mock.patch("backend.usecases.control_tenant.TenantModel")
    def test_fetch_tenants_cant_control(self, mock_tenant):
        mock_user = mock.Mock()
        mock_user.can_control_tenant.return_value = False

        with self.assertRaises(InvalidRoleException):
            ControlTenantUseCase(mock.Mock()).fetch_tenants(mock_user)

        mock_user.can_control_tenant.assert_called_once()

    def test_delete_tenant(self):
        mock_user = mock.Mock()
        mock_tenant = mock.Mock(spec=TenantModel)
        ControlTenantUseCase(mock.Mock()).delete_tenant(mock_user, mock_tenant)

        mock_tenant.delete.assert_called()
        mock_user.can_control_tenant.assert_called_once()

    def test_delete_tenant_cant_control_tenant(self):
        mock_user = mock.Mock()
        mock_user.can_control_tenant.return_value = False
        mock_tenant = mock.Mock(spec=TenantModel)

        with self.assertRaises(InvalidRoleException):
            ControlTenantUseCase(mock.Mock()).delete_tenant(mock_user, mock_tenant)

        mock_user.can_control_tenant.assert_called_once()
        mock_tenant.delete.assert_not_called()

    @mock.patch("backend.usecases.control_tenant.UserModel")
    @mock.patch("backend.usecases.control_tenant.RoleModel")
    @mock.patch("backend.usecases.control_tenant.Ses")
    def test_create_tenant(self, mock_ses, mock_role_model, mock_user_model):
        # mock準備
        mock_request_user = mock.Mock()
        mock_request_user.can_control_tenant.return_value = True

        mock_tenant = mock.Mock()

        mock_user = mock.Mock()

        mock_scheduler = mock.Mock()
        mock_user_model.return_value = mock_scheduler

        res_tenant, res_user = ControlTenantUseCase(mock.Mock()).create_tenant(
            mock_request_user, mock_tenant, mock_user
        )

        # 呼び出し検証
        mock_request_user.can_control_tenant.assert_called_once()
        mock_tenant.save.assert_called()
        mock_role_model.objects.get.assert_called_once_with(id=mock_role_model.SCHEDULER_ID)
        mock_user_model.assert_called_once_with(
            email=mock_tenant.email,
            name="SCHEDULER",
            tenant=mock_tenant,
            role=mock_role_model.objects.get.return_value
        )
        mock_scheduler.reset_password.assert_called_once()
        mock_scheduler.save.assert_called_once()
        mock_user.reset_password.assert_called()
        mock_user.save.assert_called()
        mock_ses.assert_called()
        mock_ses.return_value.send_signup_user.assert_called()
        self.assertEqual(res_tenant, mock_tenant)
        self.assertEqual(res_user, mock_user)

    @mock.patch("backend.usecases.control_tenant.UserModel")
    @mock.patch("backend.usecases.control_tenant.RoleModel")
    @mock.patch("backend.usecases.control_tenant.Ses")
    def test_create_tenant_cant_control_tenant(self, mock_ses, mock_role_model, mock_user_model):
        # mock準備
        mock_request_user = mock.Mock()
        mock_request_user.can_control_tenant.return_value = False

        mock_tenant = mock.Mock()

        mock_user = mock.Mock()

        mock_scheduler = mock.Mock()
        mock_user_model.return_value = mock_scheduler

        with self.assertRaises(InvalidRoleException):
            ControlTenantUseCase(mock.Mock()).create_tenant(
                mock_request_user, mock_tenant, mock_user
            )

        # 呼び出し検証
        mock_request_user.can_control_tenant.assert_called_once()
        mock_tenant.save.assert_not_called()
        mock_role_model.objects.get.assert_not_called()
        mock_user_model.assert_not_called()
        mock_scheduler.reset_password.assert_not_called()
        mock_scheduler.save.assert_not_called()
        mock_user.reset_password.assert_not_called()
        mock_user.save.assert_not_called()
        mock_ses.assert_not_called()
        mock_ses.return_value.send_signup_user.assert_not_called()

    def test_update_tenant(self):
        mock_user = mock.Mock()
        mock_tenant = mock.Mock(spec=TenantModel)
        res = ControlTenantUseCase(mock.Mock()).update_tenant(mock_user, mock_tenant)

        mock_tenant.save.assert_called()
        mock_user.can_control_tenant.assert_called_once()
        self.assertEqual(res, mock_tenant)

    def test_update_tenant_cant_control_tenant(self):
        mock_user = mock.Mock()
        mock_user.can_control_tenant.return_value = False
        mock_tenant = mock.Mock(spec=TenantModel)

        with self.assertRaises(InvalidRoleException):
            ControlTenantUseCase(mock.Mock()).update_tenant(mock_user, mock_tenant)

        mock_tenant.save.assert_not_called()
        mock_user.can_control_tenant.assert_called_once()
