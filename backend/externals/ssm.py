from backend.externals.external_aws_client import ExternalAwsClient
from backend.models import Document, Parameter
import time


class Ssm(ExternalAwsClient):

    def _service_name(self):
        return 'ssm'

    def send_command(self, command):
        parameters = command.document.parameters
        res = self.client.send_command(
            InstanceIds=[command.target.resource_id],
            DocumentName=command.document.name,
            Parameters={param.key: [param.value] for param in parameters if param.value is not None}
        )

        command_id = res["Command"]["CommandId"]

        invocations = []

        # コマンドの実行結果が取れるまで繰り返し
        # コマンド送信直後は結果が取れないことがある
        while not invocations:
            # 1秒ごとに結果を取りに行く
            time.sleep(1)

            invocations = self.client.list_command_invocations(
                CommandId=command_id,
                Details=True
            ).get("CommandInvocations")

            # ステータスが実行中なら取り直す
            if invocations and invocations[0]["CommandPlugins"][0]["Status"] == "InProgress":
                invocations = []

        return invocations[0]["CommandPlugins"][0]["Output"]

    def list_documents(self):
        # 最初はTokenなし
        response = self.client.list_documents(
            Filters=[dict(Key='DocumentType', Values=['Command'])]
        )
        token = response.get("NextToken")

        yield self._build_documents(response["DocumentIdentifiers"])

        # Tokenがあれば次ページを返す
        while token:
            response = self.client.list_documents(
                NextToken=token,
                Filters=[dict(Key='DocumentType', Values=['Command'])]
            )
            token = response.get("NextToken")
            yield self._build_documents(response["DocumentIdentifiers"])

    @staticmethod
    def _build_documents(documents: list):
        return [Document(name=doc_dict["Name"]) for doc_dict in documents]

    def describe_document(self, document_name):
        response = self.client.describe_document(
            Name=document_name
        )

        document_dict = response["Document"]

        return Document(
            name=document_dict["Name"],
            parameters=[Parameter(
                key=param["Name"],
                description=param["Description"]
            ) for param in document_dict["Parameters"]]
        )

    def has_ssm_agent(self, ec2):
        response = self.client.describe_instance_information()

        return ec2.resource_id in [info["InstanceId"] for info in response["InstanceInformationList"]]
