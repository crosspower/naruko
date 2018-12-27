from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework import status
from backend.models.event.cloudwatchevent import CloudWatchEvent
from backend.models.eventmodel import ScheduleModel, EventModel
from backend.externals.events import Events
from backend.models.resource.resource import Resource
from backend.models.user import UserModel
from backend.models.aws_environment import AwsEnvironmentModel
from backend.models.role import RoleModel
from enum import Enum
import json
import importlib


class Event:

    def __init__(self, event_model, cloudwatchevent: CloudWatchEvent):
        self.event_model = event_model
        self.cloudwatchevent = cloudwatchevent

    def serialize(self):
        return {
            "id": self.event_model.id,
            "is_active": self.cloudwatchevent.is_active,
            "schedule_expression": self.cloudwatchevent.schedule_expression,
            "created_at": self.event_model.created_at,
            "updated_at": self.event_model.updated_at
        }

    def execute(self):
        self._execute_view(self._build_request())

    def _build_request(self) -> Request:
        request = Request(HttpRequest())
        request.user = self._get_executor()
        params = self._add_params()
        if params:
            request._full_data = params

        return request

    def _add_params(self):
        return None

    def _get_executor(self) -> UserModel:
        raise NotImplementedError

    def _execute_view(self, request: Request):
        raise NotImplementedError


class Schedule(Event):

    def __init__(self, schedule_model: ScheduleModel, cloudwatchevent: CloudWatchEvent):
        # ParamsがJSON形式であるか
        if schedule_model.params:
            json.loads(schedule_model.params)
        super().__init__(schedule_model, cloudwatchevent)

    def serialize(self):
        serialize = super().serialize()
        serialize.update(
            {
                "name": self.event_model.name,
                "action": self.event_model.action,
                "notification": self.event_model.notification,
                "params": json.loads(self.event_model.params) if self.event_model.params else None,
                "resource": self.event_model.resource_id,
                "service": self.event_model.service,
                "region": self.event_model.region
            }
        )
        return serialize

    def _get_executor(self):
        return UserModel.objects.get(
            tenant=self.event_model.aws_environment.tenant,
            role_id=RoleModel.SCHEDULER_ID
        )

    def _execute_view(self, request: Request):
        # イベントのアクションを特定する
        action = Schedule.Actions[self.event_model.action]
        request.method = action.http_method

        view_class = getattr(importlib.import_module(action.module), action.view)
        view_func = getattr(view_class(), action.method_name)
        response = view_func(request, **action.params_dict(self))

        # 通知設定がされていれば通知を行う
        if self.event_model.notification:
            for group in self.event_model.aws_environment.notification_groups.filter(deleted=0):
                for dest in group.destinations.filter(deleted=0):
                    dest.result_schedule(self, status.is_success(response.status_code))

    def _add_params(self):
        return json.loads(self.event_model.params)

    class Actions(Enum):

        START = ("backend.views.resource_view_set", "ResourceViewSet", "post", "start", dict(
            tenant_id="tenant_pk",
            aws_env_id="aws_env_pk",
            region="region_pk",
            service="service_pk",
            resource="pk"
        ))
        STOP = ("backend.views.resource_view_set", "ResourceViewSet", "post", "stop", dict(
            tenant_id="tenant_pk",
            aws_env_id="aws_env_pk",
            region="region_pk",
            service="service_pk",
            resource="pk"
        ))
        REBOOT = ("backend.views.resource_view_set", "ResourceViewSet", "post", "reboot", dict(
            tenant_id="tenant_pk",
            aws_env_id="aws_env_pk",
            region="region_pk",
            service="service_pk",
            resource="pk"
        ))
        BACKUP = ("backend.views.backup_view_set", "BackupViewSet", "post", "create", dict(
            tenant_id="tenant_pk",
            aws_env_id="aws_env_pk",
            region="region_pk",
            service="service_pk",
            resource="resource_pk"
        ))

        def __new__(cls, module, view, http_method, method_name, params):
            obj = object.__new__(cls)
            obj.module = module
            obj.view = view
            obj.http_method = http_method
            obj.method_name = method_name
            obj.params = params
            return obj

        def params_dict(self, schedule):
            params_dict = dict(
                tenant_id=schedule.event_model.aws_environment.tenant.id,
                aws_env_id=schedule.event_model.aws_environment.id,
                region=schedule.event_model.region,
                service=schedule.event_model.service,
                resource=schedule.event_model.resource_id
            )
            return {self.params[key]: params_dict[key] for key in self.params}


class ScheduleFactory:

    @staticmethod
    def create(name: str,
               is_active: bool,
               action: str,
               notification: bool,
               schedule_expression: str,
               params: dict,
               resource_id: str,
               region: str,
               service: str,
               aws_id: int,
               event_id=None):
        json_dump_params = json.dumps(params) if params else params
        database = ScheduleModel(
            name=name,
            action=action,
            notification=notification,
            params=json_dump_params,
            resource_id=resource_id,
            service=service.lower(),
            region=region,
            aws_environment_id=aws_id
        )
        if event_id:
            target_model = ScheduleModel.get(pk=event_id)
            database.id = event_id
            database.created_at = target_model.created_at

        aws = CloudWatchEvent(
            schedule_expression=schedule_expression,
            is_active=is_active,
        )

        return Schedule(database, aws)


class EventRepository:

    NARUKO_EVENT_NAME = "NARUKO-{event_id}"

    EVENT_CLASSES = {
        type(ScheduleModel()): Schedule
    }

    @staticmethod
    def save(event: Event):
        # DBへの保存
        event.event_model.save()

        # CloudWatchEventの保存
        event.cloudwatchevent.name = EventRepository.NARUKO_EVENT_NAME.format(event_id=event.event_model.id)
        return Events().save_event(event)

    @staticmethod
    def fetch_schedules_by_resource(resource: Resource, aws: AwsEnvironmentModel):
        # DBから該当するリソースのスケジュールを取得
        database_data_list = ScheduleModel.objects.filter(
            resource_id=resource.resource_id,
            service=resource.get_service_name().lower(),
            region=resource.region,
            aws_environment=aws
        ).filter(deleted=0)

        # AWSからCloudWatchEventを取得
        cloudwatchevents = Events().list_rules()

        response = []
        for database in database_data_list:
            name = EventRepository.NARUKO_EVENT_NAME.format(event_id=database.id)
            target_cloudwatchevent = [c for c in cloudwatchevents if c.name == name]
            if target_cloudwatchevent:
                response.append(Schedule(database, target_cloudwatchevent[0]))
            else:
                # DBだけにあるデータは削除する
                database.delete()

        return response

    @staticmethod
    def delete(pk: int):
        # AWSからCloudWatchEventを削除
        database = EventModel.get(pk=pk)
        Events().delete_event(EventRepository.NARUKO_EVENT_NAME.format(event_id=database.id))

        # DBから該当するイベントを削除
        database.delete()

    @staticmethod
    def get(pk: int):
        database = EventModel.get(pk=pk)

        aws = Events().describe_event(EventRepository.NARUKO_EVENT_NAME.format(event_id=database.id))

        return EventRepository.EVENT_CLASSES[type(database)](database, aws)
