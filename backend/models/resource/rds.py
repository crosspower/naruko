from django.conf import settings
from datetime import timedelta
from . import resource


class Rds(resource.Resource):
    METRICS = {
        "CPUUtilization": "CPU使用率",
        "FreeableMemory": "メモリ空容量",
        "ReadIOPS": "ディスク読取回数",
        "WriteIOPS": "ディスク書込回数",
        "NetworkReceiveThroughput": "読込スループット",
        "NetworkTransmitThroughput": "書込スループット",
        "DatabaseConnections": "DBコネクション数",
        "ReplicaLag": "レプリカ遅延秒数"
    }

    def __init__(self, region: str, resource_id: str):
        super().__init__(region, resource_id)
        self.state = None
        self.spec = None
        self.endpoint = None

    def serialize(self, aws=None):
        res = super().serialize(aws)
        res.update(
            {
                "state": self.state,
            }
        )
        return res

    def describe(self, aws):
        from backend.externals.rds import Rds
        return Rds(aws, self.region).describe_instance(self.resource_id)

    def fetch_backups(self, aws):
        from backend.externals.rds import Rds
        return Rds(aws, self.region).describe_db_snapshots(self.resource_id)

    def create_backup(self, aws, **kwargs):
        from backend.externals.rds import Rds
        return Rds(aws, self.region).create_db_snapshot(self.resource_id)

    @staticmethod
    def get_id_name():
        return "DBInstanceIdentifier"

    @staticmethod
    def get_service_name():
        return "RDS"

    @staticmethod
    def get_instance_resource_name():
        return 'rds:db'

    @staticmethod
    def convert_instance_arn(arn) -> str:
        arn_parts = arn.split(":")  # ["arn", "aws", "service", "region", "account_id", "'db'", "id"]
        resource_id = arn_parts[-1]

        return resource_id

    @staticmethod
    def get_namespace():
        return "AWS/RDS"

    @staticmethod
    def get_metrics():
        return Rds.METRICS.keys()

    @staticmethod
    def get_metrics_japanese(metrics: str):
        return Rds.METRICS.get(metrics, metrics)


class Snapshot:

    def __init__(self, snapshot_id, state, created_at):
        self.id = snapshot_id
        self.state = state
        # 時刻はUTCでくる
        self.created_at = created_at

    def serialize(self):
        return {
            "id": self.id,
            "state": self.state,
            "created_at": self.created_at
        }
