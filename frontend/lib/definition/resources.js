import Enum from '@/lib/definition/enum'

export default new Enum({
  EC2: {
    actions: new Enum({
      start: {
        id: 'start',
        name: '起動'
      },
      stop: {
        id: 'stop',
        name: '停止'
      },
      reboot: {
        id: 'reboot',
        name: '再起動'
      },
      backup: {
        id: 'backup',
        name: 'バックアップ'
      }
    }),
    scheduleActions: new Enum({
      START: {
        id: 'START',
        name: '起動'
      },
      STOP: {
        id: 'STOP',
        name: '停止'
      },
      REBOOT: {
        id: 'REBOOT',
        name: '再起動'
      },
      BACKUP: {
        id: 'BACKUP',
        name: 'バックアップ'
      }
    }),
    infoKeys: new Enum({
      service: {
        id: 'service',
        name: 'サービス'
      },
      id: {
        id: 'id',
        name: 'ID'
      },
      powerStatus: {
        id: 'state',
        name: '電源ステータス'
      }
    }),
    state: new Enum({
      'pending': {color: 'amber'},
      'running': {color: 'green'},
      'shutting-down': {color: 'amber'},
      'terminated': {color: 'deep-orange'},
      'stopping': {color: 'amber'},
      'stopped': {color: 'deep-orange'}
    })
  },
  RDS: {
    actions: new Enum({
      backup: {
        id: 'backup',
        name: 'バックアップ'
      }
    }),
    scheduleActions: new Enum({
      BACKUP: {
        id: 'BACKUP',
        name: 'バックアップ'
      }
    }),
    infoKeys: new Enum({
      service: {
        id: 'service',
        name: 'サービス'
      },
      id: {
        id: 'id',
        name: 'ID'
      },
      powerStatus: {
        id: 'state',
        name: 'RDSステータス'
      }
    }),
    state: new Enum({
      'available': {color: 'green'},
      'backing-up': {color: 'amber'},
      'backtracking': {color: 'amber'},
      'configuring-enhanced-monitoring': {color: 'amber'},
      'configuring-iam-database-auth': {color: 'amber'},
      'configuring-log-exports': {color: 'amber'},
      'converting-to-vpc': {color: 'amber'},
      'creating': {color: 'amber'},
      'deleting': {color: 'amber'},
      'failed': {color: 'deep-orange'},
      'inaccessible-encryption-credentials': {color: 'incompatible'},
      'incompatible-credentials': {color: 'incompatible'},
      'incompatible-network': {color: 'incompatible'},
      'incompatible-option-group': {color: 'incompatible'},
      'incompatible-parameters': {color: 'incompatible'},
      'incompatible-restore': {color: 'incompatible'},
      'maintenance': {color: 'amber'},
      'modifying': {color: 'amber'},
      'moving-to-vpc': {color: 'amber'},
      'rebooting': {color: 'amber'},
      'renaming': {color: 'amber'},
      'resetting-master-credentials': {color: 'amber'},
      'restore-error': {color: 'amber'},
      'starting': {color: 'amber'},
      'stopped': {color: 'incompatible'},
      'stopping': {color: 'amber'},
      'storage-full': {color: 'incompatible'},
      'storage-optimization': {color: 'amber'},
      'upgrading': {color: 'amber'}
    })
  },
  ELB: {
    actions: new Enum(),
    scheduleActions: new Enum({}),
    infoKeys: new Enum({
      service: {
        id: 'service',
        name: 'サービス'
      },
      id: {
        id: 'id',
        name: 'ID'
      }
    }),
    state: new Enum()
  }
})