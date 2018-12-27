from django.db.models import ObjectDoesNotExist
from backend.models.event.event import EventRepository, ScheduleFactory, ScheduleModel, EventModel
from backend.models import AwsEnvironmentModel, TenantModel, CloudWatchEvent, Schedule, Event, RoleModel, UserModel
from django.test import TestCase
from unittest import mock
from datetime import datetime
import json


class EventTestCase(TestCase):

    @staticmethod
    def _create_user_model(email, name, password, tenant, role):
        now = datetime.now()
        user_model = UserModel(
            email=email,
            name=name,
            password=password,
            tenant=tenant,
            role=role,
            created_at=now,
            updated_at=now
        )
        user_model.save()
        return user_model

    @staticmethod
    def _create_role_model(id, role_name):
        now = datetime.now()
        return RoleModel.objects.create(
            id=id,
            role_name=role_name,
            created_at=now,
            updated_at=now
        )

    @staticmethod
    def _create_schedule_model(name, aws):
        now = datetime.now()
        schedule = ScheduleModel.objects.create(
            name=name,
            action="START",
            params='{"test": "test"}',
            notification=True,
            resource_id="i-01234567890",
            service="ec2",
            region="ap-northeast-1",
            aws_environment=aws,
            created_at=now,
            updated_at=now
        )
        schedule.save()
        return schedule

    @staticmethod
    def _create_aws_env_model(name, aws_account_id, tenant):
        now = datetime.now()
        aws = AwsEnvironmentModel.objects.create(
            name=name,
            aws_account_id=aws_account_id,
            aws_role="test_role",
            aws_external_id="test_external_id",
            tenant=tenant,
            created_at=now,
            updated_at=now
        )
        aws.save()
        return aws

    @staticmethod
    def _create_tenant_model(tenant_name):
        now = datetime.now()
        return TenantModel.objects.create(
            tenant_name=tenant_name,
            created_at=now,
            updated_at=now
        )

    @classmethod
    def setUpClass(cls):
        super(EventTestCase, cls).setUpClass()
        tenant_model1 = cls._create_tenant_model("test_tenant_users_in_tenant_1")
        # Company1に所属するAWS環境の作成
        aws1 = cls._create_aws_env_model("test_name1", "test_aws1", tenant_model1)
        # aws1に所属するスケジュールの作成
        cls._create_schedule_model("test_schedule1", aws1)
        # スケジューラーの作成
        role_model = cls._create_role_model(RoleModel.SCHEDULER_ID, "test_role")
        cls._create_user_model(
            email="test_email",
            name="test_name",
            password="test_password",
            tenant=tenant_model1,
            role=role_model,
        )

    # Repository
    @mock.patch("backend.models.event.event.Events")
    def test_save(self, mock_events: mock.Mock):
        test_event = mock.Mock()

        repository_save = EventRepository.save(test_event)

        test_event.save.asssert_called_once()
        mock_events.return_value.save_event.assert_called_once_with(test_event)
        self.assertEqual(repository_save, mock_events.return_value.save_event.return_value)

    @mock.patch("backend.models.event.event.Events")
    def test_fetch_schedules_by_resource(self, mock_events: mock.Mock):
        mock_resource = mock.Mock()
        mock_resource.resource_id = "i-01234567890"
        mock_resource.get_service_name.return_value = "ec2"
        mock_resource.region = "ap-northeast-1"
        aws = AwsEnvironmentModel.objects.get(name="test_name1")

        list_rules = mock_events.return_value.list_rules
        expected = CloudWatchEvent(name="NARUKO-1", schedule_expression="TEST", is_active=True)
        list_rules.return_value = [
            expected,
            CloudWatchEvent(name="NARUKO-2", schedule_expression="TEST", is_active=True),
            CloudWatchEvent(name="NARUKO-3", schedule_expression="TEST", is_active=True)
        ]

        schedules_by_resource = EventRepository.fetch_schedules_by_resource(mock_resource, aws)

        list_rules.assert_called_once()
        self.assertEqual(len(schedules_by_resource), 1)
        self.assertEqual(schedules_by_resource[0].cloudwatchevent, expected)

    @mock.patch("backend.models.event.event.Events")
    def test_delete(self, mock_events: mock.Mock):

        EventRepository.delete(1)

        mock_events.return_value.delete_event.assert_called_once_with("NARUKO-1")

        with self.assertRaises(ObjectDoesNotExist):
            EventModel.get(pk=1)

    @mock.patch("backend.models.event.event.Events")
    def test_get(self, mock_events: mock.Mock):

        res = EventRepository.get(pk=1)
        mock_events.return_value.describe_event.assert_called_once_with("NARUKO-1")

        self.assertTrue(isinstance(res, Schedule))

    # ScheduleFactory
    def test_schedule_factory_create(self):
        name = "test"
        is_active = True
        action = "test_action"
        notification = True
        schedule_expression = "cron(10 * * * ? *)"
        params = dict(test="test")
        resource_id = "i-01234567890"
        region = "ap-northeast-1"
        service = "ec2"
        aws_id = 1
        res = ScheduleFactory.create(
            name=name,
            is_active=is_active,
            action=action,
            notification=notification,
            schedule_expression=schedule_expression,
            params=params,
            resource_id=resource_id,
            region=region,
            service=service,
            aws_id=aws_id
        )

        self.assertEqual(res.event_model.name, name)
        self.assertEqual(res.event_model.action, action)
        self.assertEqual(res.event_model.notification, notification)
        self.assertEqual(res.event_model.params, json.dumps(params))
        self.assertEqual(res.event_model.resource_id, resource_id)
        self.assertEqual(res.event_model.service, service)
        self.assertEqual(res.event_model.region, region)
        self.assertEqual(res.event_model.aws_environment_id, aws_id)
        self.assertEqual(res.cloudwatchevent.schedule_expression, schedule_expression)
        self.assertEqual(res.cloudwatchevent.is_active, is_active)

    # ScheduleFactory:既存のイベントIDを指定した場合
    def test_schedule_factory_create_update(self):
        name = "test"
        is_active = True
        action = "test_action"
        notification = True
        schedule_expression = "cron(10 * * * ? *)"
        params = dict(test="test")
        resource_id = "i-01234567890"
        region = "ap-northeast-1"
        service = "ec2"
        aws_id = 1
        event_id = 1
        res = ScheduleFactory.create(
            name=name,
            is_active=is_active,
            action=action,
            notification=notification,
            schedule_expression=schedule_expression,
            params=params,
            resource_id=resource_id,
            region=region,
            service=service,
            aws_id=aws_id,
            event_id=event_id
        )

        self.assertEqual(res.event_model.id, event_id)
        self.assertEqual(res.event_model.name, name)
        self.assertEqual(res.event_model.action, action)
        self.assertEqual(res.event_model.notification, notification)
        self.assertEqual(res.event_model.params, json.dumps(params))
        self.assertEqual(res.event_model.resource_id, resource_id)
        self.assertEqual(res.event_model.service, service)
        self.assertEqual(res.event_model.region, region)
        self.assertEqual(res.event_model.aws_environment_id, aws_id)
        self.assertEqual(res.cloudwatchevent.schedule_expression, schedule_expression)
        self.assertEqual(res.cloudwatchevent.is_active, is_active)

    # ScheduleFactory:存在しないイベントIDを指定した場合
    def test_schedule_factory_create_update_not_exist(self):
        name = "test"
        is_active = True
        action = "test_action"
        notification = True
        schedule_expression = "cron(10 * * * ? *)"
        params = dict(test="test")
        resource_id = "i-01234567890"
        region = "ap-northeast-1"
        service = "ec2"
        aws_id = 1
        event_id = -1

        with self.assertRaises(ObjectDoesNotExist):
            ScheduleFactory.create(
                name=name,
                is_active=is_active,
                action=action,
                notification=notification,
                schedule_expression=schedule_expression,
                params=params,
                resource_id=resource_id,
                region=region,
                service=service,
                aws_id=aws_id,
                event_id=event_id
            )

    def test_execute_event(self):
        mock_model = mock.Mock()
        mock_aws = mock.Mock()

        with self.assertRaises(NotImplementedError):
            Event(mock_model, mock_aws).execute()

    def test_execute_schedule(self):
        mock_dest = mock.Mock()
        mock_group = mock.Mock()
        mock_group.destinations.filter.return_value = [mock_dest]

        mock_aws_env = mock.Mock(spec=AwsEnvironmentModel)
        mock_aws_env.tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        mock_aws_env.notification_groups.filter.return_value = [mock_group]

        # scheduleModel mock
        mock_schedule = mock.Mock()
        mock_schedule.params = '{"test": "test"}'
        mock_schedule.action = "START"
        mock_schedule.aws_environment = mock_aws_env
        # cloudwatchevent mock
        mock_aws_cloudwatchevent = mock.Mock()

        # 検証対象実行
        schedule = Schedule(mock_schedule, mock_aws_cloudwatchevent)
        schedule.execute()

        # 通知がされているか
        self.assertTrue(mock_schedule.notification)
        mock_dest.result_schedule.assert_called_once_with(schedule, False)

    def test_execute_schedule_no_notification(self):
        mock_dest = mock.Mock()
        mock_group = mock.Mock()
        mock_group.destinations.filter.return_value = [mock_dest]

        mock_aws_env = mock.Mock(spec=AwsEnvironmentModel)
        mock_aws_env.tenant = TenantModel.objects.get(tenant_name="test_tenant_users_in_tenant_1")
        mock_aws_env.notification_groups.filter.return_value = [mock_group]

        # scheduleModel mock
        mock_schedule = mock.Mock()
        mock_schedule.params = '{"test": "test"}'
        mock_schedule.action = "START"
        mock_schedule.aws_environment = mock_aws_env
        mock_schedule.notification = False
        # cloudwatchevent mock
        mock_aws_cloudwatchevent = mock.Mock()

        # 検証対象実行
        schedule = Schedule(mock_schedule, mock_aws_cloudwatchevent)
        schedule.execute()

        # 通知がされていないか
        self.assertFalse(mock_schedule.notification)
        mock_dest.result_schedule.assert_not_called()
