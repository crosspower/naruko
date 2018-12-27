from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel, NotificationGroupModel,\
    EmailDestination, NotificationDestinationModel
from datetime import datetime
from unittest import mock


@mock.patch('backend.views.notification_group_view_set.ControlNotificationUseCase')
class NotificationGroupTestCase(TestCase):

    api_path = '/api/tenants/{}/notification-groups/'
    api_path_detail = '/api/tenants/{}/notification-groups/{}/'

    @staticmethod
    def _create_group(name, tenant):
        now = datetime.now()
        objects_create = NotificationGroupModel.objects.create(
            name=name,
            tenant=tenant,
            created_at=now,
            updated_at=now
        )
        objects_create.save()
        return objects_create

    @staticmethod
    def _create_dest(name, address, tenant):
        now = datetime.now()
        objects_create = EmailDestination.objects.create(
            name=name,
            address=address,
            tenant=tenant,
            created_at=now,
            updated_at=now
        )
        objects_create.save()
        return objects_create

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
        super(NotificationGroupTestCase, cls).setUpClass()
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

        # Company1の通知先の作成
        cls._create_dest("test_dest", "test@test.com", tenant_model1)
        cls._create_group("test_group", tenant_model1)

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

    def test_not_login(self, use_case):
        client = APIClient()
        # 検証対象の実行
        response = client.get(self.api_path.format(1), format='json')
        self.assertEqual(response.status_code, 401)

    # 通知グループ取得：正常系
    def test_fetch_groups(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant.id

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id),
            format='json'
        )

        use_case.assert_called_once()
        use_case.return_value.fetch_groups.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # 通知グループ取得：テナントが存在しない場合
    def test_fetch_groups_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(999),
            format='json'
        )

        use_case.assert_not_called()
        use_case.return_value.fetch_groups.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # 通知グループ作成：正常系
    def test_create_group(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant.id

        # AWSのIDを取得
        aws_all = AwsEnvironmentModel.objects.all()
        aws_ids = [aws.id for aws in aws_all]

        # 通知先のIDを取得
        destination_model_all = NotificationDestinationModel.all()
        dest_ids = [dest.id for dest in destination_model_all]

        # mock準備
        save_group = use_case.return_value.save_group
        save_group.return_value = NotificationGroupModel(
            name="test_group",
            tenant=tenant
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id),
            data={
                "name": "test_group",
                "aws_environments": aws_ids,
                "destinations": dest_ids
            },
            format='json'
        )

        use_case.assert_called_once()
        self.assertEqual(response.status_code, 201)

    # 通知グループ作成：不正なリクエストの場合
    def test_create_group_invalid_params(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant.id

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id),
            data={
            },
            format='json'
        )

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 400)

    # 通知グループ作成：通知先、AWSがなくても作成できることを確認する
    def test_create_group_no_aws_no_dest(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant.id

        # mock準備
        save_group = use_case.return_value.save_group
        save_group.return_value = NotificationGroupModel(
            name="test_group",
            tenant=tenant
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id),
            data={
                "name": "test_group",
                "aws_environments": [],
                "destinations": []
            },
            format='json'
        )

        use_case.assert_called_once()
        self.assertEqual(response.status_code, 201)

    # 通知グループ作成：テナントが存在しない場合
    def test_create_group_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(999),
            data={
                "name": "test_group",
                "aws_environments": [],
                "destinations": []
            },
            format='json'
        )

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 400)

    # 通知グループ削除：正常系
    def test_destroy_group(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant.id

        # Group1のIDを取得
        notification_group_model = NotificationGroupModel.objects.get(name="test_group")
        group_id = notification_group_model.id

        # 検証対象の実行
        response = client.delete(
            path=self.api_path_detail.format(tenant_id, group_id),
            format='json'
        )

        use_case.assert_called_once()
        self.assertEqual(response.status_code, 204)

    # 通知グループ削除：削除対象が存在しない場合
    def test_destroy_group_no_group(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # 検証対象の実行
        response = client.delete(
            path=self.api_path_detail.format(999, 999),
            format='json'
        )

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # 通知グループ更新：正常系
    def test_update_group(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant.id

        # Group1のIDを取得
        notification_group_model = NotificationGroupModel.objects.get(name="test_group")
        group_id = notification_group_model.id

        # AWSのIDを取得
        aws_all = AwsEnvironmentModel.objects.all()
        aws_ids = [aws.id for aws in aws_all]

        # 通知先のIDを取得
        destination_model_all = NotificationDestinationModel.all()
        dest_ids = [dest.id for dest in destination_model_all]

        # mock準備
        save_group = use_case.return_value.save_group
        save_group.return_value = NotificationGroupModel(
            name="test_group",
            tenant=tenant
        )

        # 検証対象の実行
        response = client.put(
            path=self.api_path_detail.format(tenant_id, group_id),
            data={
                "name": "test_group",
                "aws_environments": aws_ids,
                "destinations": dest_ids
            },
            format='json'
        )

        use_case.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # 通知グループ更新：通知先、AWSがなくても作成できることを確認する
    def test_update_group_no_aws_no_dest(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        tenant_id = tenant.id

        # Group1のIDを取得
        notification_group_model = NotificationGroupModel.objects.get(name="test_group")
        group_id = notification_group_model.id

        # mock準備
        save_group = use_case.return_value.save_group
        save_group.return_value = NotificationGroupModel(
            name="test_group",
            tenant=tenant
        )

        # 検証対象の実行
        response = client.put(
            path=self.api_path_detail.format(tenant_id, group_id),
            data={
                "name": "test_group",
                "aws_environments": [],
                "destinations": []
            },
            format='json'
        )

        use_case.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # 通知グループ作成：削除対象が存在しない場合
    def test_update_group_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # 検証対象の実行
        response = client.put(
            path=self.api_path_detail.format(999, 999),
            data={
                "name": "test_group",
                "aws_environments": [],
                "destinations": []
            },
            format='json'
        )

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 404)
