from django.test import TestCase
from django.test.utils import override_settings
from backend.models import TenantModel, RoleModel, UserModel
from datetime import datetime
from unittest import mock
from backend.usecases.reset_password import ResetPasswordUseCase
from botocore.exceptions import ClientError
from backend.exceptions import InvalidEmailException


@mock.patch('backend.usecases.reset_password.Ses')
class ResetPasswordUseCaseTestCase(TestCase):

    @staticmethod
    def _create_role_model(id, role_name):
        now = datetime.now()
        return RoleModel.objects.create(
            id=id,
            role_name=role_name,
            created_at=now,
            updated_at=now
        )

    @staticmethod
    def _create_tenant_model(tenant_name):
        now = datetime.now()
        return TenantModel.objects.create(
            tenant_name=tenant_name,
            created_at=now,
            updated_at=now
        )

    @staticmethod
    def _create_user_model(email, name, password, tenant, role):
        now = datetime.now()
        user_model = UserModel(
            email=email,
            name=name,
            password=password,
            tenant=tenant,
            role=role,
            created_at=now,
            updated_at=now
        )
        user_model.save()
        return user_model

    @classmethod
    def setUpClass(cls):
        super(ResetPasswordUseCaseTestCase, cls).setUpClass()
        # Company1に所属するユーザーの作成
        role_model = cls._create_role_model(2, "test_role")
        tenant_model1 = cls._create_tenant_model("test_tenant_users_in_tenant_1")

        cls._create_user_model(
            email="test_email@email.com",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model,
        )

        cls._create_user_model(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model,
        )

    # 正常系
    @override_settings(SES_ADDRESS="SES_ADDRESS")
    def test_reset_password(self, mock_ses):
        mock_user = mock.Mock(spec=UserModel)

        # 検証対象実行
        response = ResetPasswordUseCase(mock.Mock()).reset_password(mock_user)

        # 呼び出し確認
        mock_user.reset_password.assert_called_once()
        mock_user.save.assert_called_once()

        ses_return_value = mock_ses.return_value
        ses_return_value.send_password_reset_mail.assert_called_with(
            mock_user.email,
            mock_user.reset_password.return_value
        )
        self.assertEqual(response, mock_user)

    # メール送信時にエラーだった場合、例外が送出されることを確認する
    @override_settings(SES_ADDRESS="SES_ADDRESS")
    def test_raise_invalid_email_exception(self, mock_ses):
        mock_user = mock.Mock(spec=UserModel)

        ses_return_value = mock_ses.return_value
        ses_return_value.send_password_reset_mail.side_effect = ClientError({}, "")

        # 検証対象実行
        with self.assertRaises(InvalidEmailException):
            ResetPasswordUseCase(mock.Mock()).reset_password(mock_user)

        # 呼び出し確認
        mock_user.reset_password.assert_called_once()
        mock_user.save.assert_called_once()
        ses_return_value.send_password_reset_mail.assert_called_with(
            mock_user.email,
            mock_user.reset_password.return_value
        )
