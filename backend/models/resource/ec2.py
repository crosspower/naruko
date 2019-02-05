from .resource import Resource


class Ec2(Resource):
    METRICS = {
        "StatusCheckFailed": "死活監視",
        "CPUUtilization": "CPU使用率",
        "DiskReadBytes": "ディスク読込量",
        "DiskWriteBytes": "ディスク書込量",
        "NetworkIn": "ネットワーク受信量",
        "NetworkOut": "ネットワーク送信量"
    }

    def __init__(self, region: str, resource_id: str):
        super().__init__(region, resource_id)
        self.state = None
        self.spec = None
        self.public_ip_address = None
        self.has_ssm_agent = None

    def serialize(self, aws=None):
        res = super().serialize(aws)
        res.update(
            {
                "state": self.state,
                "has_ssm_agent": self.has_ssm_agent
            }
        )
        return res

    def start(self, aws):
        from backend.externals.ec2 import Ec2
        Ec2(aws, self.region).start_instances([self.resource_id])

    def reboot(self, aws):
        from backend.externals.ec2 import Ec2
        Ec2(aws, self.region).reboot_instances([self.resource_id])

    def stop(self, aws):
        from backend.externals.ec2 import Ec2
        Ec2(aws, self.region).stop_instances([self.resource_id])

    def describe(self, aws):
        from backend.externals.ec2 import Ec2
        from backend.externals.ssm import Ssm
        ec2 = Ec2(aws, self.region).describe_instance(self.resource_id)
        ec2.has_ssm_agent = Ssm(aws, self.region).has_ssm_agent(ec2)

        return ec2

    def fetch_backups(self, aws):
        from backend.externals.ec2 import Ec2
        return Ec2(aws, self.region).describe_resource_images(self.resource_id)

    def create_backup(self, aws, no_reboot=True):
        from backend.externals.ec2 import Ec2
        return Ec2(aws, self.region).create_image(self.resource_id, no_reboot)

    @staticmethod
    def get_id_name():
        return "InstanceId"

    @staticmethod
    def get_service_name():
        return "EC2"

    @staticmethod
    def get_instance_resource_name():
        return 'ec2:instance'

    @staticmethod
    def convert_instance_arn(arn) -> str:
        arn_parts = arn.split(":")  # ["arn", "aws", "service", "region", "account_id", "id"]
        resource_id = arn_parts[-1]  # instance/i-123456789012

        return resource_id.split("/")[-1]

    @staticmethod
    def get_namespace():
        return "AWS/EC2"

    @staticmethod
    def get_metrics():
        return Ec2.METRICS.keys()

    @staticmethod
    def get_metrics_japanese(metrics: str):
        return Ec2.METRICS.get(metrics, metrics)


class AmiImage:

    def __init__(self, image_id: str, state: str, name: str, created_at: str):
        self.id = image_id
        self.name = name
        self.state = state
        # 時刻はUTC
        self.created_at = created_at

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "created_at": self.created_at
        }
