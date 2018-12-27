from rest_framework import serializers
from backend.models import UserModel, RoleModel, AwsEnvironmentModel


class UserModelUpdateValidationSerializer(serializers.ModelSerializer):

    role = serializers.PrimaryKeyRelatedField(queryset=RoleModel.objects.filter())
    aws_environments = serializers.PrimaryKeyRelatedField(queryset=AwsEnvironmentModel.objects.filter(), many=True)

    email = serializers.EmailField(max_length=200)

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

    def validate_email(self, value):
        if self.instance and UserModel.objects.exclude(pk=self.instance.pk).filter(email=value):
            raise serializers.ValidationError("user model with this email already exists.")
