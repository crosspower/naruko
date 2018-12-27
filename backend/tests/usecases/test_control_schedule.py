from django.core.exceptions import PermissionDenied
from django.test import TestCase
from backend.usecases.control_schedule import ControlScheduleUseCase
from unittest import mock


class ControlScheduleTestCase(TestCase):

    # スケジュール保存：正常系
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_save_schedule(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()
        mock_schedule = mock.Mock()

        res = ControlScheduleUseCase(mock.Mock()).save_schedule(mock_user, mock_tenant, mock_aws, mock_schedule)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        mock_repo.save.assert_called_once_with(mock_schedule)
        self.assertEqual(res, mock_repo.save.return_value)

    # スケジュール保存：テナントに属していない場合
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_save_schedule_not_belong_to_tenant(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.is_belong_to_tenant.return_value = False
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()
        mock_schedule = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlScheduleUseCase(mock.Mock()).save_schedule(mock_user, mock_tenant, mock_aws, mock_schedule)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_not_called()
        mock_repo.save.assert_not_called()

    # スケジュール保存：AWS環境を利用できない場合場合
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_save_schedule_no_aws(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.has_aws_env.return_value = False
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()
        mock_schedule = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlScheduleUseCase(mock.Mock()).save_schedule(mock_user, mock_tenant, mock_aws, mock_schedule)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        mock_repo.save.assert_not_called()

    # スケジュール取得：正常系
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_fetch_schedules(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()

        res = ControlScheduleUseCase(mock.Mock()).fetch_schedules(mock_user, mock_tenant, mock_aws, mock_resource)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        mock_repo.fetch_schedules_by_resource.assert_called_once_with(mock_resource, mock_aws)
        self.assertEqual(res, mock_repo.fetch_schedules_by_resource.return_value)

    # スケジュール取得：テナントに属していない場合
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_fetch_schedules_not_belong_to_tenant(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.is_belong_to_tenant.return_value = False
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlScheduleUseCase(mock.Mock()).fetch_schedules(mock_user, mock_tenant, mock_aws, mock_resource)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_not_called()
        mock_repo.fetch_schedules_by_resource.assert_not_called()

    # スケジュール取得：AWS環境を利用できない場合場合
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_fetch_schedules_no_aws(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.has_aws_env.return_value = False
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()
        mock_resource = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlScheduleUseCase(mock.Mock()).fetch_schedules(mock_user, mock_tenant, mock_aws, mock_resource)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        mock_repo.fetch_schedules_by_resource.assert_not_called()

    # スケジュール削除：正常系
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_delete_schedule(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()

        ControlScheduleUseCase(mock.Mock()).delete_schedule(mock_user, mock_tenant, mock_aws, 1)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        mock_repo.delete.assert_called_once_with(1)

    # スケジュール削除：テナントに属していない場合
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_delete_schedule_not_belong_to_tenant(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.is_belong_to_tenant.return_value = False
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlScheduleUseCase(mock.Mock()).delete_schedule(mock_user, mock_tenant, mock_aws, 1)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_not_called()
        mock_repo.delete.assert_not_called()

    # スケジュール削除：AWS環境を利用できない場合場合
    @mock.patch("backend.usecases.control_schedule.EventRepository")
    def test_delete_schedule_no_aws(self, mock_repo: mock.Mock):
        # mock準備
        mock_user = mock.Mock()
        mock_user.has_aws_env.return_value = False
        mock_tenant = mock.Mock()
        mock_aws = mock.Mock()

        with self.assertRaises(PermissionDenied):
            ControlScheduleUseCase(mock.Mock()).delete_schedule(mock_user, mock_tenant, mock_aws, 1)

        mock_user.is_belong_to_tenant.assert_called_once_with(mock_tenant)
        mock_user.has_aws_env.assert_called_once_with(mock_aws)
        mock_repo.delete.assert_not_called()
