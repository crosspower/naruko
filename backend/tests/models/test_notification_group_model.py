from django.test import TestCase
from backend.models import NotificationGroupModel, TenantModel
from datetime import datetime


class NotificationGroupModelTest(TestCase):

    # 通知グループが登録されていないことを確認する
    def test_is_empty(self):
        objects_all = NotificationGroupModel.objects.all()
        self.assertEqual(objects_all.count(), 0)

    # 通知グループが登録できることを確認する
    def test_create(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        model_objects_create = NotificationGroupModel.objects.create(
            name="test", tenant=tenant_model, created_at=now, updated_at=now)

        model_objects_create.save()

        objects_all = NotificationGroupModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

    # 登録した通知グループの更新ができることを確認する
    def test_update(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        model_objects_create = NotificationGroupModel.objects.create(
            name="test",tenant=tenant_model, created_at=now, updated_at=now)

        model_objects_create.save()
        # 登録されたことを確認する
        objects_all = NotificationGroupModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

        # 更新
        notification_group_model = objects_all[0]
        notification_group_model.name = "update"
        notification_group_model.save()

        # 更新されたことを確認する
        objects_get = NotificationGroupModel.objects.get(name="update")
        self.assertEqual(objects_get.name, "update")

    # 登録した通知グループを削除できることを確認する
    def test_delete(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        model_objects_create = NotificationGroupModel.objects.create(
            name="test", tenant=tenant_model, created_at=now, updated_at=now)

        model_objects_create.save()
        # 登録されたことを確認する
        objects_all = NotificationGroupModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

        objects_all.all().delete()
        self.assertEqual(objects_all.count(), 0)

    # テナントが削除された時通知グループを削除されることを確認する
    def test_delete_cascade_tenant(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        model_objects_create = NotificationGroupModel.objects.create(
            name="test", tenant=tenant_model, created_at=now, updated_at=now)

        model_objects_create.save()
        # 登録されたことを確認する
        objects_all = NotificationGroupModel.objects.all()
        self.assertEqual(objects_all.count(), 1)

        tenant_model.delete()
        model_objects_all = NotificationGroupModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)
