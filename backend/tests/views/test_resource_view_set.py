from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel, Resource
from datetime import datetime
from unittest import mock


@mock.patch("backend.views.resource_view_set.ControlResourceUseCase")
class InstanceViewSetTestCase(TestCase):

    api_path_in_tenant = '/api/tenants/{}/aws-environments/{}/resources/{}'
    api_path = '/api/tenants/{}/aws-environments/{}' \
               '/regions/ap-northeast-1/services/ec2/resources/i-123456789012/'

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
        super(InstanceViewSetTestCase, cls).setUpClass()
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
        response = client.get(self.api_path_in_tenant.format(1, 1, "?region=test"), format='json')
        self.assertEqual(response.status_code, 401)

    # 正常系
    def test_get_resource(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        fetch_resources = use_case.return_value.fetch_resources
        fetch_resources.return_value = {}

        # 検証対象の実行
        response = client.get(
            path=self.api_path_in_tenant.format(tenant_id, aws_id, "?region=test"),
            format='json')

        fetch_resources.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # テナントが存在しない場合
    def test_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        fetch_resources = use_case.return_value.fetch_resources
        fetch_resources.return_value = {}

        # 検証対象の実行
        response = client.get(
            path=self.api_path_in_tenant.format(100, aws_id, "?region=test"),
            format='json')

        fetch_resources.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # AWS環境が存在しない場合
    def test_no_aws_env(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        fetch_resources = use_case.return_value.fetch_resources
        fetch_resources.return_value = {}

        # 検証対象の実行
        response = client.get(
            path=self.api_path_in_tenant.format(tenant_id, 100, "?region=test"),
            format='json')

        fetch_resources.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース起動：正常系
    def test_start_resource(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        start_resource = use_case.return_value.start_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id) + "start/",
            format='json')

        start_resource.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # リソース起動：テナントが存在しない場合
    def test_start_resource_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        start_resource = use_case.return_value.start_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(100, aws_id) + "start/",
            format='json')

        start_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース起動：AWS環境が存在しない場合
    def test_start_resource_no_aws(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        start_resource = use_case.return_value.start_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, 100) + "start/",
            format='json')

        start_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース再起動：正常系
    def test_reboot_resource(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        reboot_resource = use_case.return_value.reboot_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id) + "reboot/",
            format='json')

        reboot_resource.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # リソース再起動：テナントが存在しない場合
    def test_reboot_resource_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        reboot_resource = use_case.return_value.reboot_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(100, aws_id) + "reboot/",
            format='json')

        reboot_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース再起動：AWS環境が存在しない場合
    def test_reboot_resource_no_aws(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        reboot_resource = use_case.return_value.reboot_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, 100) + "reboot/",
            format='json')

        reboot_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース再起動：正常系
    def test_stop_resource(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        stop_resource = use_case.return_value.stop_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id) + "stop/",
            format='json')

        stop_resource.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # リソース再起動：テナントが存在しない場合
    def test_stop_resource_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        stop_resource = use_case.return_value.stop_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(100, aws_id) + "stop/",
            format='json')

        stop_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース再起動：AWS環境が存在しない場合
    def test_stop_resource_no_aws(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        stop_resource = use_case.return_value.stop_resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, 100) + "stop/",
            format='json')

        stop_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース詳細取得：正常系
    def test_retrieve_resource(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        describe_resource = use_case.return_value.describe_resource
        mock_resource = mock.Mock()
        mock_resource.serialize.return_value = "TEST"
        describe_resource.return_value = mock_resource

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, aws_id),
            format='json')

        describe_resource.assert_called_once()
        mock_resource.serialize.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # リソース詳細取得：テナントが存在しない場合
    def test_retrieve_resource_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        describe_resource = use_case.return_value.describe_resource

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(100, aws_id),
            format='json')

        describe_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソース詳細取得：AWS環境が存在しない場合
    def test_retrieve_resource_no_aws(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        describe_resource = use_case.return_value.describe_resource

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, 100),
            format='json')

        describe_resource.assert_not_called()
        self.assertEqual(response.status_code, 404)
