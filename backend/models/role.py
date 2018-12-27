from django.db import models
from backend.models.soft_deletion_model import SoftDeletionModel


# ロールモデルクラス
class RoleModel(SoftDeletionModel):

    class Meta:
        db_table = 'role'

    id = models.IntegerField(primary_key=True, serialize=False)
    role_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    MASTER_ID = 1
    ADMIN_ID = 2
    USER_ID = 3
    SCHEDULER_ID = 4

