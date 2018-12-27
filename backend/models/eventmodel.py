from django.db import models
from polymorphic.models import PolymorphicModel
from backend.models.soft_deletion_model import SoftDeletionModel
from backend.models.aws_environment import AwsEnvironmentModel
from django.dispatch import receiver
from django.db.models.signals import pre_save


class EventModel(PolymorphicModel, SoftDeletionModel):

    class Meta:
        db_table = "event"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def all(cls):
        return cls.objects.all().filter(deleted=0)

    @classmethod
    def get(cls, pk):
        query_set = cls.objects.filter(id=pk).filter(deleted=0)
        if not query_set:
            raise models.ObjectDoesNotExist("id: {}".format(pk))
        return query_set[0]


class ScheduleModel(EventModel, SoftDeletionModel):

    class Meta:
        db_table = "schedule"

    name = models.CharField(max_length=200)
    action = models.CharField(max_length=200)
    params = models.CharField(max_length=200, blank=True, null=True)
    notification = models.BooleanField()
    aws_environment = models.ForeignKey('AwsEnvironmentModel', on_delete=models.CASCADE, related_name='schedules')
    resource_id = models.CharField(max_length=200)
    service = models.CharField(max_length=50)
    region = models.CharField(max_length=50)

    @staticmethod
    @receiver(pre_save, sender=AwsEnvironmentModel)
    def aws_soft_delete_cascade(instance: AwsEnvironmentModel, **kwargs):
        if instance.deleted:
            for schedule in instance.schedules.all():
                schedule.delete()
