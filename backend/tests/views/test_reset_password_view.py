from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import TenantModel, RoleModel, UserModel
from datetime import datetime
from unittest import mock


@mock.patch('backend.views.reset_password_view.ResetPasswordUseCase.reset_password')
class ResetPasswordViewTestCase(TestCase):

    api_path = "/api/auth/reset/"

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
        super(ResetPasswordViewTestCase, cls).setUpClass()
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

    # 認証せずに使用できることを確認する
    def test_reset_password_not_auth(self, use_case):
        client = APIClient()

        user_model = UserModel.objects.get(email="test_email@email.com")
        use_case.return_value = user_model

        data = {"email": "test_email@email.com"}
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        use_case.assert_called_once_with(user_model)
        self.assertEqual(response.status_code, 200)

    # リクエストが不正な場合
    def test_bad_request(self, use_case):
        client = APIClient()

        data = {}
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 400)

    # ユーザーが存在しない場合
    def test_no_user(self, use_case):
        client = APIClient()

        user_model = UserModel.objects.get(email="test_email@email.com")
        use_case.return_value = user_model

        data = {"email": "no_user"}
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # シリアライザーのバリデーションを通らなかった場合
    def test_serializer_is_not_valid(self, use_case):
        client = APIClient()

        user_model = UserModel.objects.get(email="test_email@email.com")
        use_case.return_value = user_model

        data = {"email": "test_email"}
        response = client.post(
            path=self.api_path,
            data=data,
            format="json"
        )

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 400)
