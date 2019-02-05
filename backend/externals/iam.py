from backend.externals.external_aws_client import ExternalAwsClient
from backend.exceptions import InvalidCrossAccount


class Iam(ExternalAwsClient):
    REQUIRED_ACTIONS = [
        'cloudwatch:PutMetricAlarm',
        'tag:GetResources',
        'cloudwatch:DescribeAlarms',
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:RebootInstances",
        "ec2:DescribeInstances",
        "rds:DescribeDBInstances",
        "elasticloadbalancing:DescribeLoadBalancers",
        "ec2:CreateImage",
        "rds:CreateDBSnapshot",
        "ec2:DescribeImages",
        "rds:DescribeDBSnapshots",
        "rds:CreateDBClusterSnapshot",
        "rds:DescribeDBClusterSnapshots",
        "ssm:SendCommand",
        "ssm:ListCommandInvocations",
        "ssm:ListDocuments",
        "ssm:DescribeDocument",
        "ssm:DescribeInstanceInformation"
    ]

    def _service_name(self):
        return 'iam'

    def validate_role(self, aws_account_id, aws_role):
        role_arn = 'arn:aws:iam::%(accountId)s:role/%(roleName)s' % {'accountId': aws_account_id, 'roleName': aws_role}
        results = self.client.simulate_principal_policy(PolicySourceArn=role_arn,
                                                        ActionNames=Iam.REQUIRED_ACTIONS)
        for result in results['EvaluationResults']:
            if result['EvalDecision'] != 'allowed':
                raise InvalidCrossAccount('action "{}" is {}.'.format(result['EvalActionName'], result['EvalDecision']))
