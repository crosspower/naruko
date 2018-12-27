from django.core.exceptions import PermissionDenied
from backend.models import UserModel, TenantModel, RoleModel, AwsEnvironmentModel
from backend.exceptions import InvalidRoleException, InvalidPasswordException
from backend.logger import NarukoLogging


class ControlUserUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    def fetch_users(self, request_user: UserModel, tenant: TenantModel):
        self.logger.info("START: fetch_users")
        if not request_user.is_belong_to_tenant(tenant):
            raise PermissionDenied("request user can't fetch users. user_id:{} tenant_id: {}".
                                   format(request_user.id, tenant.id))

        if not request_user.can_control_other_user():
            raise PermissionDenied("request user can't fetch users. id:{}".format(request_user.id))

        # スケジューラーは一覧に表示しない
        response = [user_model for user_model in UserModel.objects.filter(tenant=tenant).
                    exclude(role_id=RoleModel.SCHEDULER_ID)]
        self.logger.info("END: fetch_users")
        return response

    def delete_user(self, request_user: UserModel, user: UserModel):
        self.logger.info("START: delete_user")
        if not request_user.is_belong_to_tenant(user.tenant):
            raise PermissionDenied("request user can't fetch users. user_id:{} tenant_id: {}".
                                   format(request_user.id, user.tenant.id))

        if not request_user.can_delete_user(user):
            raise PermissionDenied("request user can't delete user. id:{}".format(request_user.id))

        user.delete()
        self.logger.info("END: delete_user")

    def create_user(self, request_user: UserModel, user: UserModel, aws_envs: AwsEnvironmentModel, password: str):
        self.logger.info("START: create_user")
        if not request_user.is_belong_to_tenant(user.tenant):
            raise PermissionDenied("request user can't fetch users. user_id:{} tenant_id: {}".
                                   format(request_user.id, user.tenant.id))

        # 作成しようとしているユーザーを作成できるロールを持つか
        if not request_user.can_save_user(user):
            raise PermissionDenied("request user can't create user. id:{}".format(request_user.id))

        # パスワードを暗号化して登録
        if not user.set_password(password):
            raise InvalidPasswordException("invalid password. {}".format(password))

        user.save()

        # ユーザーにAWS環境を登録
        if not request_user.realignment_aws_environments(user, aws_envs):
            raise PermissionDenied("request user can't control aws environments. id:{}".format(request_user.id))

        self.logger.info("END: create_user")
        return user

    def update_user(self, post_user_data: dict, request_user: UserModel, target_user: UserModel):
        self.logger.info("START: update user")
        if not request_user.is_belong_to_tenant(target_user.tenant):
            raise PermissionDenied("request user can't fetch users. user_id:{} tenant_id: {}".
                                   format(request_user.id, target_user.tenant.id))

        # 更新しようとしているユーザーを更新できるロールを持つか
        if not request_user.can_save_user(target_user):
            raise PermissionDenied("request user can't update role. id:{}".format(request_user.id))

        role = RoleModel.objects.get(id=post_user_data["role"])

        # 指定されたロールに変更可能か
        if not target_user.can_changed_role(role):
            raise InvalidRoleException("can't change role user: {}".format(target_user.id))

        target_user.email = post_user_data["email"]
        target_user.name = post_user_data["name"]
        target_user.role = role

        # 更新後のロールに更新できるロールを持つか
        if not request_user.can_save_user(target_user):
            raise PermissionDenied

        # 変更があればパスワードを暗号化して登録
        if post_user_data["password"] and not target_user.set_password(post_user_data["password"]):
            raise InvalidPasswordException("password is invalid.")

        # AWS環境の洗い替え
        aws_environments = AwsEnvironmentModel.objects.filter(id__in=post_user_data["aws_environments"]).all()
        if not request_user.realignment_aws_environments(target_user, aws_environments):
            raise PermissionDenied

        # 更新
        target_user.save()
        self.logger.info("END: update user")
        return target_user
