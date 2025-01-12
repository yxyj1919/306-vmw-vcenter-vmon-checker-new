# vCenter vMon Service Checker
![](https://yxyj1919-imagebed.oss-cn-beijing.aliyuncs.com/rocket-image/202501130043555.png)
vCenter vMon Service Checker 是一个用于检查和分析 VMware vCenter 服务状态的 Web 应用程序。它提供了直观的服务状态可视化界面，帮助管理员快速识别服务问题和依赖关系。

## 主要功能

- **服务状态矩阵视图**：以矩阵形式展示所有 vCenter 服务的运行状态
- **服务依赖关系分析**：可视化展示服务之间的依赖关系
- **日志文件分析**：自动解析和展示服务日志信息
- **服务详情查看**：支持查看每个服务的详细信息和日志路径
- **文件上传功能**：支持上传并分析 vmon 日志文件

## 部署方式

### 1. Docker 部署（推荐）

```bash
# 构建镜像
docker build -t vcenter-vmon-checker .

# 运行容器
docker run -d -p 5000:5000 --name vmon-checker vcenter-vmon-checker
```

访问 `http://localhost:5000` 即可使用。

### 2. 本地部署

1. 克隆仓库：
```bash
git clone [repository-url]
cd vmw-vcenter-vmon-checker
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 启动应用：
```bash
python app.py
```

## 使用说明

### 1. 准备工作

在 vCenter 服务器上执行以下操作：

```bash
# 1. SSH 登录 vCenter
ssh root@vcenter-ip

# 2. 重启所有服务
service-control --stop --all && service-control --start --all

# 3. 获取日志文件
cp /var/log/vmware/vmon/vmon.log /tmp/ && cd /tmp/ && tar -czf vmon-logs.tar.gz vmon.log
```

将生成的 `vmon-logs.tar.gz` 下载到本地。

### 2. 使用步骤

1. 选择 vCenter 版本（支持 7.0/8.0U1/8.0U2/8.0U3）
2. 上传日志文件（支持本地上传或远程下载）
3. 查看服务状态矩阵：
   - 点击服务可查看依赖关系
   - 双击服务可查看详细信息
   - 不同颜色代表不同状态：
     - 绿色：运行中
     - 红色：启动失败
     - 橙色：未运行
     - 灰色：状态未知
     - 蓝色：系统控制服务

## 目录结构

```
.
├── app.py                    # 主应用程序
├── Dockerfile               # Docker 构建文件
├── requirements.txt         # Python 依赖
├── templates/              # HTML 模板
│   ├── matrix.html         # 矩阵视图
│   └── upload.html         # 上传页面
├── utils/                 # 工具函数
│   ├── config.py           # 配置文件
│   └── log_processor.py    # 日志处理
└── vmon-json-services/    # 服务配置
    └── vcsa8-service.json  # 服务定义
```

## 系统要求

- Python 3.9 或更高版本
- Docker（如使用 Docker 部署）
- 现代浏览器（Chrome、Firefox、Safari、Edge 等）

## 注意事项

- 建议定期清理 `uploads` 目录中的临时文件
- 确保上传的日志文件格式正确
- 推荐使用最新版本的现代浏览器访问
- Docker 部署时会自动创建必要的目录和权限

## 常见问题

1. 上传文件失败
   - 检查文件格式是否为 .log
   - 确保文件大小在合理范围内
   - 检查 uploads 目录权限

2. 服务状态显示异常
   - 确认选择了正确的 vCenter 版本
   - 检查日志文件是否完整
   - 确保日志文件来自正确的路径

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交之前，请确保：

1. 代码符合项目的编码规范
2. 添加了必要的测试用例
3. 更新了相关文档

## 许可证

[许可证类型] 