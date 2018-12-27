from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import UserModel, RoleModel, TenantModel, AwsEnvironmentModel, Monitor, Resource
from backend.models.monitor import MonitorGraph
from datetime import datetime
from unittest import mock


@mock.patch("backend.views.monitor_view_set.ControlMonitorUseCase")
class MonitorViewSetTestCase(TestCase):

    api_path = '/api/tenants/{}/aws-environments/{}' \
               '/regions/ap-northeast-1/services/ec2/resources/i-123456789012/monitors/'

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
        super(MonitorViewSetTestCase, cls).setUpClass()
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
        response = client.get(self.api_path.format(1, 1), format='json')
        self.assertEqual(response.status_code, 401)

    # 監視設定作成
    def test_create_monitor(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        create_monitor = use_case.return_value.save_monitor
        resource = Resource.get_service_resource("ap-northeast-1", "ec2", "i-123456789012")
        resource.monitors.append(Monitor(
            "test_name",
            {"caution": 60, "danger": 90},
            True,
            300,
            1,
            'Average'
        ))

        create_monitor.return_value = resource

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id),
            data={
                "metric_name": "test_name",
                "values": {
                    "caution": 60,
                    "danger": 90
                },
                "enabled": True,
                "period": 300,
                "evaluation_period": 1,
                "statistic": 'Average'
            },
            format='json')

        use_case.assert_called_once()
        create_monitor.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "metric_name": "test_name",
            "values": {
                "danger": 90,
                "caution": 60
            },
            "enabled": True,
            "period": 300,
            "evaluation_period": 1,
            "statistic": 'Average',
            "comparison_operator": "GreaterThanOrEqualToThreshold",
            "status": None
        })

    # 監視設定作成：AWS環境が存在しない場合
    def test_create_monitor_no_aws_env(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(-1, -1),
            data={
                "metric_name": "test_name",
                "values": {
                    "caution": 60,
                    "danger": 90
                },
                "enabled": True,
                "period": 300,
                "evaluation_period": 1,
                "statistic": 'Average'
            },
            format='json')

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # 監視設定作成：不正なパラメータ
    def test_create_monitor_invalid_params(self, use_case: mock.Mock):
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
            data={
                "metric_name": "test_name",
                "values": {
                    "caution": "invalid",
                    "danger": 90
                },
                "enabled": True,
                "period": 300,
                "evaluation_period": 1,
                "statistic": 'Average'
            },
            format='json')

        use_case.assert_not_called()
        self.assertEqual(response.status_code, 400)

    # 監視設定取得：正常系
    def test_list_monitors(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        fetch_monitors = use_case.return_value.fetch_monitors
        monitors = [Monitor(
            "test_name",
            {"caution": 60, "danger": 90},
            True,
            300,
            1,
            'Average',
            Monitor.MonitorStatus.OK
        )]

        fetch_monitors.return_value = monitors

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(tenant_id, aws_id),
            format='json')

        use_case.assert_called_once()
        fetch_monitors.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{
            "metric_name": "test_name",
            "values": {
                "danger": 90,
                "caution": 60
            },
            "enabled": True,
            "period": 300,
            "evaluation_period": 1,
            "statistic": 'Average',
            "comparison_operator": "GreaterThanOrEqualToThreshold",
            "status": "OK"
        }])

    # 監視設定取得：AWS環境がない場合
    def test_list_monitors_no_aws(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # mock準備
        fetch_monitors = use_case.return_value.fetch_monitors

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format(-1, -1),
            format='json')

        use_case.assert_not_called()
        fetch_monitors.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # 監視設定取得：不正なパラメータ
    def test_list_monitors_invalid_params(self, use_case):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # mock準備
        fetch_monitors = use_case.return_value.fetch_monitors

        # 検証対象の実行
        response = client.get(
            path=self.api_path.format("invalid", "invalid"),
            format='json')

        use_case.assert_not_called()
        fetch_monitors.assert_not_called()
        self.assertEqual(response.status_code, 400)

    # グラフデータ取得：正常系
    def test_graph(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        data = {
            "start_time": "2018-12-01 00:00:00",
            "end_time": "2018-12-02 00:00:00",
            "period": 300,
            "stat": "Average"
        }
        graph = use_case.return_value.graph
        graph.return_value = MonitorGraph(
            **data, metric_name="NetworkOut"
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id) + "NetworkOut/graph/",
            data=data,
            format='json')

        use_case.assert_called_once()
        graph.assert_called_once()
        self.assertEqual(response.status_code, 200)

    # グラフデータ取得：AWs環境が見つからない場合
    def test_graph_no_aws(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # mock準備
        data = {
            "start_time": "2018-12-01 00:00:00",
            "end_time": "2018-12-02 00:00:00",
            "period": 300,
            "stat": "Average"
        }
        graph = use_case.return_value.graph
        graph.return_value = MonitorGraph(
            **data, metric_name="NetworkOut"
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(-1, -1) + "NetworkOut/graph/",
            data=data,
            format='json')

        use_case.assert_not_called()
        graph.assert_not_called()
        self.assertEqual(response.status_code, 404)

    # グラフデータ取得：パラメーターが不正の場合
    def test_graph_invalid_params(self, use_case: mock.Mock):
        client = APIClient()
        user_model = UserModel.objects.get(email="test_email")
        client.force_authenticate(user=user_model)

        # Company1のIDを取得
        tenant_id = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1").id
        # AWS環境のIDを取得
        aws_id = AwsEnvironmentModel.objects.get(aws_account_id="test_aws1").id

        # mock準備
        data = {
            "start_time": "2018-12-01 00:00:00",
            "end_time": "2018-12-02 00:00:00",
            "period": 300,
            "stat": "Average"
        }
        graph = use_case.return_value.graph
        graph.return_value = MonitorGraph(
            **data, metric_name="NetworkOut"
        )

        # 検証対象の実行
        response = client.post(
            path=self.api_path.format(tenant_id, aws_id) + "NetworkOut/graph/",
            data="invalid",
            format='json')

        use_case.assert_not_called()
        graph.assert_not_called()
        self.assertEqual(response.status_code, 400)
