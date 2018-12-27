import Enum from '@/lib/definition/enum'

export default new Enum({
  EC2: new Enum({
    StatusCheckFailed: {
      id: 'StatusCheckFailed',
      name: '死活監視',
      unit: ''
    },
    CPUUtilization: {
      id: 'CPUUtilization',
      name: 'CPU使用率',
      unit: '%'
    },
    DiskReadBytes: {
      id: 'DiskReadBytes',
      name: 'ディスク読込量',
      unit: 'IOPS'
    },
    DiskWriteBytes: {
      id: 'DiskWriteBytes',
      name: 'ディスク書込量',
      unit: 'IOPS'
    },
    NetworkIn: {
      id: 'NetworkIn',
      name: 'ネットワーク受信量',
      unit: 'byte'
    },
    NetworkOut: {
      id: 'NetworkOut',
      name: 'ネットワーク送信量',
      unit: 'byte'
    }
  }),
  RDS: new Enum({
    CPUUtilization: {
      id: 'CPUUtilization',
      name: 'CPU使用率',
      unit: '%'
    },
    FreeableMemory: {
      id: 'FreeableMemory',
      name: 'メモリ空容量',
      unit: 'byte'
    },
    ReadIOPS: {
      id: 'ReadIOPS',
      name: 'ディスク読取回数',
      unit: 'IOPS'
    },
    WriteIOPS: {
      id: 'WriteIOPS',
      name: 'ディスク書込回数',
      unit: 'IOPS'
    },
    NetworkReceiveThroughput: {
      id: 'NetworkReceiveThroughput',
      name: '読込スループット',
      unit: 'byte'
    },
    NetworkTransmitThroughput: {
      id: 'NetworkTransmitThroughput',
      name: '書込スループット',
      unit: 'byte'
    },
    DatabaseConnections: {
      id: 'DatabaseConnections',
      name: 'DBコネクション数',
      unit: ''
    },
    ReplicaLag: {
      id: 'ReplicaLag',
      name: 'レプリカ遅延秒数',
      unit: '秒'
    }
  }),
  ELB: new Enum({
    Latency: {
      id: 'Latency',
      name: 'レイテンシー',
      unit: '秒'
    },
    RequestCount: {
      id: 'RequestCount',
      name: 'リクエストカウント',
      unit: ''
    },
    HealthyHostCount: {
      id: 'HealthyHostCount',
      name: '正常EC2数',
      unit: '台'
    },
    UnHealthyHostCount: {
      id: 'UnHealthyHostCount',
      name: '危険EC2数',
      unit: '台'
    },
    HTTPCode_ELB_4XX: {
      id: 'HTTPCode_ELB_4XX',
      name: 'HTTPレスポンスコード(4xx)',
      unit: ''
    },
    HTTPCode_ELB_5XX: {
      id: 'HTTPCode_ELB_5XX',
      name: 'HTTPレスポンスコード(5xx)',
      unit: ''
    }
  })
})
