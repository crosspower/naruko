from backend.externals.external_aws_client import ExternalAwsClient
from backend.models import Resource
from backend.models.resource.rds import Snapshot
import uuid


class Rds(ExternalAwsClient):

    NARUKO_SNAPSHOT_NAME = 'NARUKO-{id}-{random}'

    def _service_name(self):
        return 'rds'

    def describe_instance(self, instance_id: str):
        response = self.client.describe_db_instances(
            DBInstanceIdentifier=instance_id
        )

        instance = response['DBInstances'][0]

        instance_state = instance.get('DBInstanceStatus')

        resource = Resource.get_service_resource(self.region, self._service_name(), instance_id)

        resource.state = instance_state
        resource.name = instance_id

        return resource

    def describe_db_snapshots(self, instance_id: str):
        # Auroraの場合クラスターからスナップショットを作成する
        instance = self.client.describe_db_instances(DBInstanceIdentifier=instance_id)['DBInstances'][0]
        cluster = instance.get("DBClusterIdentifier")

        if cluster:
            snapshots = []
            response = self.client.describe_db_cluster_snapshots(
                DBClusterIdentifier=cluster
            )
            for snapshot in response["DBClusterSnapshots"]:
                snapshots.append(
                    Snapshot(
                        snapshot_id=snapshot["DBClusterSnapshotIdentifier"],
                        state=snapshot["Status"],
                        created_at=snapshot.get("SnapshotCreateTime")
                    )
                )
        else:
            response = self.client.describe_db_snapshots(
                DBInstanceIdentifier=instance_id
            )

            snapshots = []
            for snapshot in response["DBSnapshots"]:
                snapshots.append(
                    Snapshot(
                        snapshot_id=snapshot["DBSnapshotIdentifier"],
                        state=snapshot["Status"],
                        created_at=snapshot.get("SnapshotCreateTime")
                    )
                )

        return snapshots

    def create_db_snapshot(self, instance_id: str):
        snapshot_name = Rds.NARUKO_SNAPSHOT_NAME.format(id=instance_id,
                                                        random=str(uuid.uuid4()))

        # Auroraの場合クラスターからスナップショットを作成する
        instance = self.client.describe_db_instances(DBInstanceIdentifier=instance_id)['DBInstances'][0]
        cluster = instance.get("DBClusterIdentifier")

        if cluster:
            self.client.create_db_cluster_snapshot(
                DBClusterSnapshotIdentifier=snapshot_name,
                DBClusterIdentifier=cluster
            )
        else:
            self.client.create_db_snapshot(
                DBSnapshotIdentifier=snapshot_name,
                DBInstanceIdentifier=instance_id
            )

        return snapshot_name
