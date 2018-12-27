from django.db import transaction
from django.conf import settings
from backend.models import UserModel
from backend.externals.ses import Ses
from botocore.exceptions import ClientError
from backend.exceptions import InvalidEmailException
from backend.logger import NarukoLogging


class ResetPasswordUseCase:

    def __init__(self, naruko_logger: NarukoLogging):
        self.logger = naruko_logger.get_logger(__name__)

    @transaction.atomic
    def reset_password(self, user: UserModel):
        self.logger.info("START: reset password")
        # パスワード変更
        reset_password = user.reset_password()
        user.save()

        try:
            # メール送信
            self.logger.info("START: Send mail by SES.")
            self.logger.info("using address. {}".format(settings.SES_ADDRESS))
            ses = Ses(settings.SES_ADDRESS, settings.SES_ADDRESS)
            ses.send_password_reset_mail(user.email, reset_password)
            self.logger.info("END: Send mail by SES.")
        except ClientError as e:
            self.logger.exception(e)
            raise InvalidEmailException

        self.logger.info("END: reset password")
        return user
