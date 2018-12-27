from Crypto.PublicKey import RSA
from Crypto.Util.asn1 import DerSequence
from base64 import b64decode, standard_b64decode
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from django.conf import settings
from backend.models import AwsEnvironmentModel
import boto3
import requests


class Sns:

    TOPIC_NAME = settings.SNS_TOPIC_NAME
    ALLOW_ACTIONS = [
        "Publish"
    ]

    def __init__(self, region: str=None, arn: str=None):
        if arn:
            arn_parts = arn.split(":")  # ["arn", "aws", "sns", "region", "account_id", "id"]
            self.client = boto3.client('sns', region_name=arn_parts[3])
            self.arn = arn
        elif region:
            self.client = boto3.client('sns', region_name=region)
            self.arn = [topic for topic in self.client.list_topics().get('Topics', [])
                        if Sns.TOPIC_NAME in topic["TopicArn"]][0]["TopicArn"]

    def add_permission(self, aws: AwsEnvironmentModel):
        self.client.add_permission(
            TopicArn=self.arn,
            Label=aws.aws_account_id,
            AWSAccountId=[aws.aws_account_id],
            ActionName=Sns.ALLOW_ACTIONS
        )

    def confirm_subscription(self, token):
        self.client.confirm_subscription(
            TopicArn=self.arn,
            Token=token,
        )

    @staticmethod
    def verify_notification(notification_data):
        notification_signing_input_key = [
            "Message",
            "MessageId",
            "Subject",
            "SubscribeURL",
            "Timestamp",
            "Token",
            "TopicArn",
            "Type",
        ]

        sign_input = "".join([
                "%s\n%s\n" % (k, notification_data.get(k))
                for k in notification_signing_input_key
                if k in notification_data
        ])

        res = requests.get(notification_data["SigningCertURL"])
        public_key = res.text

        b64der = ''.join(public_key.split('\n')[1:][:-2])
        cert = DerSequence()
        cert.decode(b64decode(b64der))

        tbs_certificate = DerSequence()
        tbs_certificate.decode(cert[0])

        subject_public_key_info = tbs_certificate[6]

        pub = RSA.importKey(subject_public_key_info)

        verifier = PKCS1_v1_5.new(pub)

        sig = standard_b64decode(notification_data['Signature'])
        sign_input = sign_input.encode('utf8')

        dig = SHA.new(sign_input)

        return verifier.verify(dig, sig)
