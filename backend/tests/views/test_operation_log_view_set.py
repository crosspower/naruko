from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import OperationLogModel, AwsEnvironmentModel, TenantModel, UserModel, RoleModel
from datetime import datetime
from unittest.mock import patch, Mock


@patch("backend.views.operation_log_model_view_set.ControlOperationLog")
class OperationLogModelViewSetTestCase(TestCase):
    api_path = '/api/tenants/{}/logs/{}'

    @staticmethod
    def _create_aws_env_model(name, aws_account_id, tenant):
        now = datetime.now()
        AwsEnvironmentModel.objects.create(
            name=name,
            aws_account_id=aws_account_id,
            aws_role="test_role",
            aws_external_id="test_external_id",
            tenant=tenant,
            created_at=now,
            updated_at=now
        ).save()

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
        super(OperationLogModelViewSetTestCase, cls).setUpClass()
        # Company1に所属するMASTERユーザーの作成
        role_model = cls._create_role_model(2, "test_role")
        tenant_model1 = cls._create_tenant_model("test_tenant_users_in_tenant_1")

        cls._create_user_model(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model,
        )
        # Company1に所属するUSERユーザーの作成
        role_model_user = cls._create_role_model(3, "test_role")
        cls._create_user_model(
            email="test_email_USER",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model_user,
        )

        # Company1に所属するAWS環境の作成
        cls._create_aws_env_model("test_name1", "test_aws1", tenant_model1)

        # Company2に所属するユーザーの作成
        tenant_model2 = cls._create_tenant_model("test_tenant_users_in_tenant_2")

        cls._create_user_model(
            email="test_email2",
            name="test_name2",
            password="test_password2",
            tenant=tenant_model2,
            role=role_model,
        )

        # Company2に所属するAWS環境の作成
        cls._create_aws_env_model("test_name2", "test_aws2", tenant_model2)

    # ログインしていない状態でAPIが使用できないことを確認する
    def test_not_login(self, use_case: Mock):
        client = APIClient()
        response = client.get(self.api_path.format(1, ""), format='json')
        self.assertEqual(response.status_code, 401)

    # 正常系
    def test_get_logs(self, use_case: Mock):
        # Tenant1のユーザーで認証
        api_client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        api_client.force_authenticate(user=user_model)

        fetch_logs = use_case.return_value.fetch_logs
        fetch_logs.return_value = [OperationLogModel(
            executor=user_model,
            tenant=user_model.tenant,
            operation="TEST",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )]

        response = api_client.get(
            self.api_path.format(user_model.tenant.id, ""),
            format='json'
        )

        fetch_logs.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # テナントが存在しない場合
    def test_get_logs_no_tenant(self, use_case: Mock):
        # Tenant1のユーザーで認証
        api_client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        api_client.force_authenticate(user=user_model)

        fetch_logs = use_case.return_value.fetch_logs
        fetch_logs.return_value = [OperationLogModel(
            executor=user_model,
            tenant=user_model.tenant,
            operation="TEST",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )]

        response = api_client.get(
            self.api_path.format(-1, ""),
            format='json'
        )

        fetch_logs.assert_not_called()
        self.assertEqual(response.status_code, 404)
