class Resource:

    REGION = {
        "US East (N. Virginia)": "バージニア北部",
        "US East (Ohio)": "オハイオ",
        "US West (N. California)": "北カリフォルニア",
        "US West (Oregon)": "オレゴン",
        "Canada (Central)": "中部",
        "EU (Frankfurt)": "フランクフルト",
        "EU (Ireland)": "アイルランド",
        "EU (London)": "ロンドン",
        "EU (Paris)": "パリ",
        "Asia Pacific (Tokyo)": "東京",
        "Asia Pacific (Seoul)": "ソウル",
        "Asia Pacific (Singapore)": "シンガポール",
        "Asia Pacific (Sydney)": "シドニー",
        "Asia Pacific (Mumbai)": "ムンバイ",
        "South America (São Paulo)": "サンパウロ",
    }

    def __init__(self, region: str, resource_id: str):
        self.region = region
        self.resource_id = resource_id
        self.monitors = []
        self.name = None
        self.status = None

    def serialize(self, aws=None):
        return {
            "id": self.resource_id,
            "name": self.name,
            "status": self.status,
            "service": self.get_service_name(),
            "aws_environment": aws.id if aws else None,
            "region": self.region
        }

    def get_region_japanese(self):
        return self.REGION.get(self.region, self.region)

    def describe(self, aws):
        raise NotImplementedError

    def create_backup(self, aws, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_service_resource(region: str, service_type: str, resource_id: str):
        from backend.models.resource.ec2 import Ec2
        from backend.models.resource.rds import Rds
        from backend.models.resource.elb import Elb
        service = {
            "ec2": Ec2,
            "rds": Rds,
            "elb": Elb
        }
        return service[service_type.lower()](region, resource_id)

    @staticmethod
    def get_all_services():
        from backend.models.resource.ec2 import Ec2
        from backend.models.resource.rds import Rds
        from backend.models.resource.elb import Elb

        return [Ec2, Rds, Elb]

    @staticmethod
    def get_id_name():
        raise NotImplementedError

    @staticmethod
    def get_service_name():
        raise NotImplementedError

    @staticmethod
    def get_instance_resource_name():
        raise NotImplementedError

    @staticmethod
    def convert_instance_arn(arn: str):
        raise NotImplementedError

    @staticmethod
    def get_namespace():
        raise NotImplementedError

    @staticmethod
    def get_metrics():
        raise NotImplementedError

    @staticmethod
    def get_metrics_japanese(metrics: str):
        raise NotImplementedError
