from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import AwsEnvironmentModel, TenantModel, RoleModel, UserModel
from datetime import datetime
from unittest.mock import patch, Mock


@patch("backend.views.aws_model_view_set.ControlAwsEnvironment")
class AwsEnvironmentModelViewSetTestCase(TestCase):
    api_path_in_tenant = '/api/tenants/{}/aws-environments/{}'

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
        super(AwsEnvironmentModelViewSetTestCase, cls).setUpClass()
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
        response = client.get(self.api_path_in_tenant.format(1, ""), format='json')
        self.assertEqual(response.status_code, 401)

    # テナントに紐づくAWS環境が取得できることを確認する
    @patch("backend.views.aws_model_view_set.AwsEnvironmentModelGetDetailSerializer")
    def test_get_aws_envs(self, mock_serializer, use_case: Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のAWSを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        fetch_aws_environments = use_case.return_value.fetch_aws_environments
        fetch_aws_environments.return_value = [AwsEnvironmentModel()]
        mock_serializer.return_value.data = "TEST"

        response = api_client.get(self.api_path_in_tenant.format(tenant_id, ""), format='json')

        self.assertEqual(response.status_code, 200)

    # テナントが存在しない場合
    @patch("backend.views.aws_model_view_set.AwsEnvironmentModelGetDetailSerializer")
    def test_get_aws_envs_no_tenant(self, mock_serializer, use_case: Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        fetch_aws_environments = use_case.return_value.fetch_aws_environments
        fetch_aws_environments.return_value = [AwsEnvironmentModel()]
        mock_serializer.return_value.data = "TEST"

        response = api_client.get(self.api_path_in_tenant.format(-1, ""), format='json')

        self.assertEqual(response.status_code, 404)

    # ログインしていない状態でAPIが使用できないことを確認する
    def test_create_not_login(self, use_case):
        client = APIClient()
        response = client.post(self.api_path_in_tenant.format(1, ""), format='json')
        self.assertEqual(response.status_code, 401)

    @patch('backend.views.aws_model_view_set.AwsEnvironmentModelCreateSerializer')
    @patch('backend.views.aws_model_view_set.AwsEnvironmentModelGetDetailSerializer')
    def test_create_aws_env(self, get_serializer_mock, create_serializer_mock, usecase_mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # リクエストデータ
        data = dict(aws_account_id=1234567890, aws_external_id='external id', aws_role='role name', name='account name')

        # 実際にシリアライズされるデータ
        serialize_data = dict(**data, tenant=str(tenant_id))

        # 取得用のシリアライザーの戻り値
        get_serializer_mock.return_value.data = dict(aws_account_id=1234567890, aws_role='role name',
                                                     name='account name')

        response = api_client.post(self.api_path_in_tenant.format(tenant_id, ""), data=data, format='json')

        create_serializer_mock.assert_called_once_with(data=serialize_data)
        create_serializer_mock.return_value.is_valid.assert_called_once_with(raise_exception=True)
        create_serializer_mock.return_value.save.assert_called_once()
        usecase_mock.return_value.save_aws_environment.assert_called_once_with(
            UserModel.objects.get(email="test_email"),
            create_serializer_mock.return_value.save.return_value)

        self.assertEqual(response.status_code, 201)

    # ログインしていない状態でAPIが使用できないことを確認する
    def test_update_not_login(self, use_case):
        client = APIClient()
        response = client.put(
            self.api_path_in_tenant.format(1, str(1) + '/'),
            format='json')
        self.assertEqual(response.status_code, 401)

    @patch('backend.views.aws_model_view_set.AwsEnvironmentModelUpdateSerializer')
    @patch('backend.views.aws_model_view_set.AwsEnvironmentModelGetDetailSerializer')
    def test_update_aws_env(self, get_serializer_mock, update_serializer_mock, usecase_mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # リクエストデータ
        data = dict(name='account name')

        # 取得用のシリアライザーの戻り値
        get_serializer_mock.return_value.data = dict(aws_account_id=1234567890, aws_role='role name',
                                                     name='account name')

        # Company1のAWSアカウントを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        aws_env_model = AwsEnvironmentModel.objects.get(name="test_name1")
        aws_env_id = aws_env_model.id

        response = api_client.put(self.api_path_in_tenant.format(tenant_id, str(aws_env_id) + '/'), data=data,
                                  format='json')

        update_serializer_mock.assert_called_once_with(data=data, instance=aws_env_model, partial=True)
        update_serializer_mock.return_value.is_valid.assert_called_once_with(raise_exception=True)
        update_serializer_mock.return_value.save.assert_called_once()
        usecase_mock.return_value.save_aws_environment.assert_called_once_with(
            UserModel.objects.get(email="test_email"),
            update_serializer_mock.return_value.save.return_value)

        self.assertEqual(response.status_code, 200)

    # AWS更新：AWSが見つからない場合
    @patch('backend.views.aws_model_view_set.AwsEnvironmentModelUpdateSerializer')
    @patch('backend.views.aws_model_view_set.AwsEnvironmentModelGetDetailSerializer')
    def test_update_aws_env_no_aws(self, get_serializer_mock, update_serializer_mock, usecase_mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # リクエストデータ
        data = dict(name='account name')

        response = api_client.put(self.api_path_in_tenant.format(-1, str(-1) + '/'), data=data,
                                  format='json')

        update_serializer_mock.assert_not_called()
        update_serializer_mock.return_value.is_valid.assert_not_called()
        update_serializer_mock.return_value.save.assert_not_called()
        usecase_mock.return_value.save_aws_environment.assert_not_called()

        self.assertEqual(response.status_code, 404)

    # ログインしていない状態でAPIが使用できないことを確認する
    def test_delete_not_login(self, use_case):
        client = APIClient()
        response = client.delete(
            self.api_path_in_tenant.format(1, str(1) + '/'),
            format='json')
        self.assertEqual(response.status_code, 401)

    @patch('backend.views.aws_model_view_set.AwsEnvironmentModel')
    def test_delete_aws_env(self, model_mock, usecase_mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のAWSアカウントを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        aws_env_model = AwsEnvironmentModel.objects.get(name="test_name1")
        aws_env_id = aws_env_model.id

        response = api_client.delete(self.api_path_in_tenant.format(tenant_id, str(aws_env_id) + '/'), format='json')

        model_mock.objects.get.assert_called_once_with(id=str(aws_env_id), tenant_id=str(tenant_id))
        usecase_mock.return_value.delete_aws_environment.assert_called_once_with(
            UserModel.objects.get(email="test_email"),
            model_mock.objects.get.return_value)

        self.assertEqual(response.status_code, 204)

    # AWS削除：AWSが見つからない場合
    def test_delete_aws_env_no_aws(self, usecase_mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        response = api_client.delete(self.api_path_in_tenant.format(str(-1), str(-1) + '/'), format='json')

        usecase_mock.return_value.delete_aws_environment.assert_not_called()

        self.assertEqual(response.status_code, 404)
