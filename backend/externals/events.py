import boto3
from django.conf import settings
from backend.models import CloudWatchEvent
import json


class Events:

    def __init__(self):
        self.client = boto3.client('events', region_name=settings.NARUKO_REGION)

    def list_rules(self):
        response = []
        for rules in self._list_rules():
            response.extend(rules)

        return response

    def _list_rules(self):
        # 最初はTokenなし
        response = self.client.list_rules(NamePrefix='NARUKO-')
        token = response.get("NextToken")
        yield self._build_cloudwatchevent(response["Rules"])

        # Tokenがあれば次ページを返す
        while token:
            response = self.client.list_rules(
                NamePrefix='NARUKO-',
                NextToken=token
            )
            token = response.get("NextToken")
            yield self._build_cloudwatchevent(response["Rules"])

    @staticmethod
    def _build_cloudwatchevent(rules: dict):
        cloudwatchevents = []
        for rule in rules:
            cloudwatchevents.append(CloudWatchEvent(
                name=rule["Name"],
                schedule_expression=rule.get("ScheduleExpression"),
                is_active=rule["State"] == "ENABLED"
            ))
        return cloudwatchevents

    def save_event(self, event):
        # ルール作成
        self.client.put_rule(
            Name=event.cloudwatchevent.name,
            ScheduleExpression=event.cloudwatchevent.schedule_expression,
            State="ENABLED" if event.cloudwatchevent.is_active else "DISABLED"
        )

        # ターゲット作成
        target = dict(
            Id=event.cloudwatchevent.name,
            Arn=settings.EVENT_SNS_TOPIC_ARN,
            Input=json.dumps(dict(id=event.event_model.id))
        )

        self.client.put_targets(
            Rule=event.cloudwatchevent.name,
            Targets=[target]
        )

        return event

    def delete_event(self, event_name):
        # ターゲット削除
        self.client.remove_targets(
            Rule=event_name,
            Ids=[event_name]
        )

        # ルール削除
        self.client.delete_rule(
            Name=event_name
        )

    def describe_event(self, event_name):
        response = self.client.describe_rule(
            Name=event_name
        )

        return CloudWatchEvent(
            name=response["Name"],
            schedule_expression=response["ScheduleExpression"],
            is_active=response["State"] == "ENABLED"
        )
