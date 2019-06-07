from enum import Enum, IntEnum
from dateutil.parser import parse


class Monitor:

    class MonitorStatus(IntEnum):
        UNSET = -1
        OK = 0
        CAUTION = 1
        DANGER = 2

        @classmethod
        def max(cls, status_list: list, initial=OK):
            res = initial
            for status in status_list:
                res = max(res, status)
            return cls(res)

    def __init__(self,
                 metric_name: str,
                 values: dict,
                 enabled: bool,
                 period: int,
                 evaluation_period: int,
                 statistic: str,
                 status: MonitorStatus =None):
        self.metric = MonitorMetric(metric_name)
        self.monitor_values = [MonitorValue(v, values[v.value]) for v in MonitorValue.MonitorLevel]
        self.enabled = enabled
        self.period = int(period) if period is not None else period
        self.evaluation_period = int(evaluation_period) if evaluation_period is not None else evaluation_period
        self.statistic = statistic
        self.status = status

    def serialize(self):
        return {
            "metric_name": self.metric.name,
            "values": {v.level.value: v.value for v in self.monitor_values},
            "enabled": self.enabled,
            "period": self.period,
            "evaluation_period": self.evaluation_period,
            "statistic": self.statistic,
            "comparison_operator": self.metric.comparison_operator,
            "status": self.status.name if self.status is not None else self.status
        }


class MonitorGraph:

    def __init__(self, start_time: str, end_time: str, period: int, stat: str, metric_name: str):
        self.start_time = parse(start_time)
        self.end_time = parse(end_time)
        self.period = period
        self.stat = stat
        self.metric_name = metric_name
        self.timestamps = []
        self.values = []
        self.service_name = ''
        self.dimensions = []

    def serialize(self):
        return {
            "timestamps": self.timestamps,
            "values": self.values
        }


class MonitorMetric:

    LESS_COMPARISON_METRICS = [
        "FreeableMemory",
        "HealthyHostCount"
    ]

    def __init__(self, name):
        self.name = name
        self.comparison_operator = "LessThanOrEqualToThreshold" \
            if name in MonitorMetric.LESS_COMPARISON_METRICS else "GreaterThanOrEqualToThreshold"


class MonitorValue:

    class MonitorLevel(Enum):
        CAUTION = "caution"
        DANGER = "danger"

        def is_lowest_level(self):
            """
            最も低い（安全な）レベルかどうか

            :return: 最も低い監視レベルであればTrue そうでなければFalse
            """
            return self == self.CAUTION

    def __init__(self, level: MonitorLevel, value: int):
        self.level = level
        self.value = int(value) if value is not None else value

    def serialize(self):
        return {self.level.value: self.value}
