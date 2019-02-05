# backend/urls.py
from django.urls import re_path
from backend.views import views, tenant_model_view_set, user_model_view_set, aws_model_view_set, \
    resource_view_set, monitor_view_set, notification_destination_model_view_set, notification_group_view_set,\
    schedule_view_set, backup_view_set, operation_log_model_view_set, document_model_view_set
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r'tenants', tenant_model_view_set.TenantModelViewSet, base_name='tenants')

tenant_router = routers.NestedSimpleRouter(router, r'tenants', lookup='tenant')
tenant_router.register(r'users', user_model_view_set.UserModeViewSet)
tenant_router.register(r'aws-environments', aws_model_view_set.AwsEnvironmentModelViewSet,
                       base_name='aws-environments')
tenant_router.register(r'notification-destinations',
                       notification_destination_model_view_set.NotificationDestinationViewSet,
                       base_name='notification-destinations')
tenant_router.register(r'notification-groups',
                       notification_group_view_set.NotificationGroupViewSet,
                       base_name='notification-groups')
tenant_router.register(r'logs', operation_log_model_view_set.OperationLogModelViewSet, base_name='logs')

aws_router = routers.NestedSimpleRouter(tenant_router, r'aws-environments', lookup='aws_env')
aws_router.register(r'resources', resource_view_set.ResourceViewSet, base_name='resources')
aws_router.register(r'regions', resource_view_set.RegionViewSet, base_name='regions')

region_router = routers.NestedSimpleRouter(aws_router, r'regions', lookup='region')
region_router.register(r'services', resource_view_set.ServiceViewSet, base_name=r'services')
region_router.register(r'documents', document_model_view_set.DocumentViewSet, base_name=r'documents')

service_router = routers.NestedSimpleRouter(region_router, r'services', lookup='service')
service_router.register(r'resources', resource_view_set.ResourceViewSet, base_name=r'resources')

resource_router = routers.NestedSimpleRouter(service_router, r'resources', lookup='resource')
resource_router.register(r'monitors', monitor_view_set.MonitorViewSet, base_name='monitors')
resource_router.register(r'schedules', schedule_view_set.ScheduleViewSet, base_name='schedules')
resource_router.register(r'backups', backup_view_set.BackupViewSet, base_name='backups')

urlpatterns = [
    re_path('^.*$', views.HomePageView.as_view()),
]
