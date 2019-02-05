from django.core.exceptions import PermissionDenied
from django.test import TestCase
from backend.models import UserModel, AwsEnvironmentModel
from unittest import mock
# デコレーターをmock化
with mock.patch('backend.models.OperationLogModel.operation_log', lambda executor_index=None, target_method=None, target_arg_index_list=None: lambda func: func):
    from backend.usecases.control_resource import ControlResourceUseCase


class ControlResourceTestCase(TestCase):

    # 正常系
    @mock.patch('backend.usecases.control_resource.CloudWatch')
    @mock.patch('backend.usecases.control_resource.ResourceGroupTagging')
    def test_fetch_resources(self, mock_tag: mock.Mock, mock_cloudwatch: mock.Mock):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        region = "region"

        # mockの準備
        cloudwatch_return_value = mock_cloudwatch.return_value
        cloudwatch_return_value.get_resources_status.return_value = {
            "EC2": {"ec2": "OK"},
            "RDS": {"rds": "DANGER"},
            "ELB": {"elb": "CAUTION"}
        }
        tag_return_value = mock_tag.return_value
        mock_resource1 = mock.Mock()
        mock_resource1.get_service_name.return_value = "EC2"
        mock_resource1.resource_id = "ec2"
        mock_resource2 = mock.Mock()
        mock_resource2.get_service_name.return_value = "RDS"
        mock_resource2.resource_id = "rds"
        mock_resource3 = mock.Mock()
        mock_resource3.get_service_name.return_value = "ELB"
        mock_resource3.resource_id = "elb"
        mock_resource4 = mock.Mock()
        mock_resource4.get_service_name.return_value = "EC2"
        tag_return_value.get_resources.return_value = [[
            mock_resource1, mock_resource2, mock_resource3, mock_resource4
        ], []]

        # 検証対象の実行
        resp = ControlResourceUseCase(mock.Mock()).fetch_resources(mock_user, mock_aws, region)

        # 戻り値の検証
        self.assertEqual(resp, [
            mock_resource1, mock_resource2, mock_resource3, mock_resource4
        ])
        self.assertEqual([
            "OK",
            "DANGER",
            "CAUTION",
            "UNSET"
        ], [
            mock_resource1.status,
            mock_resource2.status,
            mock_resource3.status,
            mock_resource4.status
        ])

        # 呼び出し検証
        mock_user.has_aws_env.assert_called_with(mock_aws)
        mock_cloudwatch.assert_called_with(
            aws_environment=mock_aws,
            region=region
        )
        mock_tag.assert_called_with(
            aws_environment=mock_aws,
            region=region
        )

        cloudwatch_return_value.get_resources_status.assert_called()
        tag_return_value.get_resources.assert_called()

    # ユーザーがテナントに属していない場合
    @mock.patch('backend.usecases.control_resource.CloudWatch')
    @mock.patch('backend.usecases.control_resource.ResourceGroupTagging')
    def test_not_belong_to_tenant(self, mock_tag: mock.Mock, mock_cloudwatch: mock.Mock):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        region = "region"

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).fetch_resources(mock_user, mock_aws, region)

        # 呼び出し検証
        mock_user.has_aws_env.assert_not_called()
        mock_cloudwatch.assert_not_called()
        mock_tag.assert_not_called()

        cloudwatch_return_value = mock_cloudwatch.return_value
        tag_return_value = mock_tag.return_value

        cloudwatch_return_value.get_resources_status.assert_not_called()
        tag_return_value.get_resources.assert_not_called()

    # ユーザーが指定されたAWS環境を利用できない場合
    @mock.patch('backend.usecases.control_resource.CloudWatch')
    @mock.patch('backend.usecases.control_resource.ResourceGroupTagging')
    def test_cant_use_aws_env(self, mock_tag: mock.Mock, mock_cloudwatch: mock.Mock):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        region = "region"

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).fetch_resources(mock_user, mock_aws, region)

        # 呼び出し検証
        mock_user.has_aws_env.assert_called_with(mock_aws)
        mock_cloudwatch.assert_not_called()
        mock_tag.assert_not_called()

        cloudwatch_return_value = mock_cloudwatch.return_value
        tag_return_value = mock_tag.return_value

        cloudwatch_return_value.get_resources_status.assert_not_called()
        tag_return_value.get_resources.assert_not_called()

    # リソース起動
    def test_start_resource(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        ControlResourceUseCase(mock.Mock()).start_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.start.assert_called_once()

    # リソース起動:ユーザーがテナントに属していない場合
    def test_start_resource_not_belong_to_tenant(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).start_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_not_called()

        mock_resource.start.assert_not_called()

    # リソース起動:ユーザーがAWS環境を使用できない場合
    def test_start_resource_not_have_aws(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).start_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.start.assert_not_called()

    # リソース再起動
    def test_reboot_resource(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        ControlResourceUseCase(mock.Mock()).reboot_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.reboot.assert_called_once()

    # リソース再起動:ユーザーがテナントに属していない場合
    def test_reboot_resource_not_belong_to_tenant(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).reboot_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_not_called()

        mock_resource.reboot.assert_not_called()

    # リソース再起動:ユーザーがAWS環境を使用できない場合
    def test_reboot_resource_not_have_aws(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).reboot_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.reboot.assert_not_called()

    # リソース再起動
    def test_stop_resource(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        ControlResourceUseCase(mock.Mock()).stop_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.stop.assert_called_once()

    # リソース再起動:ユーザーがテナントに属していない場合
    def test_stop_resource_not_belong_to_tenant(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).stop_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_not_called()

        mock_resource.stop.assert_not_called()

    # リソース再起動:ユーザーがAWS環境を使用できない場合
    def test_stop_resource_not_have_aws(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).stop_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.stop.assert_not_called()

    # リソース詳細取得:正常系
    def test_describe_resource(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        res = ControlResourceUseCase(mock.Mock()).describe_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.describe.assert_called_once()

        self.assertEqual(res, mock_resource.describe.return_value)

    # リソース詳細取得:リクエストユーザーがテナントに属していない場合
    def test_describe_resource_not_belong_to_tenant(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).describe_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_not_called()

        mock_resource.describe.assert_not_called()

    # リソース詳細取得:リクエストユーザーがAWS環境を使用できない場合
    def test_describe_resource_not_hav_aws(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).describe_resource(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

        mock_resource.describe.assert_not_called()

    # リソースバックアップ取得
    def test_fetch_backups(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        res = ControlResourceUseCase(mock.Mock()).fetch_backups(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()
        self.assertEqual(res, mock_resource.fetch_backups.return_value)

    # リソースバックアップ取得:リクエストユーザーがテナントに属していない場合
    def test_fetch_backups_not_belong_to_tenant(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).fetch_backups(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_not_called()

    # リソースバックアップ取得:AWS環境を使用できない場合
    def test_fetch_backups_not_have_aws(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).fetch_backups(mock_user, mock_aws, mock_resource)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

    # リソースバックアップ作成
    def test_create_backup(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        res = ControlResourceUseCase(mock.Mock()).create_backup(mock_user, mock_aws, mock_resource, True)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()
        self.assertEqual(res, mock_resource.create_backup.return_value)

    # リソースバックアップ作成:リクエストユーザーがテナントに属していない場合
    def test_create_backup_not_belong_to_tenant(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).create_backup(mock_user, mock_aws, mock_resource, True)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_not_called()

    # リソースバックアップ作成:AWS環境を使用できない場合
    def test_create_backup_not_have_aws(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_resource = mock.Mock()

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).create_backup(mock_user, mock_aws, mock_resource, True)

        # 呼び出し検証
        mock_user.is_belong_to_tenant.assert_called_once()
        mock_user.has_aws_env.assert_called_once()

    # コマンド実行：正常系
    def test_run_command(self):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_command = mock.Mock()

        # 検証対象の実行
        res = ControlResourceUseCase(mock.Mock()).run_command(mock_user, mock_aws, mock_command)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_aws.tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        mock_command.run.assert_called_once_with(mock_aws)
        self.assertEqual(res, mock_command)

    # ドキュメント一覧取得
    @mock.patch("backend.usecases.control_resource.Ssm")
    def test_fetch_documents(self, mock_ssm):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)

        list_documents = mock_ssm.return_value.list_documents
        list_documents.return_value = [[1, 2, 3], [4, 5, 6]]

        # 検証対象の実行
        res = ControlResourceUseCase(mock.Mock()).fetch_documents(mock_user, mock_aws, "region")

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_aws.tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        list_documents.assert_called()
        self.assertEqual(res, [1, 2, 3, 4, 5, 6])

    # ドキュメント一覧取得：リクエストユーザーがテナントに属していない場合
    @mock.patch("backend.usecases.control_resource.Ssm")
    def test_fetch_documents_not_belong_to_tenant(self, mock_ssm):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)

        list_documents = mock_ssm.return_value.list_documents
        list_documents.return_value = [[1, 2, 3], [4, 5, 6]]

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).fetch_documents(mock_user, mock_aws, "region")

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_aws.tenant)
        mock_user.has_aws_env.assert_not_called()
        list_documents.assert_not_called()

    # ドキュメント一覧取得：AWS環境が使用できない場合
    @mock.patch("backend.usecases.control_resource.Ssm")
    def test_fetch_documents_no_aws(self, mock_ssm):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)

        list_documents = mock_ssm.return_value.list_documents
        list_documents.return_value = [[1, 2, 3], [4, 5, 6]]

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).fetch_documents(mock_user, mock_aws, "region")

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_aws.tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        list_documents.assert_not_called()

    # ドキュメント詳細取得
    @mock.patch("backend.usecases.control_resource.Ssm")
    def test_describe_document(self, mock_ssm):
        mock_user = mock.Mock(spec=UserModel)
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_doc = mock.Mock()

        describe_document = mock_ssm.return_value.describe_document
        describe_document.return_value = mock_doc

        # 検証対象の実行
        res = ControlResourceUseCase(mock.Mock()).describe_document(mock_user, mock_aws, "region", "name")

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_aws.tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        describe_document.assert_called_once_with("name")
        self.assertEqual(res, mock_doc)

    # ドキュメント詳細取得:テナントに属していない場合
    @mock.patch("backend.usecases.control_resource.Ssm")
    def test_describe_document_not_belong_to_tenant(self, mock_ssm):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.is_belong_to_tenant.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_doc = mock.Mock()

        describe_document = mock_ssm.return_value.describe_document
        describe_document.return_value = mock_doc

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).describe_document(mock_user, mock_aws, "region", "name")

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_aws.tenant)
        mock_user.has_aws_env.assert_not_called()
        describe_document.assert_not_called()

    # ドキュメント詳細取得:AWSを使用できない場合
    @mock.patch("backend.usecases.control_resource.Ssm")
    def test_describe_document_no_aws(self, mock_ssm):
        mock_user = mock.Mock(spec=UserModel)
        mock_user.has_aws_env.return_value = False
        mock_aws = mock.Mock(spec=AwsEnvironmentModel)
        mock_doc = mock.Mock()

        describe_document = mock_ssm.return_value.describe_document
        describe_document.return_value = mock_doc

        # 検証対象の実行
        with self.assertRaises(PermissionDenied):
            ControlResourceUseCase(mock.Mock()).describe_document(mock_user, mock_aws, "region", "name")

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_aws.tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        describe_document.assert_not_called()
