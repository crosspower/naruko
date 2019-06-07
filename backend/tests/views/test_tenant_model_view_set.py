from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel
from datetime import datetime
from unittest import mock


@mock.patch("backend.views.tenant_model_view_set.ControlTenantUseCase")
class TenantModelViewSetTestCase(TestCase):
    api_path_in_tenant = '/api/tenants/'
    api_path_in_tenant_pk = '/api/tenants/{}/'

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
        super(TenantModelViewSetTestCase, cls).setUpClass()

        # Company1作成
        tenant_model1 = cls._create_tenant_model("test_tenant_users_in_tenant_1")
        cls._create_aws_env_model("test_name1", "aws_env1", tenant_model1)
        cls._create_aws_env_model("test_name2", "aws_env2", tenant_model1)

        # Company1に所属するMASTERユーザーの作成
        role_model_master = cls._create_role_model(RoleModel.MASTER_ID, "MASTER")
        cls._create_user_model(
            email="master_email",
            name="master_name",
            password="master_password",
            tenant=tenant_model1,
            role=role_model_master,
        )
        # Company1に所属するADMINユーザーの作成
        role_model_admin = cls._create_role_model(RoleModel.ADMIN_ID, "ADMIN")
        cls._create_user_model(
            email="admin_email",
            name="admin_name",
            password="admin_password",
            tenant=tenant_model1,
            role=role_model_admin,
        )

        # Company1に所属するUSERユーザーの作成
        role_model_user = cls._create_role_model(RoleModel.USER_ID, "USER")
        cls._create_user_model(
            email="user_email",
            name="user_name",
            password="user_password",
            tenant=tenant_model1,
            role=role_model_user,
        )

    # ログインしていない状態でAPIが使用できないことを確認する
    def test_not_login(self, usecase):
        client = APIClient()
        response = client.get(self.api_path_in_tenant, format='json')
        self.assertEqual(response.status_code, 401)

    # テナントの情報にアクセスできることを確認する
    def test_get_tenants(self, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))

        # Company1の情報を取得
        response = api_client.get(self.api_path_in_tenant, format='json')

        self.assertEqual(response.status_code, 200)

    # テナントが削除できることを確認する
    def test_delete_tenant(self, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))

        # Company1を削除
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        response = api_client.delete(self.api_path_in_tenant_pk.format(tenant_id), format='json')

        self.assertEqual(response.status_code, 204)

    # 存在しないテナントを削除できないことを確認する
    def test_delete_tenant_not_found(self, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))

        response = api_client.delete(self.api_path_in_tenant_pk.format(-1), format='json')

        self.assertEqual(response.status_code, 404)

    # 不正なIDでテナントを削除できないことを確認する
    def test_delete_tenant_invalid_pk(self, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))

        response = api_client.delete(self.api_path_in_tenant_pk.format("invalid"), format='json')

        self.assertEqual(response.status_code, 400)

    # テナントを作成できることを確認する
    @mock.patch("backend.views.tenant_model_view_set.UserModelDetailSerializer")
    @mock.patch("backend.views.tenant_model_view_set.TenantModelDetailSerializer")
    def test_create_tenant_master(self, tenant_serializer, user_serializer, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))

        # 作成するテナント
        data = dict(
            tenant=dict(tenant_name='test_tenant', email='test@test.com', tel='03-1234-1234'),
            user=dict(name="test_user", email="test@test.com")
        )
        usecase.return_value.create_tenant.return_value = (
            TenantModel(
                tenant_name="test_tenant",
                email="test@test.com",
                tel='03-1234-1234'
            ),
            UserModel(
                email="test@test.com",
                name="test_user"
            )
        )
        usecase.return_value.create_tenant.return_value = (mock.Mock(spec=TenantModel), mock.Mock(spec=UserModel))
        tenant_serializer.return_value.data = "TEST"
        user_serializer.return_value.data = "TEST"

        # Company1の情報を取得
        response = api_client.post(self.api_path_in_tenant, data=data, format='json')

        self.assertEqual(response.status_code, 201)

    # テナントが更新できることを確認する
    def test_update_tenant(self, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))
        # mock作成
        data = dict(tenant_name='updated', email='test@test.com', tel='03-1234-1234')
        update_tenant = usecase.return_value.update_tenant
        update_tenant.return_value = data

        # Company1を更新
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        response = api_client.put(
            self.api_path_in_tenant_pk.format(tenant_id),
            data=data,
            format='json')

        self.assertEqual(response.status_code, 200)
        update_tenant.assert_called()

    # 存在しないテナントは更新できないことを確認する
    def test_update_tenant_not_exist(self, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))
        # mock作成
        data = dict(tenant_name='updated', email='test@test.com', tel='03-1234-1234')
        update_tenant = usecase.return_value.update_tenant
        update_tenant.return_value = data

        # Company1を更新
        response = api_client.put(
            self.api_path_in_tenant_pk.format(-1),
            data=data,
            format='json')

        self.assertEqual(response.status_code, 404)
        update_tenant.assert_not_called()

    # 不正なIDでテナントが更新できないことを確認する
    def test_update_tenant_invalid(self, usecase):
        # MASTERユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="master_email"))
        # mock作成
        data = dict(tenant_name='updated', email='test@test.com', tel='03-1234-1234')
        update_tenant = usecase.return_value.update_tenant
        update_tenant.return_value = data

        # Company1を更新
        response = api_client.put(
            self.api_path_in_tenant_pk.format("invalid"),
            data=data,
            format='json')

        self.assertEqual(response.status_code, 400)
        update_tenant.assert_not_called()
