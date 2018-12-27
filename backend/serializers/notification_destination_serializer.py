from rest_framework import serializers
from backend.models import NotificationDestinationModel, EmailDestination


# 通知先ベース
class NotificationDestinationModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationDestinationModel
        fields = (
            'id',
            'name',
            'tenant',
            'created_at',
            'updated_at'
        )


class NotificationDestinationModelDetailSerializer(serializers.ModelSerializer):

    from backend.serializers.tenant_model_serializer import TenantModelSerializer

    tenant = TenantModelSerializer()

    class Meta:
        model = EmailDestination
        fields = (
            'id',
            "name",
            "tenant",
            'created_at',
            'updated_at'
        )


# EMAIL
class EmailDestinationModelSerializer(serializers.ModelSerializer):
    type = serializers.CharField(read_only=True, default="email")

    class Meta(NotificationDestinationModelSerializer.Meta):
        model = EmailDestination
        NotificationDestinationModelSerializer.Meta.fields += (
            'type',
            'address',
        )


class EmailDestinationModelDetailSerializer(NotificationDestinationModelDetailSerializer):
    type = serializers.CharField(read_only=True, default="email")

    class Meta(NotificationDestinationModelDetailSerializer.Meta):
        model = EmailDestination
        NotificationDestinationModelDetailSerializer.Meta.fields += (
            'type',
            'address',
        )


# 共通メソッド
def serialize_destinations_detail(destinations: list):
    """
    通知先モデルを通知方法にしたがってシリアライズする
    :param destinations:
    :return: シリアライズ結果
    """
    dest_types = {
        EmailDestination: EmailDestinationModelDetailSerializer
    }

    return [dest_types[type(dest)](dest).data for dest in destinations]


def serialize_destination(destination: NotificationDestinationModel):
    dest_types = {
        EmailDestination: EmailDestinationModelSerializer
    }

    return dest_types[type(destination)](destination).data


def get_serializer(destination: dict):
    dest_types = {
        "email": EmailDestinationModelSerializer
    }

    return dest_types[destination["type"]](data=destination)
