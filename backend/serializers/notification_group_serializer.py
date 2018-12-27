from rest_framework import serializers
from backend.models import NotificationGroupModel, NotificationDestinationModel, AwsEnvironmentModel


# 通知グループ
class NotificationGroupModelSerializer(serializers.ModelSerializer):
    destinations = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=NotificationDestinationModel.all())
    aws_environments = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=AwsEnvironmentModel.objects.filter())

    class Meta:
        model = NotificationGroupModel
        fields = (
            'id',
            'name',
            'tenant',
            'destinations',
            'aws_environments',
            'created_at',
            'updated_at'
        )


class NotificationGroupModelDetailSerializer(serializers.ModelSerializer):

    from backend.serializers.tenant_model_serializer import TenantModelSerializer
    from backend.serializers.aws_environment_model_serializer import AwsEnvironmentModelGetSerializer

    tenant = TenantModelSerializer()
    aws_environments = AwsEnvironmentModelGetSerializer(many=True, allow_null=True)
    destinations = serializers.SerializerMethodField()

    class Meta:
        model = NotificationGroupModel
        fields = (
            'id',
            'name',
            'destinations',
            'tenant',
            'aws_environments',
            'created_at',
            'updated_at'
        )

    def get_destinations(self, instance: NotificationGroupModel):
        from backend.serializers.notification_destination_serializer import serialize_destination
        return [serialize_destination(dest) for dest in instance.destinations.all().filter(deleted=0)]
