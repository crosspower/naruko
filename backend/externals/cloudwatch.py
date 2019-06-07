from backend.externals.external_aws_client import ExternalAwsClient
from enum import Enum, IntEnum
from backend.models import Resource
from backend.models.monitor import Monitor, MonitorValue
from backend.models.resource.ec2 import Ec2
from backend.models.resource.rds import Rds
from backend.models.resource.elb import Elb
from backend.models.monitor import MonitorGraph


class CloudWatch(ExternalAwsClient):
    NARUKO_ALARM_NAME_PREFIX = 'NARUKO-'
    NARUKO_ALARM_NAME_SPECIFY_INSTANCE = 'NARUKO-{}-{}-'
    NARUKO_ALARM_NAME = 'NARUKO-{}-{}-{}-{}'

    def _service_name(self):
        return 'cloudwatch'

    def get_resources_status(self):
        """
        NARUKOから設定された各アラームを取得し
        インスタンスの状態を返す
         :return:dict:
            {
                "EC2": {"instance_id": "status", ...},
                "RDS": {"instance_id": "status", ...},
                "ELB": {"instance_id": "status", ...}
            }
        """
        alarms_list = [alarms for alarms in self._get_instances_status()]

        response = {"EC2": {}, "RDS": {}, "ELB": {}}
        for alarms in alarms_list:
            for service in CloudWatch.Services:
                response[service.name].update(alarms[service.name])

        return response

    def _get_instances_status(self) -> dict:
        # 最初はTokenなし
        response = self.client.describe_alarms(
                AlarmNamePrefix=CloudWatch.NARUKO_ALARM_NAME_PREFIX,
        )
        token = response.get("NextToken")
        yield self._build_alarm(response["MetricAlarms"])

        # Tokenがあれば次ページを返す
        while token:
            response = self.client.describe_alarms(
                AlarmNamePrefix=CloudWatch.NARUKO_ALARM_NAME_PREFIX,
                NextToken=token
            )
            token = response.get("NextToken")
            yield self._build_alarm(response["MetricAlarms"])

    @staticmethod
    def _build_alarm(alarms) -> dict:
        res_alarms = {"EC2": {}, "RDS": {}, "ELB": {}}
        for alarm in alarms:
            # サービスを特定する
            service_instance = CloudWatch._specify_service(alarm["Namespace"])
            res_alarm = res_alarms[service_instance.get_service_name()]
            # サービスのIDを取得
            dimensions = CloudWatch.convert_tag(alarm["Dimensions"], key_name="Name")
            instance_id = dimensions[service_instance.get_id_name()]
            # アラームからインスタンスの状態を把握する
            alarm_kind = alarm["AlarmName"].rsplit('-', 1)[1]  # DANGER or CAUTION
            state = alarm["StateValue"]
            # 前のループでセットされたステータスを確認する
            instance_alarm = res_alarm.get(instance_id)

            # 初回の場合
            if not instance_alarm:
                # アラームが発生している場合そのままセットする
                if state == CloudWatch.AlarmState.ALARM.value:
                    res_alarm[instance_id] = alarm_kind
                # アラームがなければOK
                else:
                    res_alarm[instance_id] = CloudWatch.InstanceStatus["OK"].name

            # 2回目以降にアラームが発生している場合
            elif state == CloudWatch.AlarmState.ALARM.value:
                # statusの優先度により更新するかどうか決める
                if CloudWatch.InstanceStatus[alarm_kind] > CloudWatch.InstanceStatus[res_alarm[instance_id]]:
                    res_alarm[instance_id] = alarm_kind
                # 発生していない場合初回の状態を維持する

        return res_alarms

    def describe_resource_monitors(self, resource: Resource):
        res = self.client.describe_alarms(
            AlarmNamePrefix=CloudWatch.NARUKO_ALARM_NAME_SPECIFY_INSTANCE.format(
                resource.get_service_name(),
                resource.resource_id
            )
        )
        # metricごとにアラームをグルーピングする
        grouped_alarms = dict()
        for alarm in res["MetricAlarms"]:
            # metric = alarm["Metrics"][0]["MetricStat"]["Metric"]
            alarms_by_metric = grouped_alarms.get(alarm["MetricName"], [])
            if alarms_by_metric:
                alarms_by_metric.append(alarm)
            else:
                alarms_by_metric.append(alarm)
                grouped_alarms[alarm["MetricName"]] = alarms_by_metric

        # alarmをmonitorに
        monitors = []
        for metric in resource.get_metrics():
            # metricの全レベルのアラーム
            metric_alarms = grouped_alarms.get(metric, [{}])

            # 初期値：アラームが未設定の場合に使用する
            monitor_status = Monitor.MonitorStatus.UNSET
            monitor_values = {level.value: None for level in MonitorValue.MonitorLevel}

            # メトリクスにアラームが設定されている場合
            if metric_alarms[0]:
                alarms_state = {state.name: [] for state in CloudWatch.AlarmState}
                for metric_alarm in metric_alarms:
                    # 監視レベルの値を振り分ける
                    level = metric_alarm["AlarmName"].rsplit('-', 1)[1]
                    monitor_values[level.lower()] = metric_alarm["Threshold"]

                    # アラームのステータスごとに監視レベルを振り分ける
                    alarms_state[metric_alarm["StateValue"]].append(level)

                # アラームが発生しているもので最も監視レベルが高いステータスを取得する
                # アラームが発生していない場合はOK
                monitor_status = Monitor.MonitorStatus.max(
                    [Monitor.MonitorStatus[level.upper()] for level in alarms_state[CloudWatch.AlarmState.ALARM.name]]
                )

            monitors.append(
                Monitor(
                    metric_name=metric,
                    values=monitor_values,
                    enabled=metric_alarms[0].get("ActionsEnabled"),
                    period=metric_alarms[0].get("Period"),
                    evaluation_period=metric_alarms[0].get("EvaluationPeriods"),
                    statistic=metric_alarms[0].get("Statistic"),
                    status=monitor_status
                )
            )

        return monitors

    def put_metric_alarms(self, resource: Resource, topic_arn: str):
        """
        アラームを設定する
        一つのメトリクスに対しNARUKOで取り扱う監視レベルの数だけアラームを設定する
        最も低いレベルのアラームには復旧時のトリガーを設定する

        :param resource:
        :param topic_arn:
        :return:
        """
        monitor = resource.monitors[0]
        for monitor_value in monitor.monitor_values:
            params = dict(
                AlarmName=CloudWatch.NARUKO_ALARM_NAME.format(
                    resource.get_service_name(),
                    resource.resource_id,
                    monitor.metric.name,
                    monitor_value.level.name
                ),
                ActionsEnabled=monitor.enabled,
                AlarmActions=[topic_arn],
                MetricName=monitor.metric.name,
                Namespace=resource.get_namespace(),
                Statistic=monitor.statistic,
                Dimensions=[dict(
                    Name=resource.get_id_name(),
                    Value=resource.resource_id
                )],
                Period=monitor.period,
                EvaluationPeriods=1,
                Threshold=monitor_value.value,
                ComparisonOperator=monitor.metric.comparison_operator
            )

            # 最も安全なレベルのアラームには復旧時の通知を設定する
            if monitor_value.level.is_lowest_level():
                params.update(dict(OKActions=[topic_arn]))

            self.client.put_metric_alarm(**params)

    def get_chart(self, monitor_graph: MonitorGraph):

        for graph_data in [graph_data_list for graph_data_list in self._get_chart(monitor_graph)]:
            monitor_graph.timestamps.extend(graph_data["Timestamps"])
            monitor_graph.values.extend(graph_data["Values"])

        return monitor_graph

    def _get_chart(self, monitor_graph: MonitorGraph):
        # 最初はTokenなし
        response = self.get_metric_data(
            monitor_graph=monitor_graph
        )

        token = response.get("NextToken")
        yield response["MetricDataResults"][0]

        # Tokenがあれば次ページを返す
        while token:
            response = self.get_metric_data(
                monitor_graph=monitor_graph,
                token=token
            )
            token = response.get("NextToken")
            yield response["MetricDataResults"][0]

    def get_metric_data(self, monitor_graph: MonitorGraph, token: str = None):
        params = dict(
            MetricDataQueries=[dict(
                Id=monitor_graph.metric_name.lower(),
                MetricStat=dict(
                    Metric=dict(
                        Namespace=monitor_graph.service_name,
                        MetricName=monitor_graph.metric_name,
                        Dimensions=monitor_graph.dimensions
                    ),
                    Period=monitor_graph.period,
                    Stat=monitor_graph.stat
                )
            )],
            StartTime=monitor_graph.start_time,
            EndTime=monitor_graph.end_time,
            ScanBy="TimestampAscending",
            MaxDatapoints=500
        )

        if token:
            params["NextToken"] = token

        response = self.client.get_metric_data(**params)

        return response

    @staticmethod
    def _specify_service(name_space) -> Resource:
        value = CloudWatch.Services[str.replace(name_space, "AWS/", "")].value
        return value

    class AlarmState(Enum):
        OK = 'OK'
        ALARM = 'ALARM'
        INSUFFICIENT_DATA = 'INSUFFICIENT_DATA'

    class InstanceStatus(IntEnum):
        OK = 0
        CAUTION = 1
        DANGER = 2

    class Services(Enum):
        EC2 = Ec2
        RDS = Rds
        ELB = Elb
