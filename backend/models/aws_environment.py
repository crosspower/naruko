from django.db import models
from backend.models.soft_deletion_model import SoftDeletionModel
from backend.models.tenant import TenantModel
from django.dispatch import receiver
from django.db.models.signals import pre_save


# AWS環境モデルクラス
class AwsEnvironmentModel(SoftDeletionModel):

    class Meta:
        db_table = 'aws_environment'
        unique_together = ('aws_account_id', 'deleted')

    name = models.CharField(max_length=200)
    aws_account_id = models.CharField(max_length=200)
    aws_role = models.CharField(max_length=200)
    aws_external_id = models.CharField(max_length=200)
    tenant = models.ForeignKey('TenantModel', on_delete=models.CASCADE, related_name='aws_environments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_belong_to_tenant(self, tenant):
        return self.tenant_id == tenant.id

    @staticmethod
    @receiver(pre_save, sender=TenantModel)
    def tenant_soft_delete_cascade(instance: TenantModel, **kwargs):
        if instance.deleted:
            for aws in instance.aws_environments.all():
                aws.delete()
