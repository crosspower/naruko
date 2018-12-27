from . import resource
from botocore.exceptions import ClientError


class Elb(resource.Resource):
    METRICS = {
        "Latency": "レイテンシー",
        "RequestCount": "リクエストカウント",
        "HealthyHostCount": "正常EC2数",
        "UnHealthyHostCount": "危険EC2数",
        "HTTPCode_ELB_4XX": "HTTPレスポンスコード(4xx)",
        "HTTPCode_ELB_5XX": "HTTPレスポンスコード(5xx)",
    }

    def __init__(self, region: str, resource_id: str):
        super().__init__(region, resource_id)
        self.dns_name = None
        self.scheme = None

    def serialize(self, aws=None):
        res = super().serialize(aws)
        return res

    def describe(self, aws):
        from backend.externals.elb import Elb, Elbv2
        try:
            return Elbv2(aws, self.region).describe_load_balancer(self.resource_id)
        except ClientError:
            return Elb(aws, self.region).describe_load_balancer(self.resource_id)

    @staticmethod
    def get_id_name():
        return "LoadBalancerName"

    @staticmethod
    def get_service_name():
        return "ELB"

    @staticmethod
    def get_instance_resource_name():
        return 'elasticloadbalancing:loadbalancer'

    @staticmethod
    def convert_instance_arn(arn) -> str:
        arn_parts = arn.split(":")  # ["arn", "aws", "service", "region", "account_id", "id"]

        resource_id = arn_parts[-1]
        resource_id_parts = resource_id.split("/")

        return resource_id_parts[2] if resource_id_parts[1] in ["app", "net"] else resource_id_parts[1]

    @staticmethod
    def get_namespace():
        return "AWS/ELB"

    @staticmethod
    def get_metrics():
        return Elb.METRICS.keys()

    @staticmethod
    def get_metrics_japanese(metrics: str):
        return Elb.METRICS.get(metrics, metrics)
