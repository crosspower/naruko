from django.db import models
from django.db.models.query import QuerySet


class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted=0)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeletionModel(models.Model):
    deleted = models.IntegerField(default=0)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted = self.pk
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()


class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        for instance in self:
            instance.delete()
        return len(self)

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()
