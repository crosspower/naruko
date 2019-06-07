from django.core.exceptions import PermissionDenied
from django.test import TestCase
from unittest.mock import Mock, patch
from unittest import mock
# デコレーターをmock化
with patch('backend.models.OperationLogModel.operation_log', lambda executor_index=None, target_method=None, target_arg_index_list=None: lambda func: func):
    from backend.usecases.control_aws_environment import ControlAwsEnvironment


class ControlAwsEnvironmentTestCase(TestCase):

    # AWS取得正常系
    @patch('backend.usecases.control_aws_environment.AwsEnvironmentModel')
    def test_fetch_aws_environments(self, mock_aws_model):
        mock_user = Mock()
        mock_tenant = Mock()
        objects_filter = mock_aws_model.objects.filter

        res = ControlAwsEnvironment(Mock()).fetch_aws_environments(mock_user, mock_tenant)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_called_once()
        objects_filter.assert_called_once_with(tenant_id=mock_tenant.id)
        self.assertEqual(res, objects_filter.return_value)

    # AWS取得：テナントに属していない場合
    @patch('backend.usecases.control_aws_environment.AwsEnvironmentModel')
    def test_fetch_aws_environments_no_belong_to_tenant(self, mock_aws_model):
        mock_user = Mock()
        mock_user.is_belong_to_tenant.return_value = False
        mock_tenant = Mock()

        with self.assertRaises(PermissionDenied):
            ControlAwsEnvironment(Mock()).fetch_aws_environments(mock_user, mock_tenant)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_not_called()
        mock_aws_model.objects.filter.assert_not_called()

    # AWS取得：AWSを管理できない場合
    @patch('backend.usecases.control_aws_environment.AwsEnvironmentModel')
    def test_fetch_aws_environments_cant_control_aws(self, mock_aws_model):
        mock_user = Mock()
        mock_user.can_control_aws.return_value = False
        mock_tenant = Mock()

        with self.assertRaises(PermissionDenied):
            ControlAwsEnvironment(Mock()).fetch_aws_environments(mock_user, mock_tenant)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_called_once()
        mock_aws_model.objects.filter.assert_not_called()

    # awsアカウント作成
    @patch('backend.usecases.control_aws_environment.UserModel')
    @patch('backend.usecases.control_aws_environment.Iam')
    def test_save_aws_environment(self, iam_mock, user_model_mock):
        mock_user = Mock()
        aws_environment_mock = Mock()

        mock_scheduler = Mock()
        user_model_mock.get_scheduler.return_value = mock_scheduler

        target = ControlAwsEnvironment(Mock())
        result = target.save_aws_environment(mock_user, aws_environment_mock)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_called_once()

        iam_mock.assert_called_once_with(aws_environment_mock, None)
        iam_mock.return_value.validate_role.assert_called_once_with(aws_environment_mock.aws_account_id,
                                                                    aws_environment_mock.aws_role)
        aws_environment_mock.save.assert_called_once()
        mock_scheduler.save.assert_called_once()
        self.assertEqual(result, aws_environment_mock)

    # awsアカウント作成: テナントに属していない場合
    @patch('backend.usecases.control_aws_environment.UserModel')
    @patch('backend.usecases.control_aws_environment.Iam')
    def test_save_aws_environment_not_belong_to_tenant(self, iam_mock, user_model_mock):
        mock_user = Mock()
        mock_user.is_belong_to_tenant.return_value = False
        aws_environment_mock = Mock()

        mock_scheduler = Mock()
        user_model_mock.get_scheduler.return_value = mock_scheduler

        target = ControlAwsEnvironment(Mock())

        with self.assertRaises(PermissionDenied):
            target.save_aws_environment(mock_user, aws_environment_mock)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_not_called()

        iam_mock.assert_not_called()
        iam_mock.return_value.validate_role.assert_not_called()

        aws_environment_mock.save.assert_not_called()
        mock_scheduler.save.assert_not_called()

    # awsアカウント作成: AWSを管理できない場合
    @patch('backend.usecases.control_aws_environment.UserModel')
    @patch('backend.usecases.control_aws_environment.Iam')
    def test_save_aws_environment_not_belong_to_tenant(self, iam_mock, user_model_mock):
        mock_user = Mock()
        mock_user.can_control_aws.return_value = False
        aws_environment_mock = Mock()

        mock_scheduler = Mock()
        user_model_mock.get_scheduler.return_value = mock_scheduler

        target = ControlAwsEnvironment(Mock())

        with self.assertRaises(PermissionDenied):
            target.save_aws_environment(mock_user, aws_environment_mock)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_called_once()

        iam_mock.assert_not_called()
        iam_mock.return_value.validate_role.assert_not_called()

        aws_environment_mock.save.assert_not_called()
        mock_scheduler.save.assert_not_called()

    # AWS削除
    def test_delete_aws_environment(self):
        mock_user = Mock()
        mock_aws = Mock()

        ControlAwsEnvironment(Mock()).delete_aws_environment(mock_user, mock_aws)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_called_once()
        mock_aws.delete.assert_called_once()

    # AWS削除：テナントに属していない場合
    def test_delete_aws_environment_not_belong_to_tenant(self):
        mock_user = Mock()
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = Mock()

        with self.assertRaises(PermissionDenied):
            ControlAwsEnvironment(Mock()).delete_aws_environment(mock_user, mock_aws)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_not_called()
        mock_aws.delete.assert_not_called()

    # AWS削除：AWSを操作できない場合
    def test_delete_aws_environment_cant_control_aws(self):
        mock_user = Mock()
        mock_user.can_control_aws.return_value = False
        mock_aws = Mock()

        with self.assertRaises(PermissionDenied):
            ControlAwsEnvironment(Mock()).delete_aws_environment(mock_user, mock_aws)

        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.can_control_aws.assert_called_once()
        mock_aws.delete.assert_not_called()

    # 請求情報取得：正常系
    @mock.patch('backend.usecases.control_aws_environment.CloudWatch')
    def test_billing_graph(self, mock_cloudwatch: Mock):
        # mock準備
        mock_user = Mock()
        mock_aws = Mock()
        mock_monitor_graph = Mock()

        mock_user.can_fetch_billing.return_value = True
        mock_user.has_aws_env.return_value = True

        get_chart = mock_cloudwatch.return_value.get_chart
        res = ControlAwsEnvironment(Mock()).billing_graph(mock_user, mock_aws, mock_monitor_graph)

        mock_user.has_aws_env.assert_called()
        mock_user.can_fetch_billing.assert_called()
        mock_cloudwatch.assert_called_once_with(mock_aws, 'us-east-1')
        get_chart.assert_called_once_with(mock_monitor_graph)
        self.assertEqual(res, get_chart.return_value)

    # 請求情報取得：使用できないAWSアカウントの場合
    def test_billing_graph_cant_use_aws(self):
        mock_user = Mock()
        mock_aws = Mock()
        mock_monitor_graph = Mock()

        mock_user.can_fetch_billing.return_value = True
        mock_user.has_aws_env.return_value = False

        with self.assertRaises(PermissionDenied):
            ControlAwsEnvironment(Mock()).billing_graph(mock_user, mock_aws, mock_monitor_graph)

        mock_user.has_aws_env.assert_called()
        mock_user.can_fetch_billing.assert_not_called()

    # 請求情報取得：権限を持っていないアカウントの場合
    def test_billing_graph_dont_have_permission(self):
        mock_user = Mock()
        mock_aws = Mock()
        mock_monitor_graph = Mock()

        mock_user.can_fetch_billing.return_value = False
        mock_user.has_aws_env.return_value = True

        with self.assertRaises(PermissionDenied):
            ControlAwsEnvironment(Mock()).billing_graph(mock_user, mock_aws, mock_monitor_graph)

        mock_user.has_aws_env.assert_called()
        mock_user.can_fetch_billing.assert_called()
