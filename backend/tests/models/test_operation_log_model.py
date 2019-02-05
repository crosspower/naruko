from django.test import TestCase
from backend.models import OperationLogModel, TenantModel, UserModel, RoleModel
from datetime import datetime
from unittest import mock


class OperationLogModelTests(TestCase):
    # 操作ログが登録されていないことを確認する
    def test_is_empty(self):
        objects_all = OperationLogModel.objects.all()
        self.assertEqual(objects_all.count(), 0)

    # 操作ログが登録できることを確認する
    def test_create(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        user_model = UserModel.objects.create(
            name="test_user",
            email="test@test.com",
            role=role_model,
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        operation_log_model = OperationLogModel.objects.create(
            executor=user_model,
            tenant=tenant_model,
            operation="operation",
            created_at=now,
            updated_at=now
        )

        operation_log_model.save()
        objects_all = OperationLogModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

    # 登録した操作ログが削除できることを確認する
    def test_delete(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        user_model = UserModel.objects.create(
            name="test_user",
            email="test@test.com",
            role=role_model,
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        operation_log_model = OperationLogModel.objects.create(
            executor=user_model,
            tenant=tenant_model,
            operation="operation",
            created_at=now,
            updated_at=now
        )

        operation_log_model.save()
        objects_all = OperationLogModel.objects.all()
        objects_all.all().delete()
        objects_all = OperationLogModel.objects.all()
        self.assertEqual(objects_all.count(), 0)

    # 登録した操作ログが更新できることを確認する
    def test_update(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        user_model = UserModel.objects.create(
            name="test_user",
            email="test@test.com",
            role=role_model,
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        operation_log_model = OperationLogModel.objects.create(
            executor=user_model,
            tenant=tenant_model,
            operation="operation",
            created_at=now,
            updated_at=now
        )

        operation_log_model.save()
        # 登録されたことを確認する
        objects_all = OperationLogModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

        # 更新
        model_objects_all = OperationLogModel.objects.all()
        actual_operation_log_model = model_objects_all[0]
        actual_operation_log_model.operation = "updated_operation"
        actual_operation_log_model.save()

        # 更新されたことを確認する
        model_objects_get = OperationLogModel.objects.get(operation="updated_operation")
        self.assertEqual(model_objects_get.operation, "updated_operation")

    # テナントを削除したときに紐づく操作ログが削除されることを確認する
    def test_delete_cascade_tenant(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        user_model = UserModel.objects.create(
            name="test_user",
            email="test@test.com",
            role=role_model,
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        operation_log_model = OperationLogModel.objects.create(
            executor=user_model,
            tenant=tenant_model,
            operation="operation",
            created_at=now,
            updated_at=now
        )

        operation_log_model.save()
        # 登録されたことを確認する
        objects_all = OperationLogModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

        # 削除されたことを確認する
        tenant_model.delete()
        model_objects_all = OperationLogModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)

    # ユーザーを削除したときに紐づく操作ログの実行者が消えることを確認する
    def test_delete_set_null_user(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        user_model = UserModel.objects.create(
            name="test_user",
            email="test@test.com",
            role=role_model,
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        operation_log_model = OperationLogModel.objects.create(
            executor=user_model,
            tenant=tenant_model,
            operation="operation",
            created_at=now,
            updated_at=now
        )

        operation_log_model.save()
        # 登録されたことを確認する
        objects_all = OperationLogModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

        # 更新されることを確認する
        user_model.delete()
        model_objects_all = OperationLogModel.objects.all()
        self.assertEqual(model_objects_all[0].executor, None)

    # 操作ログ書き込み
    def test_operation_log(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        user_model = UserModel.objects.create(
            name="test_user",
            email="test@test.com",
            role=role_model,
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        @staticmethod
        def target_info(user, target):
            return "{}_{}".format(user.name, target.param)

        @OperationLogModel.operation_log(executor_index=0, target_method=target_info, target_arg_index_list=[0, 1])
        def test_func(request_user, target):
            return "TEST_FUNC"

        mock_target = mock.Mock()
        mock_target.param = "TEST_PARAM"
        res = test_func(user_model, mock_target)

        self.assertEqual(res, "TEST_FUNC")
        operation_log_model = OperationLogModel.objects.all()[0]

        self.assertEqual(operation_log_model.operation, "test_func: test_user_TEST_PARAM")
