from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from backend.models.role import RoleModel
from backend.models.tenant import TenantModel
from backend.models.aws_environment import AwsEnvironmentModel
from django.contrib.auth.hashers import make_password
from backend.models.soft_deletion_model import SoftDeletionManager
from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models.deletion import ProtectedError
import re
import string
import random


class UserManager(BaseUserManager, SoftDeletionManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        入力されたメールアドレスとパスワードおよびテナントID、ロールIDでユーザーを作成する
        """
        if not email:
            raise ValueError('The given e_mail must be set')
        email = self.normalize_email(email)
        role = RoleModel.objects.get(id=extra_fields["role"])
        tenant = TenantModel.objects.get(id=extra_fields["tenant"])
        user = self.model(email=email, role=role, tenant=tenant)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        print(extra_fields)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# ユーザーモデルクラス
class UserModel(AbstractBaseUser, PermissionsMixin):

    class Meta:
        db_table = 'user'
        unique_together = ('email', 'deleted')

    email = models.EmailField(max_length=200)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    tenant = models.ForeignKey('TenantModel', on_delete=models.CASCADE, related_name='users')
    role = models.ForeignKey('RoleModel', on_delete=models.PROTECT, related_name='users')
    aws_environments = models.ManyToManyField(AwsEnvironmentModel)
    deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role', 'tenant']
    PASSWORD_PATTERN = r'^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?\d)(?=.*?[!-/:-@[-`{-~])[!-~]{8,200}$'

    def delete(self):
        self.deleted = self.pk
        self.save()

    @staticmethod
    @receiver(pre_save, sender=TenantModel)
    def tenant_soft_delete_cascade(instance: TenantModel, **kwargs):
        if instance.deleted:
            for user in instance.users.all():
                user.delete()

    @staticmethod
    @receiver(pre_save, sender=RoleModel)
    def role_soft_delete_protect(instance: RoleModel, **kwargs):
        if instance.deleted:
            users_all = instance.users.all()
            if users_all:
                raise ProtectedError("role has users.", users_all)

    @staticmethod
    def get_scheduler(tenant: TenantModel):
        return UserModel.objects.get(tenant=tenant, role=RoleModel.objects.get(id=RoleModel.SCHEDULER_ID))

    def is_belong_to_tenant(self, tenant):
        """
        対象のテナントに属しているか
        :param tenant: 確かめたいテナント
        :return: 対象のテナントに属しているか
        """
        return self.tenant_id == tenant.id

    def _is_master(self):
        return self.role.id == RoleModel.MASTER_ID

    def _is_admin(self):
        return self.role.id == RoleModel.ADMIN_ID

    def _is_user(self):
        return self.role.id == RoleModel.USER_ID

    def _is_scheduler(self):
        return self.role.id == RoleModel.SCHEDULER_ID

    def can_control_other_user(self):
        """
        他のユーザーを管理できる権限を持っているか
        :return: 他のユーザーを管理できる権限を持っているか
        """
        return self._is_master() or self._is_admin() or self._is_scheduler()

    def can_save_user(self, user):
        """
        対象のユーザーを保存できるか

        同じテナントに属し権限が適切であれば操作できる

        :param user: 操作対象のユーザー
        :return:
        """
        # スケジューラーは保存できない
        if user._is_scheduler():
            return False

        # 他のテナントのユーザーは操作できない
        if self.tenant.id != user.tenant.id:
            return False

        # 自分自身は操作可能
        if self.id == user.id and self.role.id == user.role.id:
            return True

        # 自身がUSER権限の場合：他のユーザーは操作できない
        if self._is_user():
            return False

        # 自身がMASTERか、操作対象がMASTERでなければ操作可能
        return self._is_master() or not user._is_master()

    def can_delete_user(self, user):
        """
        対象のユーザーを削除できるか

        同じテナントに属し権限が適切であれば操作できる

        :param user:
        :return:
        """
        # スケジューラーは削除できない
        if user._is_scheduler():
            return False

        # 他のテナントのユーザーは操作できない
        if self.tenant.id != user.tenant.id:
            return False

        # 自分自身は削除できない
        if self.id == user.id and self.role.id == user.role.id:
            return False

        # 自身がUSER権限の場合：他のユーザーは削除できない
        if self._is_user():
            return False

        # 自身がMASTERか、操作対象がMASTERでなければ操作可能
        return self._is_master() or not user._is_master()

    def can_changed_role(self, role: RoleModel):
        """
        引数で指定されたロールに変更可能かどうか

        :param role: 変更対象のロール
        :return: 変更対象のロールに変更可能ならばTrue 不可能ならばFalse
        """
        # ユーザーがUSER権限ならば変更可能
        if self._is_user():
            return True

        # ユーザーがADMINかMASTERかSCHEDULERの場合、0人にならないようにする
        return not (
                UserModel.objects.filter(tenant=self.tenant, role=self.role).all().count() == 1
                and self.role != role
        )

    def realignment_aws_environments(self, user, aws_environments):
        """
        指定されたAWS環境に洗い替える

        トランザクション管理は呼び出し元で実施する

        :param user: 変更対象のユーザー
        :param aws_environments:AWS環境
        :return: 洗い替えに成功した場合True 不正なAWS環境を指定された場合False
        """
        # 実行者がUSER権限の場合
        if self._is_user():
            # AWS環境の変更はできない
            if [aws.id for aws in user.aws_environments.all()] != [aws.id for aws in aws_environments.all()]:
                return False

        # 現在のAWS環境との紐づけをすべて削除する
        for aws in user.aws_environments.all():
            user.aws_environments.remove(aws.id)

        # 指定されたAWS環境すべてと紐づける
        for aws_env in aws_environments:
            # ユーザーのテナントに属さないAWS環境は使用できない
            if not aws_env.is_belong_to_tenant(user.tenant):
                return False
            user.aws_environments.add(aws_env)

        return True

    def set_password(self, raw_password):
        """
        パスワードを登録する

        半角英数字記号をそれぞれ1文字以上含み8~200文字で指定する

        :param raw_password:
        :return: パスワード登録に成功した場合True 不正なパスワードを指定された場合False
        """
        match = re.search(self.PASSWORD_PATTERN, raw_password)
        if not match:
            return False
        self.password = make_password(raw_password)
        self._password = raw_password
        return True

    def reset_password(self):
        """
        パスワードをリセットし再設定する

        :return: 新パスワード
        """
        password_chars = string.digits + string.ascii_letters + string.punctuation
        new_password = ''.join(random.choices(password_chars, k=random.randint(8, 200)))

        is_valid_password = False
        while not is_valid_password:
            is_valid_password = self.set_password(new_password)

        return new_password

    def has_aws_env(self, aws):
        """
        指定されたAWS環境を利用できるか

        :param aws:
        :return:
        """
        return aws in self.aws_environments.all()

    def can_control_tenant(self):
        """
        テナントを操作できるか
        :return:
        """
        return self._is_master()

    def can_control_aws(self):
        """
        AWS環境を管理できる権限を持っているか
        :return: AWS環境を管理できる権限を持っているか
        """
        return self._is_master() or self._is_admin() or self._is_scheduler()

    def can_control_notification(self):
        """
        通知を操作できるか
        :return:
        """
        return self._is_master() or self._is_admin() or self._is_scheduler()
