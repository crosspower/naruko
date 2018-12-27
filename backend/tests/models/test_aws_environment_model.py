from django.test import TestCase
from backend.models import AwsEnvironmentModel, TenantModel
from datetime import datetime


class AwsEnvironmentModelTests(TestCase):
    # AWS環境が登録されていないことを確認する
    def test_is_empty(self):
        model_objects_all = AwsEnvironmentModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)

    # AWS環境が登録できることを確認する
    def test_create(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        aws_env_model = AwsEnvironmentModel.objects.create(
            aws_account_id="test_aws_account_id",
            aws_role="test_aws_role",
            aws_external_id="test_aws_external_id",
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )
        aws_env_model.save()

        model_objects_all = AwsEnvironmentModel.objects.all()
        self.assertEqual(model_objects_all.count(), 1)

    # 登録したAWS環境が削除できることを確認する
    def test_delete(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        aws_env_model = AwsEnvironmentModel.objects.create(
            aws_account_id="test_aws_account_id",
            aws_role="test_aws_role",
            aws_external_id="test_aws_external_id",
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        aws_env_model.save()
        aws_env_model = AwsEnvironmentModel.objects.all()
        aws_env_model.all().delete()
        model_objects_all = AwsEnvironmentModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)

    # 登録したAWS環境の更新ができることを確認する
    def test_update(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        aws_env_model = AwsEnvironmentModel.objects.create(
            aws_account_id="test_aws_account_id",
            aws_role="test_aws_role",
            aws_external_id="test_aws_external_id",
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        aws_env_model.save()
        # 登録されたことを確認する
        model_objects_all = AwsEnvironmentModel.objects.all()
        self.assertEqual(model_objects_all.count(), 1)

        # 更新
        model_objects_all = AwsEnvironmentModel.objects.all()
        actual_aws_env_model = model_objects_all[0]
        actual_aws_env_model.aws_account_id = "updated_aws_env"
        actual_aws_env_model.save()

        # 更新されたことを確認する
        model_objects_get = AwsEnvironmentModel.objects.get(aws_account_id="updated_aws_env")
        self.assertEqual(model_objects_get.aws_account_id, "updated_aws_env")

    # テナントを削除したときに紐づくAWS環境が削除されることを確認する
    def test_delete_cascade_tenant(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now
        )
        aws_env_model = AwsEnvironmentModel.objects.create(
            aws_account_id="test_aws_account_id",
            aws_role="test_aws_role",
            aws_external_id="test_aws_external_id",
            tenant=tenant_model,
            created_at=now,
            updated_at=now
        )

        aws_env_model.save()
        # 登録されたことを確認する
        model_objects_all = AwsEnvironmentModel.objects.all()
        self.assertEqual(model_objects_all.count(), 1)

        # 削除されたことを確認する
        tenant_model.delete()
        model_objects_all = AwsEnvironmentModel.objects.all()
        self.assertEqual(model_objects_all.count(), 0)

