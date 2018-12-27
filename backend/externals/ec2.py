from backend.externals.external_aws_client import ExternalAwsClient
from backend.models import Resource
from backend.models.resource.ec2 import AmiImage
import uuid


class Ec2(ExternalAwsClient):

    NARUKO_AMI_NAME = 'NARUKO-{id}-{random}'
    NARUKO_AMI_NAME_PREFIX = 'NARUKO-{id}-'

    def _service_name(self):
        return 'ec2'

    def start_instances(self, instance_ids: list):
        self.client.start_instances(
            InstanceIds=instance_ids
        )

    def reboot_instances(self, instance_ids: list):
        self.client.reboot_instances(
            InstanceIds=instance_ids
        )

    def stop_instances(self, instance_ids: list):
        self.client.stop_instances(
            InstanceIds=instance_ids
        )

    def describe_instance(self, instance_id: str):
        response = self.client.describe_instances(
            Filters=[
                {'Name': 'instance-id', 'Values': [instance_id]}
            ]
        )

        instance = response['Reservations'][0]['Instances'][0]
        tag = self.convert_tag(instance.get("Tags", []))
        name = tag.get("Name", instance_id)

        instance_state = instance.get('State', {}).get('Name')

        resource = Resource.get_service_resource(self.region, self._service_name(), instance_id)

        resource.name = name
        resource.state = instance_state

        return resource

    def describe_resource_images(self, instance_id):
        # AMI名では前方一致ができないため所有者で絞る
        response = self.client.describe_images(
            Owners=[self.aws.aws_account_id]
        )
        prefix = Ec2.NARUKO_AMI_NAME_PREFIX.format(id=instance_id)
        ami_images = []

        # AMI名でフィルタリングして処理する
        res_images = [res_image for res_image in response["Images"] if res_image["Name"].startswith(prefix)]
        for image in res_images:
            ami_images.append(
                AmiImage(
                    image_id=image["ImageId"],
                    name=image["Name"],
                    state=image["State"],
                    created_at=image.get("CreationDate")
                )
            )

        return ami_images

    def create_image(self, instance_id: str, no_reboot: bool):
        res = self.client.create_image(
            InstanceId=instance_id,
            Name=Ec2.NARUKO_AMI_NAME.format(
                id=instance_id,
                random=str(uuid.uuid4())
            ),
            NoReboot=no_reboot
        )

        return res['ImageId']
