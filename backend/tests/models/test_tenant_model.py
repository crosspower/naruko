from django.test import TestCase
from backend.models import UserModel, TenantModel, RoleModel
from datetime import datetime


class TenantModelTests(TestCase):
    # テナントが登録されていないことを確認する
    def test_is_empty(self):
        model_objects_all = TenantModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)

    # テナントが登録できることを確認する
    def test_create(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        tenant_model.save()

        model_objects_all = TenantModel.objects.all()
        self.assertEqual(model_objects_all.count(), 1)

    # 登録したテナントが削除できることを確認する
    def test_delete(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        tenant_model.save()
        tenant_model = TenantModel.objects.all()
        tenant_model.all().delete()
        model_objects_all = TenantModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)

    # 登録したテナントの更新ができることを確認する
    def test_update(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )

        tenant_model.save()
        model_objects_all = TenantModel.objects.all()
        actual_tenant_model = model_objects_all[0]
        actual_tenant_model.tenant_name = "updated_tenant"
        actual_tenant_model.save()

        model_objects_get = TenantModel.objects.get(tenant_name="updated_tenant")
        self.assertEqual(model_objects_get.tenant_name, "updated_tenant")
