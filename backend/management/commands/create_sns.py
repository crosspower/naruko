from django.core.management.base import BaseCommand
from django.conf import settings
import boto3


class Command(BaseCommand):

    NOTIFY_TOPIC_NAME = "NARUKO_NOTIFY"
    SCHEDULE_TOPIC_NAME = "NARUKO_SCHEDULE"

    @staticmethod
    def create_sns_if_not_exists(region, sns_name):
        client = boto3.client('sns', region_name=region)
        response = client.list_topics()
        topics = {topic["TopicArn"].split(":")[-1]: topic["TopicArn"] for topic in response["Topics"]}

        if topics.get(sns_name):
            # すでにトピックが存在する場合
            print("{} exists in {}. Arn is {}.".format(sns_name, region, topics.get(sns_name)))
        else:
            # 存在しない場合は作成する
            res = client.create_topic(
                Name=sns_name
            )
            print("{} is created in {}. Arn is {}.".format(sns_name, region, res["TopicArn"]))

    def handle(self, *args, **options):
        # 通知用トピック作成
        regions = [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "ap-south-1",
            "ap-northeast-2",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
            "ca-central-1",
            "eu-central-1",
            "eu-west-1",
            "eu-west-2",
            "eu-west-3",
            "sa-east-1",
        ]

        for region in regions:
            self.create_sns_if_not_exists(region, Command.NOTIFY_TOPIC_NAME)

        # スケジュール用SNS作成
        self.create_sns_if_not_exists(settings.NARUKO_REGION, Command.SCHEDULE_TOPIC_NAME)
