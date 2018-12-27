from rest_framework import serializers
from backend.models import AwsEnvironmentModel


class AwsEnvironmentModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwsEnvironmentModel
        fields = '__all__'


class AwsEnvironmentModelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwsEnvironmentModel
        fields = '__all__'
        read_only_fields = ('aws_account_id', 'aws_role', 'aws_external_id', 'tenant_id')


class AwsEnvironmentModelGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwsEnvironmentModel
        exclude = ('aws_external_id',)


class AwsEnvironmentModelGetDetailSerializer(serializers.ModelSerializer):
    from backend.serializers.tenant_model_serializer import TenantModelSerializer

    tenant = TenantModelSerializer()

    class Meta:
        model = AwsEnvironmentModel
        fields = (
            'id',
            'name',
            'aws_account_id',
            'aws_role',
            'tenant',
            'created_at',
            'updated_at'
        )
