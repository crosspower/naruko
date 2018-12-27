from django.test import TestCase
from backend.models import EventModel, ScheduleModel, TenantModel, AwsEnvironmentModel
from datetime import datetime


class EventModelTestCase(TestCase):

    # イベントが登録されていないことを確認する
    def test_is_empty(self):
        objects_all = EventModel.objects.all()
        self.assertEqual(objects_all.count(), 0)

    # イベントが登録できることを確認する
    def test_create(self):
        now = datetime.now()
        objects_create = EventModel.objects.create(created_at=now, updated_at=now)

        objects_create.save()

        event_all = EventModel.all()
        self.assertEqual(event_all.count(), 1)

    # 登録したイベントが削除できることを確認する
    def test_delete(self):
        now = datetime.now()
        objects_create = EventModel.objects.create(created_at=now, updated_at=now)

        objects_create.save()

        event_all = EventModel.all()
        self.assertEqual(event_all.count(), 1)

        event_all.all().delete()

        event_all = EventModel.all()
        self.assertEqual(event_all.count(), 0)

    # 登録したイベントの更新ができることを確認する
    def test_update(self):
        now = datetime.now()
        objects_create = EventModel.objects.create(created_at=now, updated_at=now)

        objects_create.save()

        event_all = EventModel.all()
        self.assertEqual(event_all.count(), 1)

        event = event_all[0]
        event.updated_at = datetime.now()
        event.save()

        updated_event = EventModel.get(event.id)
        self.assertNotEqual(updated_event.updated_at, now)

    # scheduleとして登録できるか確認する
    def test_schedule(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now)

        aws_environment_model = AwsEnvironmentModel.objects.create(
            name="test_aws_name",
            aws_account_id="test_account",
            aws_external_id="test_external",
            aws_role="test_role",
            tenant=tenant_model,
            created_at=now,
            updated_at=now)

        schedule_model = ScheduleModel.objects.create(
            name="test_schedule",
            action="test_action",
            params="test_params",
            notification=True,
            aws_environment=aws_environment_model,
            resource_id="test_resource",
            service="test_service",
            region="test_region"
        )

        schedule_model.save()

        # イベントとして取得したときに区別できているか
        event_all = EventModel.all()
        self.assertTrue(isinstance(event_all[0], ScheduleModel))

        # Scheduleとして取得したときに区別できているか
        schedule_all = ScheduleModel.all()
        self.assertTrue(isinstance(schedule_all[0], ScheduleModel))

    # AWSを削除したときに紐づくスケジュールが削除されることを確認する
    def test_delete_cascade_aws(self):
        now = datetime.now()
        tenant_model = TenantModel.objects.create(
            tenant_name="test_tenant",
            created_at=now,
            updated_at=now)

        aws_environment_model = AwsEnvironmentModel.objects.create(
            name="test_aws_name",
            aws_account_id="test_account",
            aws_external_id="test_external",
            aws_role="test_role",
            tenant=tenant_model,
            created_at=now,
            updated_at=now)

        schedule_model = ScheduleModel.objects.create(
            name="test_schedule",
            action="test_action",
            params="test_params",
            notification=True,
            aws_environment=aws_environment_model,
            resource_id="test_resource",
            service="test_service",
            region="test_region"
        )

        schedule_model.save()
        event_all = EventModel.all()
        self.assertEqual(event_all.count(), 1)

        aws = AwsEnvironmentModel.objects.get(name="test_aws_name")
        aws.delete()

        event_all = EventModel.all()
        self.assertEqual(event_all.count(), 0)
