from botocore.exceptions import ClientError
from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel, Schedule, ScheduleModel,\
    CloudWatchEvent
from datetime import datetime
from unittest import mock


@mock.patch("backend.views.schedule_view_set.ControlScheduleUseCase")
class ScheduleViewSetTestCase(TestCase):

    api_path = '/api/tenants/{}/aws-environments/{}' \
               '/regions/ap-northeast-1/services/ec2/resources/i-123456789012/schedules/'

    @staticmethod
    def _create_schedule_model(name, aws):
        now = datetime.now()
        schedule = ScheduleModel.objects.create(
            name=name,
            action="action",
            params='{"test": "test"}',
            notification=True,
            resource_id="i-01234567890",
            service="ec2",
            region="ap-northeast-1",
            aws_environment=aws,
            created_at=now,
            updated_at=now
        )
        schedule.save()
        return schedule

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
        super(ScheduleViewSetTestCase, cls).setUpClass()
        # Company1に所属するMASTERユーザーの作成
        role_model = cls._create_role_model(2, "test_role")
        tenant_model1 = cls._create_tenant_model("test_tenant_users_in_tenant_1")
        # Company1に所属するAWS環境の作成
        aws1 = cls._create_aws_env_model("test_name1", "test_aws1", tenant_model1)
        # aws1に所属するスケジュールの作成
        cls._create_schedule_model("test_schedule1", aws1)

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
        response = client.get(self.api_path.format(1, 1), format='json')
        self.assertEqual(response.status_code, 401)

    # スケジュール作成：正常系
    def test_create_schedule(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.return_value = Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id),
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_called_once()
        save_schedule.assert_called_once()
        self.assertEqual(response.status_code, 201)

    # スケジュール作成：テナントが見つからない場合
    def test_create_schedule_no_tenant(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.return_value = Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(-1, aws_id),
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_not_called()
        save_schedule.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール作成：AWS環境が見つからない場合
    def test_create_schedule_no_aws(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.return_value = Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, -1),
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_not_called()
        save_schedule.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール作成：boto3の例外時
    def test_create_schedule_botocore_exception(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.side_effect = ClientError

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id),
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_called_once()
        save_schedule.assert_called_once()
        self.assertEqual(response.status_code, 400)

    # スケジュール更新：正常系
    def test_update_schedule(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.return_value = Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )

        # 検証対象の実行
        response = client.put(
            path=self.api_path.format(tenant_id, aws_id) + str(schedule_id) + "/",
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_called_once()
        save_schedule.assert_called_once()
        self.assertEqual(response.status_code, 201)

    # スケジュール更新：テナントが見つからない場合
    def test_update_schedule_no_tenant(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.return_value = Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )

        # 検証対象の実行
        response = client.put(
            path=self.api_path.format(-1, aws_id) + str(schedule_id) + "/",
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_not_called()
        save_schedule.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール更新：AWS環境が見つからない場合
    def test_update_schedule_no_aws(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.return_value = Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )

        # 検証対象の実行
        response = client.put(
            path=self.api_path.format(tenant_id, -1) + str(schedule_id) + "/",
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_not_called()
        save_schedule.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール更新：boto3の例外時
    def test_update_schedule_botocore_exception(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        save_schedule = use_case.return_value.save_schedule
        save_schedule.side_effect = ClientError

        # 検証対象の実行
        response = client.put(
            path=self.api_path.format(tenant_id, aws_id) + str(schedule_id) + "/",
            data={
                "name": "test_schedule",
                "is_active": True,
                "action": "test_action",
                "schedule_expression": "(10 * * * ? *)",
                "params": {"key": "value"},
                "notification": True
            },
            format="json"
        )

        use_case.assert_called_once()
        save_schedule.assert_called_once()
        self.assertEqual(response.status_code, 400)

    # スケジュール取得：正常系
    def test_list_schedule(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        fetch_schedules = use_case.return_value.fetch_schedules
        fetch_schedules.return_value = [Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )]

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, aws_id),
            format="json"
        )

        use_case.assert_called_once()
        fetch_schedules.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # スケジュール取得：テナントが見つからない場合
    def test_list_schedule_no_tenant(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        fetch_schedules = use_case.return_value.fetch_schedules
        fetch_schedules.return_value = [Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )]

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(-1, aws_id),
            format="json"
        )

        use_case.assert_not_called()
        fetch_schedules.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール取得：AWS環境が見つからない場合
    def test_list_schedule_no_aws(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id

        # mock準備
        fetch_schedules = use_case.return_value.fetch_schedules
        fetch_schedules.return_value = [Schedule(
            ScheduleModel(),
            CloudWatchEvent("test", True)
        )]

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, -1),
            format="json"
        )

        use_case.assert_not_called()
        fetch_schedules.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール取得：boto3の例外時
    def test_list_schedule_botocore_exception(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        fetch_schedules = use_case.return_value.fetch_schedules
        fetch_schedules.side_effect = ClientError

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, aws_id),
            format="json"
        )

        use_case.assert_called_once()
        fetch_schedules.assert_called_once()
        self.assertEqual(response.status_code, 400)

    # スケジュール削除：正常系
    def test_delete_schedule(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        delete_schedule = use_case.return_value.delete_schedule

        # 検証対象の実行
        response = client.delete(
            path=self.api_path.format(tenant_id, aws_id) + str(schedule_id) + "/",
            format="json"
        )

        use_case.assert_called_once()
        delete_schedule.assert_called_once()
        self.assertEqual(response.status_code, 204)

    # スケジュール削除：テナントが見つからない場合
    def test_delete_schedule_no_tenant(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        delete_schedule = use_case.return_value.delete_schedule

        # 検証対象の実行
        response = client.delete(
            path=self.api_path.format(-1, aws_id) + str(schedule_id) + "/",
            format="json"
        )

        use_case.assert_not_called()
        delete_schedule.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール削除：AWS環境が見つからない場合
    def test_delete_schedule_no_aws(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        delete_schedule = use_case.return_value.delete_schedule

        # 検証対象の実行
        response = client.delete(
            path=self.api_path.format(tenant_id, -1) + str(schedule_id) + "/",
            format="json"
        )

        use_case.assert_not_called()
        delete_schedule.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # スケジュール削除：boto3の例外時
    def test_delete_schedule_botocore_exception(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id
        # スケジュールのIDを取得
        schedule_id = ScheduleModel.objects.get(name="test_schedule1").id

        # mock準備
        delete_schedule = use_case.return_value.delete_schedule
        delete_schedule.side_effect = ClientError

        # 検証対象の実行
        response = client.delete(
            path=self.api_path.format(tenant_id, aws_id) + str(schedule_id) + "/",
            format="json"
        )

        use_case.assert_called_once()
        delete_schedule.assert_called_once()
        self.assertEqual(response.status_code, 400)
