describe('lib/httpClient/tenant', () => {
  it('getUsers', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1

    const axiosMock = {
      get: jest.fn()
    }

    tenant(axiosMock).getUsers(tenantId)

    expect(axiosMock.get).toHaveBeenCalledWith(`/api/tenants/${tenantId}/users/`)
    done()
  })

  it('deleteUser', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const userId = 1

    const axiosMock = {
      delete: jest.fn()
    }

    tenant(axiosMock).deleteUser(tenantId, userId)

    expect(axiosMock.delete).toHaveBeenCalledWith(`/api/tenants/${tenantId}/users/${userId}/`)
    done()
  })

  it('addUser', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const name = 'test'
    const email = 'test@test.com'
    const password = 'testpassword'
    const role = 1
    const aws_environments = [1, 2]

    const axiosMock = {
      post: jest.fn()
    }

    const data = {
      name,
      email,
      password,
      role,
      aws_environments
    }

    tenant(axiosMock).addUser(tenantId, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/users/`, data)
    done()
  })

  it('editUser', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const userId = 1
    const tenantId = 1
    const name = 'test'
    const email = 'test@test.com'
    const password = 'testpassword'
    const role = 1
    const aws_environments = [1, 2]

    const axiosMock = {
      put: jest.fn()
    }

    const data = {
      name,
      email,
      password,
      role,
      aws_environments
    }

    tenant(axiosMock).editUser(tenantId, userId, data)

    expect(axiosMock.put).toHaveBeenCalledWith(`/api/tenants/${tenantId}/users/${userId}/`, data)
    done()
  })

  it('getResources', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'test'
    const cancelToken = 'cancelToken'

    const axiosMock = {
      get: jest.fn()
    }

    tenant(axiosMock).getResources(cancelToken, tenantId, aws_environments, region)

    expect(axiosMock.get).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/resources/?region=${region}`, {cancelToken: cancelToken})
    done()
  })

  it('getTenants', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const axiosMock = {
      get: jest.fn()
    }

    tenant(axiosMock).getTenants()

    expect(axiosMock.get).toHaveBeenCalledWith(`/api/tenants/`)
    done()
  })

  it('addTenant', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenant_name = 'test'
    const email = 'test@test.com'
    const tel = '03-1234-1234'
    const username = 'testuser'
    const userEmail = 'useremail@test.com'

    const axiosMock = {
      post: jest.fn()
    }

    const data = {
      tenant: {
        tenant_name,
        email,
        tel
      },
      user: {
        name: username,
        email: userEmail
      }
    }

    tenant(axiosMock).addTenant(data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/`, data)
    done()
  })

  it('editTenant', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const tenant_name = 'test'
    const email = 'test@test.com'
    const tel = '03-1234-1234'

    const axiosMock = {
      put: jest.fn()
    }

    const data = {
      tenant_name,
      email,
      tel
    }

    tenant(axiosMock).editTenant(tenantId, data)

    expect(axiosMock.put).toHaveBeenCalledWith(`/api/tenants/${tenantId}/`, data)
    done()
  })

  it('deleteTenant', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1

    const axiosMock = {
      delete: jest.fn()
    }

    tenant(axiosMock).deleteTenant(tenantId)

    expect(axiosMock.delete).toHaveBeenCalledWith(`/api/tenants/${tenantId}/`)
    done()
  })

  it('addAwsAccount', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const name = 'aws account name'
    const aws_account_id = 'id'
    const aws_role = 'roleName'
    const aws_external_id = 'externalId'

    const axiosMock = {
      post: jest.fn()
    }

    const data = {
      name,
      aws_account_id,
      aws_role,
      aws_external_id
    }

    tenant(axiosMock).addAwsAccount(tenantId, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/`, data)
    done()
  })

  it('editAwsAccount', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const id = 1
    const name = 'aws account name'

    const axiosMock = {
      put: jest.fn()
    }

    const data = {
      name
    }

    tenant(axiosMock).editAwsAccount(tenantId, id, data)

    expect(axiosMock.put).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${id}/`, data)
    done()
  })

  it('deleteAwsAccount', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const id = 1

    const axiosMock = {
      delete: jest.fn()
    }

    tenant(axiosMock).deleteAwsAccount(tenantId, id)

    expect(axiosMock.delete).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${id}/`)
    done()
  })

  it('getNotificationDestinations', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1


    const axiosMock = {
      get: jest.fn()
    }

    tenant(axiosMock).getNotificationDestinations(tenantId)

    expect(axiosMock.get).toHaveBeenCalledWith(`/api/tenants/${tenantId}/notification-destinations/`)
    done()
  })

  it('addNotificationDestination', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1

    const data = {
      name: 'name',
      type: 'email',
      address: 'test@test.com'
    }

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).addNotificationDestination(tenantId, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/notification-destinations/`, data)
    done()
  })

  it('deleteNotificationDestination', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1

    const desinationId = 12

    const axiosMock = {
      delete: jest.fn()
    }

    tenant(axiosMock).deleteNotificationDestination(tenantId, desinationId)

    expect(axiosMock.delete).toHaveBeenCalledWith(`/api/tenants/${tenantId}/notification-destinations/${desinationId}/`)
    done()
  })

  it('getNotificationGroups', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1


    const axiosMock = {
      get: jest.fn()
    }

    tenant(axiosMock).getNotificationGroups(tenantId)

    expect(axiosMock.get).toHaveBeenCalledWith(`/api/tenants/${tenantId}/notification-groups/`)
    done()
  })

  it('addNotificationGroup', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1

    const data = {
      name: 'name',
      aws_environments: [1, 2, 3],
      destinations: [1, 2, 3]
    }

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).addNotificationGroup(tenantId, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/notification-groups/`, data)
    done()
  })

  it('editNotificationGroup', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const groupId = 1

    const data = {
      name: 'name',
      aws_environments: [1, 2, 3],
      destinations: [1, 2, 3]
    }

    const axiosMock = {
      put: jest.fn()
    }

    tenant(axiosMock).editNotificationGroup(tenantId, groupId, data)

    expect(axiosMock.put).toHaveBeenCalledWith(`/api/tenants/${tenantId}/notification-groups/${groupId}/`, data)
    done()
  })

  it('deleteNotificationGroup', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1

    const groupId = 12

    const axiosMock = {
      delete: jest.fn()
    }

    tenant(axiosMock).deleteNotificationGroup(tenantId, groupId)

    expect(axiosMock.delete).toHaveBeenCalledWith(`/api/tenants/${tenantId}/notification-groups/${groupId }/`)
    done()
  })

  it('addMonitor', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'

    const data = {
      metric_name: 'metric name',
      values: {
        caution: 70,
        danger: 80
      },
      enabled: true,
      period: 300,
      evaluation_period: 1,
      statistic: 'GreaterThanOrEqualToThreshold'
    }

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).addMonitor(tenantId, aws_environments, region, service, resourceId, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/monitors/`, data)
    done()
  })

  it('startEc2Instance', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).startEc2Instance(tenantId, aws_environments, region, service, resourceId)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/start/`)
    done()
  })

  it('stopEc2Instance', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).stopEc2Instance(tenantId, aws_environments, region, service, resourceId)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/stop/`)
    done()
  })

  it('rebootEc2Instance', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).rebootEc2Instance(tenantId, aws_environments, region, service, resourceId)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/reboot/`)
    done()
  })

  it('createResourceBackup', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'

    const data = {
      no_reboot: false
    }

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).createResourceBackup(tenantId, aws_environments, region, service, resourceId, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/backups/`, data)
    done()
  })

  it('getSchedules', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'

    const axiosMock = {
      get: jest.fn()
    }

    tenant(axiosMock).getSchedules(tenantId, aws_environments, region, service, resourceId)

    expect(axiosMock.get).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/`)
    done()
  })

  it('addSchedule', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'

    const data = {
      name: "test",
      is_active: true,
      action: "START",
      schedule_expression: "cron(0 15 L * ? *)",
      params: {},
      notification: true
    }

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).addSchedule(tenantId, aws_environments, region, service, resourceId, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/`, data)
    done()
  })

  it('editSchedule', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'
    const scheduleId = '123'

    const data = {
      name: "test",
      is_active: true,
      action: "START",
      schedule_expression: "cron(0 15 L * ? *)",
      params: {},
      notification: true
    }

    const axiosMock = {
      put: jest.fn()
    }

    tenant(axiosMock).editSchedule(tenantId, aws_environments, region, service, resourceId, scheduleId, data)

    expect(axiosMock.put).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/${scheduleId}/`, data)
    done()
  })

  it('deleteSchedule', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'
    const scheduleId = '123'

    const axiosMock = {
      delete: jest.fn()
    }

    tenant(axiosMock).deleteSchedule(tenantId, aws_environments, region, service, resourceId, scheduleId)

    expect(axiosMock.delete).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/schedules/${scheduleId}/`)
    done()
  })

  it('getMonitorGraph', (done) => {
    const tenant = require('@/lib/httpClient/tenant').default

    const tenantId = 1
    const aws_environments = 1
    const region = 'ap-northeast1'
    const service = 'ec2'
    const resourceId = 'i-1234567890'
    const metricName = 'testmetric'

    const data = {
      start_time: "2018-12-14T14:07:28+09:00",
      end_time: "2018-12-21T14:07:28+09:00",
      period: 300,
      stat: "Average"
    }

    const axiosMock = {
      post: jest.fn()
    }

    tenant(axiosMock).getMonitorGraph(tenantId, aws_environments, region, service, resourceId, metricName, data)

    expect(axiosMock.post).toHaveBeenCalledWith(`/api/tenants/${tenantId}/aws-environments/${aws_environments}/regions/${region}/services/${service}/resources/${resourceId}/monitors/${metricName}/graph/`, data)
    done()
  })

})
