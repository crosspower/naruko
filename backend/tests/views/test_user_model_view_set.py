from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel
from datetime import datetime
from unittest import mock


@mock.patch("backend.views.user_model_view_set.ControlUserUseCase")
class UserModelViewSetTestCase(TestCase):

    api_path_in_tenant = '/api/tenants/{}/users/{}'
    api_path = '/api/users/'

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
        super(UserModelViewSetTestCase, cls).setUpClass()
        cls._create_role_model(RoleModel.MASTER_ID, "test_role")
        # Company1に所属するADMINユーザーの作成
        role_model = cls._create_role_model(RoleModel.ADMIN_ID, "test_role")
        tenant_model1 = cls._create_tenant_model("test_tenant_users_in_tenant_1")
        cls._create_aws_env_model("test_name1", "aws_env1", tenant_model1)
        cls._create_aws_env_model("test_name2", "aws_env2", tenant_model1)

        cls._create_user_model(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model,
        )
        # Company1に所属するUSERユーザーの作成
        role_model_user = cls._create_role_model(RoleModel.USER_ID, "test_role")
        cls._create_user_model(
            email="test_email_USER",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model_user,
        )

        # Company2に所属するユーザーの作成
        tenant_model2 = cls._create_tenant_model("test_tenant_users_in_tenant_2")
        cls._create_aws_env_model("test_name3", "aws_env3", tenant_model2)

        cls._create_user_model(
            email="test_email2",
            name="test_name2",
            password="test_password2",
            tenant=tenant_model2,
            role=role_model,
        )

        cls._create_user_model(
            email="test_email3",
            name="test_name3",
            password="test_password3",
            tenant=tenant_model2,
            role=role_model,
        )

        cls._create_user_model(
            email="test_email4",
            name="test_name4",
            password="test_password4",
            tenant=tenant_model2,
            role=role_model,
        )

    # ログインしていない状態でAPIが使用できないことを確認する
    def test_not_login(self, use_case: mock.Mock):
        client = APIClient()
        response = client.get(self.api_path_in_tenant.format(1, ""), format='json')
        self.assertEqual(response.status_code, 401)

    # ユーザー取得：テナントに紐づくユーザーが取得できることを確認する
    def test_get_users(self, use_case: mock.Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のユーザーを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        response = api_client.get(self.api_path_in_tenant.format(tenant_id, ""), format='json')

        use_case.return_value.fetch_users.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # ユーザー取得：テナントが存在しない場合
    def test_get_users_no_tenant(self, use_case: mock.Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        response = api_client.get(self.api_path_in_tenant.format(-1, ""), format='json')

        use_case.return_value.fetch_users.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # ユーザー削除：テナントに紐づくユーザーが削除できることを確認する
    def test_delete_user(self, use_case: mock.Mock):
        # Company2のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email2"))

        # Company2のユーザーを削除
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_2")
        tenant_id = tenant.id
        user_model = UserModel.objects.filter(tenant=tenant).first()
        user_id = user_model.id
        response = api_client.delete(
            "/api/tenants/{}/users/{}/".format(tenant_id, user_id),
        )

        use_case.return_value.delete_user.assert_called_once()
        self.assertEqual(response.status_code, 204)

    # ユーザー削除：ユーザーが存在しない場合
    def test_delete_user_no_tenant(self, use_case: mock.Mock):
        # Company2のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email2"))

        response = api_client.delete(
            "/api/tenants/{}/users/{}/".format(-1, -1),
        )

        use_case.return_value.delete_user.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # テナントに紐づくユーザーを作成できることを確認する
    @mock.patch('backend.views.user_model_view_set.UserModelDetailSerializer')
    def test_create_user(self, mock_serializer, use_case: mock.Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のユーザーを作成
        user_name = "postman"
        user_password = "!QAZ2wsx"
        user_email = "post@post.com"

        tenant_model = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant_model.id

        aws_models = AwsEnvironmentModel.objects.filter(tenant=tenant_model)
        aws_ids = [aws.id for aws in aws_models]

        create_user = use_case.return_value.create_user
        create_user.return_value = UserModel()

        mock_serializer.return_value.data = "TEST"

        response = api_client.post(
            path=self.api_path_in_tenant.format(tenant_id, ""),
            data={
                "email": user_email,
                "name": user_name,
                "password": user_password,
                "role": RoleModel.USER_ID,
                "aws_environments": aws_ids
            },
            format='json'
        )

        # ステータスコードの確認
        create_user.assert_called_once()
        self.assertEqual(response.status_code, 201)

    # リクエストデータが不正な場合ユーザーが作成できないことを確認する
    def test_denied_create_user_for_bad_request(self, use_case: mock.Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のユーザーを作成
        user_email = "post@post.com"

        tenant_model = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant_model.id

        response = api_client.post(
            path=self.api_path_in_tenant.format(tenant_id, ""),
            data="Bad Request",
            format='json'
        )

        # ステータスコードの確認
        self.assertEqual(response.status_code, 400)
        # DBの確認
        with self.assertRaises(UserModel.DoesNotExist):
            UserModel.objects.get(email=user_email)

    # テナントに紐づくユーザーを更新できることを確認する
    def test_update_user(self, use_case: mock.Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のユーザーを更新
        user = UserModel.objects.get(email="test_email_USER")
        user_id = user.id
        tenant_id = user.tenant.id

        user_name = "putman"
        user_password = "!QAZ2wsx"
        user_email = "put@put.com"

        aws_models = AwsEnvironmentModel.objects.filter(tenant=user.tenant)
        aws_ids = [aws.id for aws in aws_models]

        update_user = use_case.return_value.update_user
        update_user.return_value = UserModel(id=100)

        response = api_client.put(
            path=self.api_path_in_tenant.format(tenant_id, user_id) + "/",
            data={
                "email": user_email,
                "name": user_name,
                "password": user_password,
                "role": RoleModel.USER_ID,
                "aws_environments": aws_ids
            },
            format='json'
        )

        use_case.return_value.update_user.assert_called_once()
        # ステータスコードの確認
        self.assertEqual(response.status_code, 200)

    # ユーザーが存在しない場合
    def test_update_user_no_user(self, use_case: mock.Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のユーザーを更新
        user = UserModel.objects.get(email="test_email_USER")

        user_name = "putman"
        user_password = "!QAZ2wsx"
        user_email = "put@put.com"

        aws_models = AwsEnvironmentModel.objects.filter(tenant=user.tenant)
        aws_ids = [aws.id for aws in aws_models]

        update_user = use_case.return_value.update_user
        update_user.return_value = UserModel(id=100)

        response = api_client.put(
            path=self.api_path_in_tenant.format(-100, -100) + "/",
            data={
                "email": user_email,
                "name": user_name,
                "password": user_password,
                "role": RoleModel.USER_ID,
                "aws_environments": aws_ids
            },
            format='json'
        )

        use_case.return_value.update_user.assert_not_called()
        # ステータスコードの確認
        self.assertEqual(response.status_code, 404)

    # リクエストデータが不正な場合ユーザーが作成できないことを確認する
    def test_denied_update_user_for_bad_request(self, use_case: mock.Mock):
        # Company1のユーザーで認証
        api_client = APIClient()
        api_client.force_authenticate(user=UserModel.objects.get(email="test_email"))

        # Company1のユーザーを更新
        user = UserModel.objects.get(email="test_email_USER")
        user_id = user.id
        tenant_id = user.tenant.id

        user_email = "put@put.com"

        aws_models = AwsEnvironmentModel.objects.filter(tenant=user.tenant)

        response = api_client.put(
            path=self.api_path_in_tenant.format(tenant_id, user_id) + "/",
            data="Bad Request",
            format='json'
        )

        use_case.return_value.update_user.assert_not_called()
        # ステータスコードの確認
        self.assertEqual(response.status_code, 400)
