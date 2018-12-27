from backend.externals.external_aws_client import ExternalAwsClient
from backend.models.resource.ec2 import Ec2
from backend.models.resource.rds import Rds
from backend.models.resource.elb import Elb
from enum import Enum


class ResourceGroupTagging(ExternalAwsClient):

    def _service_name(self):
        return "resourcegroupstaggingapi"

    def get_resources(self, aws_services: list) -> list:
        """
        指定されたサービスのインスタンスリソースのタグ情報を返すジェネレータ

        次のページがあれば次のレスポンスを返す
        :param aws_services:
        :return:
        """
        # 最初はTokenなし
        res = self.client.get_resources(
            ResourceTypeFilters=[service.get_instance_resource_name() for service in aws_services]
        )
        token = res["PaginationToken"]
        yield self._build_resources(res["ResourceTagMappingList"])

        # Tokenがあれば次ページを返す
        while token:
            res = self.client.get_resources(
                PaginationToken=token,
                ResourceTypeFilters=[service.get_instance_resource_name() for service in aws_services]
            )
            token = res["PaginationToken"]
            yield self._build_resources(res["ResourceTagMappingList"])

    def _build_resources(self, resource_tag_mapping_list: list) -> list:
        resources = []
        for resource_tag_mapping in resource_tag_mapping_list:
            arn = resource_tag_mapping["ResourceARN"]
            arn_parts = arn.split(":")  # ["arn", "aws", "service", "region", "account_id", "id"]

            service_name = arn_parts[2]
            service = ResourceGroupTagging.ServiceType[service_name].value
            instance_id = service.convert_instance_arn(arn)
            tags = ExternalAwsClient.convert_tag(resource_tag_mapping["Tags"])
            # EC2はNameに該当するタグがなければIDと同じ
            instance_name = tags.get("Name", instance_id) if service_name == "ec2" else instance_id

            resource = service(self.region, instance_id)
            resource.name = instance_name
            resources.append(resource)

        return resources

    class ServiceType(Enum):
        ec2 = Ec2
        rds = Rds
        elasticloadbalancing = Elb


