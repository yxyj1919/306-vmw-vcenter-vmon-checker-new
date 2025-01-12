"""
服务配置和状态颜色映射
"""

# 定义各个profile包含的服务
PROFILE_SERVICES = {
    "NONE": [],
    "HACore": ["vcha"],
    "HAActive": [
        "rhttpproxy", "envoy", "envoy-hgw", "envoy-sidecar", "lookupsvc", 
        "sts", "sca", "applmgmt", "cis-license", "content-library", 
        "vpxd-svcs", "eam", "imagebuilder", "netdumper", "perfcharts", 
        "rbd", "sps", "vapi-endpoint", "updatemgr", "vpxd", "vsan-health", 
        "vsm", "vmonapi", "vmware-postgres-archiver", "vmcam", "pschealth", 
        "vsphere-ui", "analytics", "hvc", "trustmanagement", 
        "certificatemanagement", "certificateauthority", "vlcm", 
        "infraprofile", "topologysvc", "vstats", "vtsdb", "wcp", 
        "observability-vapi", "vc-ws1a-broker"
    ],
    "CRITICAL": [
        "vcha", "vpxd", "rhttpproxy", "envoy", "envoy-hgw", "envoy-sidecar",
        "rbd", "vpxd-svcs", "sps", "vmware-postgres-archiver", 
        "vmware-vpostgres", "vapi-endpoint", "pschealth", "lookupsvc", 
        "wcp", "sts", "vc-ws1a-broker"
    ],
    "ALL": [
        "envoy","envoy-sidecar","envoy-hgw","rhttpproxy","vmware-vpostgres",
        "vtsdb","vmware-postgres-archiver","eam","lookupsvc","trustmanagement",
        "vc-ws1a-broker","sts","vpxd","sca","vlcm",
        "pschealth","cis-license","vapi-endpoint","vsan-health","vsm",
        "vpxd-svcs","sps","analytics","vstats","certificateauthority",
        "observability-vapi","certificatemanagement","topologysvc","wcp","applmgmt",
        "updatemgr","infraprofile","hvc","vsphere-ui","content-library",
        "perfcharts"
    ]
}

# 状态颜色映射
STATUS_COLORS = {
    'running': '#4CAF50',      # 绿色
    'failed to start': '#F44336',  # 红色
    'not running': '#FFA500',   # 橙色
    'unknown': '#9E9E9E',       # 灰色
    'system-control': '#2196F3'  # 蓝色 - 用于级别1和级别3的系统控制服务
}

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'log'} 