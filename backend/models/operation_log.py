from django.db import models
from backend.models.soft_deletion_model import SoftDeletionModel
from backend.models.tenant import TenantModel
from backend.models.user import UserModel
from django.dispatch import receiver
from django.db.models.signals import pre_save


# 操作ログモデルクラス
class OperationLogModel(SoftDeletionModel):

    class Meta:
        db_table = 'operation_log'

    tenant = models.ForeignKey('TenantModel', on_delete=models.CASCADE, related_name='operation_logs')
    # 実行者
    executor = models.ForeignKey('UserModel', on_delete=models.SET_NULL, related_name='operation_logs',
                                 null=True, blank=True)
    # 操作内容
    operation = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    @receiver(pre_save, sender=TenantModel)
    def tenant_soft_delete_cascade(instance: TenantModel, **kwargs):
        if instance.deleted:
            for operation_log in instance.operation_logs.all():
                operation_log.delete()

    @staticmethod
    @receiver(pre_save, sender=UserModel)
    def user_soft_delete_set_null(instance: UserModel, **kwargs):
        if instance.deleted:
            for operation_log in instance.operation_logs.all():
                operation_log.executor = None
                operation_log.save()

    @classmethod
    def operation_log(cls, executor_index: int=None, target_method=None, target_arg_index_list: list =None):
        """
        操作ログ書き込み

        :param executor_index: リクエストユーザーの引数のインデックス
        :param target_method: 操作対象を取得するための関数
        :param target_arg_index_list: 呼び出し元のメソッドの引数のインデックス
        :return:
        """
        if target_arg_index_list is None:
            target_arg_index_list = []

        def _decorator(func):
            def wrapper(*args, **kwargs):
                # 実行
                res = func(*args, **kwargs)

                # 実行者を取得
                executor = args[executor_index] if executor_index is not None else None

                # 操作対象の情報を取得
                target_info = target_method.__func__(*(args[index] for index in target_arg_index_list)) if target_method else None

                # ログ書き込み
                cls.objects.create(
                    tenant=executor.tenant if executor else None,
                    executor=executor,
                    operation=func.__name__ + (": " + target_info if target_info else "")
                ).save()
                return res
            return wrapper
        return _decorator
