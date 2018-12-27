from rest_framework import serializers
from backend.models import TenantModel
from backend.validators.phone_number import PhoneNumber


class TenantModelSerializer(serializers.ModelSerializer):
    tel = serializers.CharField(validators=[PhoneNumber()])

    class Meta:
        model = TenantModel
        fields = (
            'id',
            'tenant_name',
            'email',
            'tel',
            'created_at',
            'updated_at'
        )


class TenantModelDetailSerializer(serializers.ModelSerializer):
    from backend.serializers.aws_environment_model_serializer import AwsEnvironmentModelGetSerializer

    aws_environments = AwsEnvironmentModelGetSerializer(many=True)
    tel = serializers.CharField(validators=[PhoneNumber()])

    class Meta:
        model = TenantModel
        fields = (
            'id',
            'tenant_name',
            'email',
            'tel',
            'aws_environments',
            'created_at',
            'updated_at'
        )
