from django.test import TestCase
from django.urls.resolvers import URLResolver, RegexPattern


class UrlsTestCase(TestCase):

    def setUp(self):
        pass

    # "/"にアクセスしたときHomePageViewが呼ばれることを確認する
    def test_access_index(self):
        url_resolver = URLResolver(RegexPattern(''), "backend.urls")
        resolve = url_resolver.resolve('/')
        self.assertEqual(resolve.func.__name__, "HomePageView")

    # "auth/"にアクセスしたときobtain_jwt_tokenが呼ばれることを確認する
    def test_access_auth(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/auth/')
        self.assertEqual(resolve.func.__name__, "ObtainJSONWebToken")

    # "auth/verify/"にアクセスしたときverify_jwt_tokenが呼ばれることを確認する
    def test_access_auth_verify(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/auth/verify/')
        self.assertEqual(resolve.func.__name__, "VerifyJSONWebToken")

    # "auth/refresh/"にアクセスしたときverify_jwt_tokenが呼ばれることを確認する
    def test_access_auth_refresh(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/auth/refresh/')
        self.assertEqual(resolve.func.__name__, "RefreshJSONWebToken")

    # "auth/reset/"にアクセスしたときUsersInCompanyModelViewSetが呼ばれることを確認する
    def test_access_reset_password(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/auth/reset/')
        self.assertEqual(resolve.func.__name__, "reset_password")

    # "notify/"にアクセスしたときnotifyが呼ばれることを確認する
    def test_access_notify(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/notify/')
        self.assertEqual(resolve.func.__name__, "notify")

    # "event/"にアクセスしたときevent_executeが呼ばれることを確認する
    def test_access_event(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/event/')
        self.assertEqual(resolve.func.__name__, "event_execute")

    # "tenants/"にアクセスしたときCompanyModelViewSetが呼ばれることを確認する
    def test_access_tenants(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/')
        self.assertEqual(resolve.func.__name__, "TenantModelViewSet")

    # "tenants/pk/users/"にアクセスしたときUsersInCompanyModelViewSetが呼ばれることを確認する
    def test_access_users_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/1/users/')
        self.assertEqual(resolve.func.__name__, "UserModeViewSet")

    # "tenants/pk/aws-environments/"にアクセスしたときAwsEnvironmentModelViewSetが呼ばれることを確認する
    def test_access_awsenvs_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/1/aws-environments/')
        self.assertEqual(resolve.func.__name__, "AwsEnvironmentModelViewSet")

    # "tenants/pk/aws-environments/1/regions/region/documents/"にアクセスしたときDocumentViewSetが呼ばれることを確認する
    def test_access_documents_in_awsenvs_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/1/aws-environments/1/regions/region/documents/')
        self.assertEqual(resolve.func.__name__, "DocumentViewSet")

    # "tenants/pk/aws-environments/1/resources/"にアクセスしたときResourceViewSetが呼ばれることを確認する
    def test_access_instances_in_awsenvs_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/1/aws-environments/1/resources/')
        self.assertEqual(resolve.func.__name__, "ResourceViewSet")

    # "tenants/pk/aws-environments/1/regions/region/service/service/resources/id/monitor/"にアクセスしたときUsersInCompanyModelViewSetが呼ばれることを確認する
    def test_access_monitors_in_resources_in_awsenvs_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve(
            'api/tenants/1/aws-environments/1/regions/ap-northeast-1/services/ec2/resources/i-123456789/monitors/')
        self.assertEqual(resolve.func.__name__, "MonitorViewSet")

    # "tenants/pk/notification-destinations/"にアクセスしたときNotificationDestinationViewSetが呼ばれることを確認する
    def test_access_dest_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/1/notification-destinations/')
        self.assertEqual(resolve.func.__name__, "NotificationDestinationViewSet")

    # "tenants/pk/notification-groups/"にアクセスしたときNotificationGroupViewSetが呼ばれることを確認する
    def test_access_group_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/1/notification-groups/')
        self.assertEqual(resolve.func.__name__, "NotificationGroupViewSet")

    # "tenants/pk/logs/"にアクセスしたときOperationLogModelViewSetが呼ばれることを確認する
    def test_access_logs_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve('api/tenants/1/logs/')
        self.assertEqual(resolve.func.__name__, "OperationLogModelViewSet")

    # "tenants/pk/aws-environments/1/resources/1/schedules/"にアクセスしたときScheduleViewSetが呼ばれることを確認する
    def test_access_schedule_in_resources_in_awsenvs_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve(
            'api/tenants/1/aws-environments/1/regions/ap-northeast-1/services/ec2/resources/i-123456789/schedules/')
        self.assertEqual(resolve.func.__name__, "ScheduleViewSet")

    # "tenants/pk/aws-environments/1/regions/region/service/service/instances/id/backups/"にアクセスしたときBackupViewSetが呼ばれることを確認する
    def test_access_backups_in_resources_in_awsenvs_in_tenant(self):
        url_resolver = URLResolver(RegexPattern(''), "config.urls")
        resolve = url_resolver.resolve(
            'api/tenants/1/aws-environments/1/regions/ap-northeast-1/services/ec2/resources/i-123456789/backups/')
        self.assertEqual(resolve.func.__name__, "BackupViewSet")
