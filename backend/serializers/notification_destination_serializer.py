from rest_framework import serializers
from backend.models import NotificationDestinationModel, EmailDestination, TelephoneDestination
from backend.validators.phone_number import PhoneNumber


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
        fields = NotificationDestinationModelDetailSerializer.Meta.fields + (
            'type',
            'address',
        )


class EmailDestinationModelDetailSerializer(serializers.ModelSerializer):
    type = serializers.CharField(read_only=True, default="email")

    class Meta(NotificationDestinationModelDetailSerializer.Meta):
        model = EmailDestination
        fields = NotificationDestinationModelDetailSerializer.Meta.fields + (
            'type',
            'address',
        )


# Telephone
class TelephoneDestinationModelSerializer(serializers.ModelSerializer):
    type = serializers.CharField(read_only=True, default="telephone")
    phone_number = serializers.CharField(validators=[PhoneNumber()])

    class Meta(NotificationDestinationModelSerializer.Meta):
        model = TelephoneDestination
        fields = NotificationDestinationModelDetailSerializer.Meta.fields + (
            'type',
            'phone_number',
        )


class TelephoneDestinationModelDetailSerializer(serializers.ModelSerializer):
    type = serializers.CharField(read_only=True, default="telephone")
    phone_number = serializers.CharField(validators=[PhoneNumber()])

    class Meta(NotificationDestinationModelDetailSerializer.Meta):
        model = TelephoneDestination
        fields = NotificationDestinationModelDetailSerializer.Meta.fields + (
            'type',
            'phone_number',
        )


# 共通メソッド
def serialize_destinations_detail(destinations: list):
    """
    通知先モデルを通知方法にしたがってシリアライズする
    :param destinations:
    :return: シリアライズ結果
    """
    dest_types = {
        EmailDestination: EmailDestinationModelDetailSerializer,
        TelephoneDestination: TelephoneDestinationModelDetailSerializer
    }

    return [dest_types[type(dest)](dest).data for dest in destinations]


def serialize_destination(destination: NotificationDestinationModel):
    dest_types = {
        EmailDestination: EmailDestinationModelSerializer,
        TelephoneDestination: TelephoneDestinationModelSerializer
    }

    return dest_types[type(destination)](destination).data


def get_serializer(destination: dict):
    dest_types = {
        "email": EmailDestinationModelSerializer,
        "telephone": TelephoneDestinationModelSerializer
    }

    return dest_types[destination["type"]](data=destination)
