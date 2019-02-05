from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel, Document
from datetime import datetime
from unittest import mock


@mock.patch('backend.views.document_model_view_set.ControlResourceUseCase')
class DocumentViewSetTestCase(TestCase):

    api_path = '/api/tenants/{}/aws-environments/{}/regions/ap-northeast-1/documents/{}'

    @staticmethod
    def _create_aws_env_model(name, aws_account_id, tenant):
        now = datetime.now()
        aws = AwsEnvironmentModel.objects.create(
            name=name,
            aws_account_id=aws_account_id,
            aws_role="test_role",
            aws_external_id="test_external_id",
            tenant=tenant,
            created_at=now,
            updated_at=now
        )
        aws.save()
        return aws

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
            updated_at=now,
        )
        user_model.save()
        return user_model

    @classmethod
    def setUpClass(cls):
        super(DocumentViewSetTestCase, cls).setUpClass()
        # Company1に所属するMASTERユーザーの作成
        role_model = cls._create_role_model(2, "test_role")
        tenant_model1 = cls._create_tenant_model("test_tenant_users_in_tenant_1")
        # Company1に所属するAWS環境の作成
        aws1 = cls._create_aws_env_model("test_name1", "test_aws1", tenant_model1)

        user1 = cls._create_user_model(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model,
        )
        user1.aws_environments.add(aws1)
        # Company1に所属するUSERユーザーの作成
        role_model_user = cls._create_role_model(3, "test_role")
        user2 = cls._create_user_model(
            email="test_email_USER",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model_user,
        )
        user2.aws_environments.add(aws1)

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
    def test_not_login(self, use_case):
        client = APIClient()
        # 検証対象の実行
        response = client.get(self.api_path.format(1, 1, ""), format='json')
        self.assertEqual(response.status_code, 401)

    # 正常系
    def test_list_documents(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        fetch_documents = use_case.return_value.fetch_documents
        fetch_documents.return_value = []

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, aws_id, ""),
            format='json')

        fetch_documents.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # AWS環境が存在しない場合
    def test_list_documents_no_aws_env(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        fetch_documents = use_case.return_value.fetch_documents
        fetch_documents.return_value = []

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(-1, -1, ""),
            format='json')

        fetch_documents.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # 正常系
    def test_get_document(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        describe_document = use_case.return_value.describe_document
        describe_document.return_value = Document(name="test", parameters=[])

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, aws_id, "test/"),
            format='json')

        describe_document.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # AWSの環境が存在しない場合
    def test_get_document_no_aws_env(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        describe_document = use_case.return_value.describe_document
        describe_document.return_value = Document(name="test", parameters=[])

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(-1, -1, "test/"),
            format='json')

        describe_document.assert_not_called()
        self.assertEqual(response.status_code, 404)
