from django.test import TestCase
from backend.models import UserModel, TenantModel, AwsEnvironmentModel, RoleModel
from datetime import datetime
from django.db.models.deletion import ProtectedError


class UserModelTests(TestCase):
    # ユーザーが登録されていないことを確認する
    def test_is_empty(self):
        user_model_objects_all = UserModel.objects.all()
        self.assertEqual(user_model_objects_all.count(), 0)

    # ユーザーが登録できることを確認する
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

        user_model = UserModel(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model,
            role=role_model,
            created_at=now,
            updated_at=now
        )

        user_model.save()
        saved_user_model = UserModel.objects.all()
        self.assertEqual(saved_user_model.count(), 1)

    # 登録したユーザーが削除できることを確認する
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

        user_model = UserModel(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model,
            role=role_model,
            created_at=now,
            updated_at=now
        )

        user_model.save()
        saved_user_model = UserModel.objects.all()
        saved_user_model.all().delete()
        deleted_user_model = UserModel.objects.all()
        self.assertEqual(deleted_user_model.count(), 0)

    # 登録したユーザーの更新ができることを確認する
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

        user_model = UserModel(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model,
            role=role_model,
            created_at=now,
            updated_at=now
        )

        user_model.save()
        saved_user_model = UserModel.objects.all()
        actual_user_model = saved_user_model[0]
        actual_user_model.email = "updated_email"
        actual_user_model.save()

        user_model_objects_get = UserModel.objects.get(email="updated_email")
        self.assertEqual(user_model_objects_get.email, "updated_email")

    # テナントを削除したとき紐づくユーザーが削除されることを確認する
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

        user_model = UserModel(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model,
            role=role_model,
            created_at=now,
            updated_at=now
        )

        user_model.save()
        # 登録されたことを確認する
        model_objects_all = UserModel.objects.all()
        self.assertEqual(model_objects_all.count(), 1)

        # 削除されたことを確認する
        tenant_model.delete()
        model_objects_all = UserModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)

    # 特定のロールに紐づくユーザーがいる際にロールが削除できないことを確認する
    def test_delete_protect_role(self):
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

        user_model = UserModel(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model,
            role=role_model,
            created_at=now,
            updated_at=now
        )

        user_model.save()
        # 登録されたことを確認する
        model_objects_all = UserModel.objects.all()
        self.assertEqual(model_objects_all.count(), 1)

        # 削除できないことを確認する
        with self.assertRaises(ProtectedError):
            role_model.delete()
        model_objects_all = UserModel.objects.all()
        self.assertEqual(model_objects_all.count(), 1)
