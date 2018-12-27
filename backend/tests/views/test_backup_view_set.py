from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel
from backend.models.resource.ec2 import AmiImage
from backend.models.resource.rds import Snapshot
from datetime import datetime
from unittest import mock


@mock.patch("backend.views.backup_view_set.ControlResourceUseCase")
class BackupViewSetTestCase(TestCase):

    api_path = '/api/tenants/{}/aws-environments/{}' \
               '/regions/ap-northeast-1/services/ec2/resources/i-123456789012/backups/'

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
        super(BackupViewSetTestCase, cls).setUpClass()
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
        response = client.post(self.api_path.format(1, 1), format='json')
        self.assertEqual(response.status_code, 401)

    # リソースバックアップ取得：正常系
    def test_list_backup_resource(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        fetch_backups = use_case.return_value.fetch_backups
        d = datetime(2018, 12, 1, 0, 0, 0)
        fetch_backups.return_value = [
            AmiImage(
                image_id="TEST_EC2",
                name="TEST",
                state="available",
                created_at="2018-12-01T00:00:00.000Z"),
            Snapshot(
                snapshot_id="TEST_RDS",
                state="available",
                created_at=d
            )
        ]

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, aws_id),
            format='json')

        fetch_backups.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [
            {
                "id": "TEST_EC2",
                "name": "TEST",
                "state": "available",
                "created_at": "2018-12-01T00:00:00.000Z"
            },
            {
                "id": "TEST_RDS",
                "state": "available",
                "created_at": d
            },
        ])

    # リソースバックアップ取得：テナントが存在しない場合
    def test_list_backup_resource_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        fetch_backups = use_case.return_value.fetch_backups

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(100, aws_id),
            format='json')

        fetch_backups.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソースバックアップ取得：AWS環境が存在しない場合
    def test_list_backup_resource_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        fetch_backups = use_case.return_value.fetch_backups

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, 100),
            format='json')

        fetch_backups.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソースバックアップ作成：正常系
    def test_backup_resource(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        create_backup = use_case.return_value.create_backup
        create_backup.return_value = "TEST"

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id),
            data={"no_reboot": True},
            format='json')

        create_backup.assert_called_once()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["backup_id"], "TEST")

    # リソースバックアップ作成：テナントが存在しない場合
    def test_backup_resource_no_tenant(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        create_backup = use_case.return_value.create_backup
        create_backup.return_value = "TEST"

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(100, aws_id),
            data={"no_reboot": True},
            format='json')

        create_backup.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソースバックアップ作成：AWS環境が存在しない場合
    def test_backup_resource_no_aws(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        create_backup = use_case.return_value.create_backup
        create_backup.return_value = "TEST"

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, 100),
            data={"no_reboot": True},
            format='json')

        create_backup.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # リソースバックアップ作成：EC2でリクエストが不正な場合
    def test_backup_resource_ec2_invalid_params(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id),
            format='json')

        self.assertEqual(response.status_code, 400)

    # リソースバックアップ作成：RDS正常系
    def test_backup_resource_rds(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        create_backup = use_case.return_value.create_backup
        create_backup.return_value = "TEST"

        # 検証対象の実行
        response = client.post(
            path='/api/tenants/{}/aws-environments/{}'
                 '/regions/ap-northeast-1/services/rds/resources/i-123456789012/backups/'.format(
                    tenant_id, aws_id),
            format='json')

        create_backup.assert_called_once()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["backup_id"], "TEST")
