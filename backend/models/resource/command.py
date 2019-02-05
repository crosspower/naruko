from backend.models.resource.ec2 import Ec2


class Command:

    def __init__(self, document, target_ec2: Ec2):
        if not isinstance(target_ec2, Ec2):
            raise TypeError(type(target_ec2))

        self.document = document
        self.target = target_ec2
        self.out_put = None

    def run(self, aws):
        from backend.externals.ssm import Ssm
        self.out_put = Ssm(aws_environment=aws, region=self.target.region).send_command(self)

    def serialize(self):
        return dict(
            document=self.document.serialize(),
            target=self.target.serialize(),
            out_put=self.out_put
        )


class Document:

    def __init__(self, name: str, parameters: list=None):
        self.name = name
        self.parameters = parameters if parameters else []

    def serialize(self):
        return dict(
            name=self.name,
            parameters=[params.serialize() for params in self.parameters]
        )


class Parameter:

    def __init__(self, key, value=None, description=None):
        self.key = key
        self.value = value
        self.description = description

    def serialize(self):
        return dict(
            key=self.key,
            value=self.value,
            description=self.description
        )
