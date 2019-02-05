from rest_framework import serializers
from backend.models import OperationLogModel


class OperationLogModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLogModel
        fields = '__all__'


class OperationLogModelSerializerDetail(serializers.ModelSerializer):
    from backend.serializers.user_model_serializer import UserModelSerializer
    from backend.serializers.tenant_model_serializer import TenantModelSerializer
    tenant = TenantModelSerializer()
    executor = UserModelSerializer()

    class Meta:
        model = OperationLogModel
        fields = '__all__'
