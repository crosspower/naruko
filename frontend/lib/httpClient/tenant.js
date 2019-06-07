export default function (client) {
  return {
    getTenants() {
      return client.get(`/api/tenants/`)
    },
    getUsers(tenantId) {
      return client.get(`/api/tenants/${tenantId}/users/`)
    },
    addUser(tenantId, data) {
      return client.post(`/api/tenants/${tenantId}/users/`, data)
    },
    editUser(tenantId, userId, data) {
      return client.put(`/api/tenants/${tenantId}/users/${userId}/`, data)
    },
    deleteUser(tenantId, userId) {
      return client.delete(`/api/tenants/${tenantId}/users/${userId}/`)
    },
    getAwsAccount(tenantId) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/`)
    },
    addAwsAccount(tenantId, data) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/`, data)
    },
    editAwsAccount(tenantId, awsAccountId, data) {
      return client.put(`/api/tenants/${tenantId}/aws-environments/${awsAccountId}/`, data)
    },
    getBilling(tenantId,awsAccountId,data){
      return client.post(`/api/tenants/${tenantId}/aws-environments/${awsAccountId}/billing/`,data)
    },
    getResources(cancelToken, tenantId, aws_environments, region) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/resources/?region=${region}`, {
        cancelToken: cancelToken
      })
    },
    getResourceDetail(tenantId, aws_environments, region, service, resourceId) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/`)
    },
    startEc2Instance(tenantId, aws_environments, region, service, resourceId) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/start/`)
    },
    stopEc2Instance(tenantId, aws_environments, region, service, resourceId) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/stop/`)
    },
    rebootEc2Instance(tenantId, aws_environments, region, service, resourceId) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/reboot/`)
    },
    createResourceBackup(tenantId, aws_environments, region, service, resourceId, data) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/backups/`, data)
    },
    getResourceBackups(tenantId, aws_environments, region, service, resourceId) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/backups/`)
    },
    addTenant(data) {
      return client.post(`/api/tenants/`, data)
    },
    editTenant(tenantId, data) {
      return client.put(`/api/tenants/${tenantId}/`, data)
    },
    deleteTenant(tenantId) {
      return client.delete(`/api/tenants/${tenantId}/`)
    },
    deleteAwsAccount(tenantId, awsAccountId) {
      return client.delete(`/api/tenants/${tenantId}/aws-environments/${awsAccountId}/`)
    },
    getMonitors(tenantId, aws_environments, region, service, resourceId) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/monitors/`)
    },
    addMonitor(tenantId, aws_environments, region, service, resourceId, data) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/monitors/`, data)
    },
    getMonitorGraph(tenantId, aws_environments, region, service, resourceId, metricName, data) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/monitors/${metricName}/graph/`, data)
    },
    getNotificationDestinations(tenantId) {
      return client.get(`/api/tenants/${tenantId}/notification-destinations/`)
    },
    addNotificationDestination(tenantId, data) {
      return client.post(`/api/tenants/${tenantId}/notification-destinations/`, data)
    },
    deleteNotificationDestination(tenantId, destinationId) {
      return client.delete(`/api/tenants/${tenantId}/notification-destinations/${destinationId}/`)
    },
    getNotificationGroups(tenantId) {
      return client.get(`/api/tenants/${tenantId}/notification-groups/`)
    },
    addNotificationGroup(tenantId, data) {
      return client.post(`/api/tenants/${tenantId}/notification-groups/`, data)
    },
    editNotificationGroup(tenantId, groupId, data) {
      return client.put(`/api/tenants/${tenantId}/notification-groups/${groupId}/`, data)
    },
    deleteNotificationGroup(tenantId, groupId) {
      return client.delete(`/api/tenants/${tenantId}/notification-groups/${groupId}/`)
    },
    getSchedules(tenantId, aws_environments, region, service, resourceId) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/`)
    },
    addSchedule(tenantId, aws_environments, region, service, resourceId, data) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/`, data)
    },
    editSchedule(tenantId, aws_environments, region, service, resourceId, scheduleId, data) {
      return client.put(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/${scheduleId}/`, data)
    },
    deleteSchedule(tenantId, aws_environments, region, service, resourceId, scheduleId) {
      return client.delete(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/${scheduleId}/`)
    },
    getOperationLog(tenantId) {
      return client.get(`/api/tenants/${tenantId}/logs/`)
    },
    getDocuments(tenantId, aws_environments, region) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/documents/`)
    },
    getDocumentDetail(tenantId, aws_environments, region, documentName) {
      return client.get(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/documents/${documentName}/`)
    },
    runCommand(tenantId, aws_environments, region, service, resourceId, data) {
      return client.post(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/run_command/`, data)
    }
  }
}