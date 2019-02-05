from django.core.exceptions import PermissionDenied
from django.test import TestCase
from backend.exceptions import InvalidPasswordException, InvalidRoleException
from unittest import mock
# デコレーターをmock化
with mock.patch('backend.models.OperationLogModel.operation_log', lambda executor_index=None, target_method=None, target_arg_index_list=None: lambda func: func):
    from backend.usecases.control_user import ControlUserUseCase


class ControlUserTestCase(TestCase):

    # ユーザー取得：正常系
    @mock.patch("backend.usecases.control_user.UserModel")
    def test_fetch_user(self, mock_user_model: mock.Mock):
        mock_request_user = mock.Mock()
        mock_tenant = mock.Mock()

        objects_filter = mock_user_model.objects.filter

        res = ControlUserUseCase(mock.Mock()).fetch_users(mock_request_user, mock_tenant)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_control_other_user.assert_called_once()
        objects_filter.assert_called_once_with(tenant=mock_tenant)
        self.assertEqual(res, [])

    # ユーザー取得：テナントに属していない場合
    @mock.patch("backend.usecases.control_user.UserModel")
    def test_fetch_user_not_belong_to_tenant(self, mock_user_model: mock.Mock):
        mock_request_user = mock.Mock()
        mock_request_user.is_belong_to_tenant.return_value = False
        mock_tenant = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).fetch_users(mock_request_user, mock_tenant)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_control_other_user.assert_not_called()

    # ユーザー取得：他のユーザーを操作できない場合
    @mock.patch("backend.usecases.control_user.UserModel")
    def test_fetch_user_not_control_other_user(self, mock_user_model: mock.Mock):
        mock_request_user = mock.Mock()
        mock_request_user.can_control_other_user.return_value = False
        mock_tenant = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).fetch_users(mock_request_user, mock_tenant)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_control_other_user.assert_called_once()

    # ユーザー削除：正常系
    def test_delete_user(self):
        mock_request_user = mock.Mock()
        mock_user = mock.Mock()

        ControlUserUseCase(mock.Mock()).delete_user(mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_delete_user.assert_called_once()
        mock_user.delete.assert_called()

    # ユーザー削除：テナントに属していない場合
    def test_delete_user_not_belong_to_tenant(self):
        mock_request_user = mock.Mock()
        mock_request_user.is_belong_to_tenant.return_value = False
        mock_user = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).delete_user(mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_delete_user.assert_not_called()
        mock_user.delete.assert_not_called()

    # ユーザー削除：他のユーザーを操作できない場合
    def test_delete_user_not_control_other_user(self):
        mock_request_user = mock.Mock()
        mock_request_user.can_delete_user.return_value = False
        mock_user = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).delete_user(mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_delete_user.assert_called_once()
        mock_user.delete.assert_not_called()

    # ユーザー作成：正常系
    def test_create_user(self):
        mock_request_user = mock.Mock()
        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        password = "TEST"

        res = ControlUserUseCase(mock.Mock()).create_user(mock_request_user, mock_user, mock_aws, password)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called_once()
        mock_user.set_password.assert_called_once()
        mock_user.save.assert_called_once()
        mock_request_user.realignment_aws_environments.assert_called_once()
        self.assertEqual(res, mock_user)

    # ユーザー作成：テナントに属していない場合
    def test_create_user_not_belong_to_tenant(self):
        mock_request_user = mock.Mock()
        mock_request_user.is_belong_to_tenant.return_value = False

        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        password = "TEST"

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).create_user(mock_request_user, mock_user, mock_aws, password)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_not_called()
        mock_user.set_password.assert_not_called()
        mock_user.save.assert_not_called()
        mock_request_user.realignment_aws_environments.assert_not_called()

    # ユーザー作成：他のユーザーを操作できない場合
    def test_create_user_not_control_user(self):
        mock_request_user = mock.Mock()
        mock_request_user.can_save_user.return_value = False

        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        password = "TEST"

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).create_user(mock_request_user, mock_user, mock_aws, password)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called_once()
        mock_user.set_password.assert_not_called()
        mock_user.save.assert_not_called()
        mock_request_user.realignment_aws_environments.assert_not_called()

    # ユーザー作成：パスワードが不正な場合
    def test_create_user_invalid_password(self):
        mock_request_user = mock.Mock()
        mock_user = mock.Mock()
        mock_user.set_password.return_value = False

        mock_aws = mock.Mock()
        password = "TEST"

        with self.assertRaises(InvalidPasswordException):
            ControlUserUseCase(mock.Mock()).create_user(mock_request_user, mock_user, mock_aws, password)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called_once()
        mock_user.set_password.assert_called_once()
        mock_user.save.assert_not_called()
        mock_request_user.realignment_aws_environments.assert_not_called()

    # ユーザー作成：AWS環境を登録できない場合
    def test_create_user_cant_save_aws(self):
        mock_request_user = mock.Mock()
        mock_request_user.realignment_aws_environments.return_value = False

        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        password = "TEST"

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).create_user(mock_request_user, mock_user, mock_aws, password)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called_once()
        mock_user.set_password.assert_called_once()
        mock_user.save.assert_called_once()
        mock_request_user.realignment_aws_environments.assert_called_once()

    # ユーザー更新：正常系
    @mock.patch("backend.usecases.control_user.AwsEnvironmentModel")
    @mock.patch("backend.usecases.control_user.RoleModel")
    def test_update_user(self, mock_role_model, mock_aws_model):
        post_user_data = {
            "email": "test@test.com",
            "name": "test_name",
            "password": "!QAZ2wsx",
            "role": 3,
            "aws_environments": [1,2,3]
        }
        mock_request_user = mock.Mock()
        mock_user = mock.Mock()

        res = ControlUserUseCase(mock.Mock()).update_user(post_user_data, mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called()
        mock_user.can_changed_role.assert_called_once()
        mock_user.set_password.assert_called_once()
        mock_request_user.realignment_aws_environments.assert_called_once()
        mock_user.save.assert_called_once()
        self.assertEqual(res, mock_user)

    # ユーザー更新：テナントに属していない場合
    @mock.patch("backend.usecases.control_user.AwsEnvironmentModel")
    @mock.patch("backend.usecases.control_user.RoleModel")
    def test_update_user_not_belong_to_tenant(self, mock_role_model, mock_aws_model):
        post_user_data = {
            "email": "test@test.com",
            "name": "test_name",
            "password": "!QAZ2wsx",
            "role": 3,
            "aws_environments": [1,2,3]
        }
        mock_request_user = mock.Mock()
        mock_request_user.is_belong_to_tenant.return_value = False
        mock_user = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).update_user(post_user_data, mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called()
        mock_request_user.can_save_user.assert_not_called()
        mock_user.can_changed_role.assert_not_called()
        mock_user.set_password.assert_not_called()
        mock_request_user.realignment_aws_environments.assert_not_called()
        mock_user.save.assert_not_called()

    # ユーザー更新：他のユーザーを操作できない場合
    @mock.patch("backend.usecases.control_user.AwsEnvironmentModel")
    @mock.patch("backend.usecases.control_user.RoleModel")
    def test_update_user_cant_control_user(self, mock_role_model, mock_aws_model):
        post_user_data = {
            "email": "test@test.com",
            "name": "test_name",
            "password": "!QAZ2wsx",
            "role": 3,
            "aws_environments": [1,2,3]
        }
        mock_request_user = mock.Mock()
        mock_request_user.can_save_user.return_value = False
        mock_user = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).update_user(post_user_data, mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called()
        mock_request_user.can_save_user.assert_called()
        mock_user.can_changed_role.assert_not_called()
        mock_user.set_password.assert_not_called()
        mock_request_user.realignment_aws_environments.assert_not_called()
        mock_user.save.assert_not_called()

    # ユーザー更新：ロールを変更できない場合
    @mock.patch("backend.usecases.control_user.AwsEnvironmentModel")
    @mock.patch("backend.usecases.control_user.RoleModel")
    def test_update_user_cant_change_role(self, mock_role_model, mock_aws_model):
        post_user_data = {
            "email": "test@test.com",
            "name": "test_name",
            "password": "!QAZ2wsx",
            "role": 3,
            "aws_environments": [1,2,3]
        }
        mock_request_user = mock.Mock()
        mock_user = mock.Mock()
        mock_user.can_changed_role.return_value = False

        with self.assertRaises(InvalidRoleException):
            ControlUserUseCase(mock.Mock()).update_user(post_user_data, mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called()
        mock_user.can_changed_role.assert_called_once()
        mock_user.set_password.assert_not_called()
        mock_request_user.realignment_aws_environments.assert_not_called()
        mock_user.save.assert_not_called()

    # ユーザー更新：パスワードが不正な場合
    @mock.patch("backend.usecases.control_user.AwsEnvironmentModel")
    @mock.patch("backend.usecases.control_user.RoleModel")
    def test_update_user_cant_change_role(self, mock_role_model, mock_aws_model):
        post_user_data = {
            "email": "test@test.com",
            "name": "test_name",
            "password": "!QAZ2wsx",
            "role": 3,
            "aws_environments": [1,2,3]
        }
        mock_request_user = mock.Mock()
        mock_user = mock.Mock()
        mock_user.set_password.return_value = False

        with self.assertRaises(InvalidPasswordException):
            ControlUserUseCase(mock.Mock()).update_user(post_user_data, mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called()
        mock_user.can_changed_role.assert_called_once()
        mock_user.set_password.assert_called_once()
        mock_request_user.realignment_aws_environments.assert_not_called()
        mock_user.save.assert_not_called()

    # ユーザー更新：AWS環境を登録できない場合
    @mock.patch("backend.usecases.control_user.AwsEnvironmentModel")
    @mock.patch("backend.usecases.control_user.RoleModel")
    def test_update_user_cant_save_aws(self, mock_role_model, mock_aws_model):
        post_user_data = {
            "email": "test@test.com",
            "name": "test_name",
            "password": "!QAZ2wsx",
            "role": 3,
            "aws_environments": [1,2,3]
        }
        mock_request_user = mock.Mock()
        mock_request_user.realignment_aws_environments.return_value = False
        mock_user = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlUserUseCase(mock.Mock()).update_user(post_user_data, mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called()
        mock_user.can_changed_role.assert_called_once()
        mock_user.set_password.assert_called_once()
        mock_request_user.realignment_aws_environments.assert_called_once()
        mock_user.save.assert_not_called()

    # ユーザー更新：パスワード変更がない場合
    @mock.patch("backend.usecases.control_user.AwsEnvironmentModel")
    @mock.patch("backend.usecases.control_user.RoleModel")
    def test_update_user_not_change_password(self, mock_role_model, mock_aws_model):
        post_user_data = {
            "email": "test@test.com",
            "name": "test_name",
            "password": None,
            "role": 3,
            "aws_environments": [1,2,3]
        }
        mock_request_user = mock.Mock()
        mock_user = mock.Mock()

        res = ControlUserUseCase(mock.Mock()).update_user(post_user_data, mock_request_user, mock_user)

        mock_request_user.is_belong_to_tenant.assert_called_once()
        mock_request_user.can_save_user.assert_called()
        mock_user.can_changed_role.assert_called_once()
        # パスワード変更は呼ばれない
        mock_user.set_password.assert_not_called()
        mock_request_user.realignment_aws_environments.assert_called_once()
        mock_user.save.assert_called_once()
        self.assertEqual(res, mock_user)
