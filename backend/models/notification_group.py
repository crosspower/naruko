from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from backend.models.soft_deletion_model import SoftDeletionModel
from backend.models.notification_destination import NotificationDestinationModel
from backend.models.aws_environment import AwsEnvironmentModel
from backend.models.tenant import TenantModel


# 通知グループモデルクラス
class NotificationGroupModel(SoftDeletionModel):

    class Meta:
        db_table = 'notification_group'

    name = models.CharField(max_length=50)
    destinations = models.ManyToManyField(NotificationDestinationModel, related_name="notification_groups")
    aws_environments = models.ManyToManyField(AwsEnvironmentModel, related_name="notification_groups")
    tenant = models.ForeignKey('TenantModel', on_delete=models.CASCADE, related_name='notification_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    @receiver(pre_save, sender=TenantModel)
    def company_soft_delete_cascade(instance: TenantModel, **kwargs):
        if instance.deleted:
            for notification_group in instance.notification_groups.all():
                notification_group.delete()
