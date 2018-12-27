from rest_framework import serializers
from backend.models import UserModel


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'id',
            'email',
            'name',
            'tenant',
            'role',
            'created_at',
            'updated_at'
        )


class UserModelDetailSerializer(serializers.ModelSerializer):
    from backend.serializers.role_model_serializer import RoleModelSerializer
    from backend.serializers.tenant_model_serializer import TenantModelSerializer
    from backend.serializers.aws_environment_model_serializer import AwsEnvironmentModelGetSerializer

    tenant = TenantModelSerializer()
    role = RoleModelSerializer()
    aws_environments = AwsEnvironmentModelGetSerializer(many=True)

    class Meta:
        model = UserModel
        fields = (
            'id',
            'email',
            'name',
            'tenant',
            'role',
            'aws_environments',
            'created_at',
            'updated_at'
        )
