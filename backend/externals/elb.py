from backend.externals.external_aws_client import ExternalAwsClient
from backend.models import Resource


class Elb(ExternalAwsClient):

    def _service_name(self):
        return 'elb'

    def describe_load_balancer(self, name: str):
        # response = self.client.describe_load_balancers(
        #     LoadBalancerNames=[name]
        # )
        #
        # load_balancer = response['LoadBalancerDescriptions'][0]

        resource = Resource.get_service_resource(self.region, self._service_name(), name)

        resource.name = name
        return resource


class Elbv2(ExternalAwsClient):

    def _service_name(self):
        return 'elbv2'

    def describe_load_balancer(self, name: str):
        # response = self.client.describe_load_balancers(
        #     Names=[name]
        # )
        #
        # load_balancer = response['LoadBalancers'][0]

        resource = Resource.get_service_resource(self.region, 'elb', name)

        resource.name = name
        return resource
