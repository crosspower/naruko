from django.db import models
from backend.models.soft_deletion_model import SoftDeletionModel


# テナントモデルクラス
class TenantModel(SoftDeletionModel):

    class Meta:
        db_table = 'tenant'

    tenant_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    tel = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
