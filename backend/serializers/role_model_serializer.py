from rest_framework import serializers
from backend.models import RoleModel


class RoleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleModel
        fields = (
            'id',
            'role_name',
            'created_at',
            'updated_at'
        )
