from django.test import TestCase
from backend.models import RoleModel
from datetime import datetime


class RoleModelTests(TestCase):
    # ロールが登録されていないことを確認する
    def test_is_empty(self):
        role_model_objects_all = RoleModel.objects.all()
        self.assertEqual(role_model_objects_all.count(), 0)

    # ロールが登録できることを確認する
    def test_create(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )
        role_model.save()

        role_model_objects_all = RoleModel.objects.all()
        self.assertEqual(role_model_objects_all.count(), 1)

    # 登録したロールが削除できることを確認する
    def test_delete(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        role_model.save()
        role_model = RoleModel.objects.all()
        role_model.all().delete()
        role_model_objects_all = RoleModel.objects.all()
        self.assertEqual(role_model_objects_all.count(), 0)

    # 登録したロールの更新ができることを確認する
    def test_update(self):
        now = datetime.now()
        role_model = RoleModel.objects.create(
            id=RoleModel.MASTER_ID,
            role_name="test_role",
            created_at=now,
            updated_at=now
        )

        role_model.save()
        role_model_objects_all = RoleModel.objects.all()
        actual_role_model = role_model_objects_all[0]
        actual_role_model.role_name = "updated_role"
        actual_role_model.save()

        role_model_objects_get = RoleModel.objects.get(role_name="updated_role")
        self.assertEqual(role_model_objects_get.role_name, "updated_role")

