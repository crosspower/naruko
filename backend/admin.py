from django.contrib import admin
from backend.models import UserModel, AwsEnvironmentModel, TenantModel, RoleModel, \
    NotificationGroupModel, NotificationDestinationModel, EmailDestination

admin.site.register(UserModel)
admin.site.register(AwsEnvironmentModel)
admin.site.register(TenantModel)
admin.site.register(RoleModel)
admin.site.register(NotificationDestinationModel)
admin.site.register(NotificationGroupModel)
admin.site.register(EmailDestination)
