from django.db.models.base import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from backend.usecases.control_monitor import ControlMonitorUseCase
from unittest import mock


class ControlMonitorTestCase(TestCase):

    # 監視設定保存：正常系
    @mock.patch('backend.usecases.control_monitor.CloudWatch')
    @mock.patch('backend.usecases.control_monitor.Sns')
    def test_save_monitor(self, mock_sns: mock.Mock, mock_cloudwatch: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()

        res = ControlMonitorUseCase(mock.Mock()).save_monitor(mock_user, mock_resource, mock_aws)

        self.assertEqual(res, mock_resource)
        mock_user.has_aws_env.assert_called()
        mock_sns.return_value.add_permission.assert_called_with(mock_aws)
        mock_cloudwatch.return_value.put_metric_alarms.assert_called_with(mock_resource, mock_sns.return_value.arn)

    # 監視設定保存：リクエストユーザーがAWSアカウントを利用できない場合
    @mock.patch('backend.usecases.control_monitor.CloudWatch')
    @mock.patch('backend.usecases.control_monitor.Sns')
    def test_save_monitor_no_aws(self, mock_sns: mock.Mock, mock_cloudwatch: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlMonitorUseCase(mock.Mock()).save_monitor(mock_user, mock_resource, mock_aws)

        mock_user.has_aws_env.assert_called()
        mock_sns.return_value.add_permission.assert_not_called()
        mock_cloudwatch.return_value.put_metric_alarms.assert_not_called()

    # 監視設定取得：正常系
    @mock.patch('backend.usecases.control_monitor.CloudWatch')
    def test_fetch_monitors(self, mock_cloudwatch: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()

        res = ControlMonitorUseCase(mock.Mock()).fetch_monitors(mock_user, mock_aws, mock_resource)

        self.assertEqual(res, mock_cloudwatch.return_value.describe_resource_monitors.return_value)
        mock_user.has_aws_env.assert_called()
        mock_cloudwatch.return_value.describe_resource_monitors.assert_called_with(mock_resource)

    # 監視設定取得：リクエストユーザーがAWS環境を利用できない場合
    @mock.patch('backend.usecases.control_monitor.CloudWatch')
    def test_fetch_monitors_no_aws(self, mock_cloudwatch: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlMonitorUseCase(mock.Mock()).fetch_monitors(mock_user, mock_aws, mock_resource)

        mock_user.has_aws_env.assert_called()
        mock_cloudwatch.return_value.describe_resource_monitors.assert_not_called()

    # グラフデータ取得：正常系
    @mock.patch('backend.usecases.control_monitor.CloudWatch')
    def test_graph(self, mock_cloudwatch: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()
        mock_monitor_graph = mock.Mock()
        get_chart = mock_cloudwatch.return_value.get_chart

        mock_monitor_graph.metric_name = "Valid"
        mock_resource.get_metrics.return_value = ["Valid"]

        res = ControlMonitorUseCase(mock.Mock()).graph(mock_user, mock_resource, mock_aws, mock_monitor_graph)

        mock_user.has_aws_env.assert_called()
        mock_resource.get_metrics.assert_called_once()
        get_chart.assert_called_once_with(mock_monitor_graph, mock_resource)
        self.assertEqual(res, get_chart.return_value)

    # グラフデータ取得：AWS環境を利用できない場合
    @mock.patch('backend.usecases.control_monitor.CloudWatch')
    def test_graph_no_aws(self, mock_cloudwatch: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()
        mock_monitor_graph = mock.Mock()
        get_chart = mock_cloudwatch.return_value.get_chart

        mock_monitor_graph.metric_name = "Valid"
        mock_resource.get_metrics.return_value = ["Valid"]

        with self.assertRaises(PermissionDenied):
            ControlMonitorUseCase(mock.Mock()).graph(mock_user, mock_resource, mock_aws, mock_monitor_graph)

        mock_user.has_aws_env.assert_called()
        mock_resource.get_metrics.assert_not_called()
        get_chart.assert_not_called()

    # グラフデータ取得：不正なメトリクスの場合
    @mock.patch('backend.usecases.control_monitor.CloudWatch')
    def test_graph_invalid_metrics(self, mock_cloudwatch: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()
        mock_monitor_graph = mock.Mock()
        get_chart = mock_cloudwatch.return_value.get_chart

        mock_monitor_graph.metric_name = "invalid"
        mock_resource.get_metrics.return_value = ["Valid"]

        with self.assertRaises(ObjectDoesNotExist):
            ControlMonitorUseCase(mock.Mock()).graph(mock_user, mock_resource, mock_aws, mock_monitor_graph)

        mock_user.has_aws_env.assert_called()
        mock_resource.get_metrics.assert_called()
        get_chart.assert_not_called()
