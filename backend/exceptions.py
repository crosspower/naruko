class NarukoException(Exception):
    """
    アプリケーション仕様上の例外を示す
    """
    pass


class InvalidRoleException(NarukoException):
    """
    不正なロール操作
    """
    pass


class InvalidPasswordException(NarukoException):
    """
    不正なパスワード操作
    """
    pass


class InvalidEmailException(NarukoException):
    """
    不正なメール
    """
    pass


class InvalidNotificationException(NarukoException):
    """
    不正なSNS通知
    """
    pass


class InvalidCrossAccount(NarukoException):
    """
    不正なクロスアカウント
    """
    pass
