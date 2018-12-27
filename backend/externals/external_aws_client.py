import boto3
from backend.models.aws_environment import AwsEnvironmentModel
from backend.decorators import timed_cache


class ExternalAwsClient:

    def __init__(self, aws_environment: AwsEnvironmentModel, region: str):
        # STSからアクセス情報取得
        result = self._build_role(
            aws_environment.aws_account_id,
            aws_environment.aws_role,
            aws_environment.aws_external_id
        )
        credentials = result['Credentials']

        # セッション取得
        session = self._build_session(
            credentials['AccessKeyId'],
            credentials['SecretAccessKey'],
            credentials['SessionToken']
        )

        # サービスクライアント取得
        self.client = self._build_client(
            session,
            self._service_name(),
            region
        )
        self.region = region
        self.aws = aws_environment

    @staticmethod
    @timed_cache(hours=1)
    def _build_role(aws_account_id, aws_role, aws_external_id, retry_count=1):
        try:
            return boto3.client('sts').assume_role(
                RoleArn='arn:aws:iam::%(accountId)s:role/%(roleName)s' %
                        {'accountId': aws_account_id, 'roleName': aws_role},
                RoleSessionName="session",
                ExternalId=aws_external_id)
        except KeyError as e:
            if retry_count >= 3:
                raise e
            retry_count += 1
            return ExternalAwsClient._build_role(aws_account_id, aws_role, aws_external_id, retry_count)

    @staticmethod
    @timed_cache(hours=1)
    def _build_session(aws_access_key_id, aws_secret_access_key, aws_session_token):
        return boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )

    @staticmethod
    @timed_cache(hours=1)
    def _build_client(session, service_name, region):
        return session.client(
            service_name=service_name,
            region_name=region
        )

    @staticmethod
    def _service_name():
        # return 'service_name' e.g. 'ec2'
        raise NotImplementedError

    @staticmethod
    def convert_tag(target_tag_list: list, key_name: str = "Key", value_name: str = "Value") -> dict:
        """
        以下の配列を
        [{'Key': key_value. 'Value': value_value}, ...]
         辞書に変換する
        {'key_value': 'value_value', ...}

        :param target_tag_list:
        :param key_name:
        :param value_name:
        :return:
        """

        return {elem[key_name]: elem[value_name] for elem in target_tag_list}