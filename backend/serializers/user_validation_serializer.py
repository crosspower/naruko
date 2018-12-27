from rest_framework import serializers
from backend.models import UserModel, RoleModel, AwsEnvironmentModel


class UserModelValidationSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=RoleModel.objects.filter())
    aws_environments = serializers.PrimaryKeyRelatedField(queryset=AwsEnvironmentModel.objects.filter(), many=True)

    class Meta:
        model = UserModel
        fields = (
            'id',
            'email',
            'name',
            'role',
            'aws_environments',
            'created_at',
            'updated_at'
        )
