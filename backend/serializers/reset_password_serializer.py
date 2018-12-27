from rest_framework import serializers
from backend.models import UserModel, TenantModel


class ResetPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = (
            'id',
            'email',
        )

    def validate_email(self, value):
        if self.instance and UserModel.objects.exclude(pk=self.instance.pk).filter(email=value):
            raise serializers.ValidationError("user model with this email already exists.")