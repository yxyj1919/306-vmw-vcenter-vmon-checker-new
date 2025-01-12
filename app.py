from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import json
import os
from werkzeug.utils import secure_filename
import requests
from urllib.parse import urlparse

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'log'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 添加 session 密钥
app.secret_key = 'your-secret-key'  # 请更改为随机密钥

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    version = request.form.get('version')
    if not version:
        return 'Version is required', 400
        
    filepath = None
    
    if 'logUrl' in request.form:
        # 处理远程URL
        url = request.form['logUrl']
        try:
            # 验证URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return 'Invalid URL', 400
                
            # 下载文件
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存到临时文件
            filename = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_vmon.log')
            with open(filename, 'wb') as f:
                f.write(response.content)
            filepath = filename
            
        except Exception as e:
            return f'Failed to download file: {str(e)}', 400
            
    elif 'logFile' in request.files:
        # 处理本地文件上传
        file = request.files['logFile']
        if file.filename == '':
            return 'No selected file', 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            return 'Invalid file', 400
    else:
        return 'No file provided', 400
    
    try:
        # 分析日志文件
        service_states = analyze_vmon_log(filepath)
        
        # 根据版本选择对应的服务配置文件
        services_config = load_services_config(version)
        
        # 更新服务状态
        update_services_status(services_config, service_states)
        
        # 存储更新后的配置供服务页面使用
        session['current_services'] = services_config
        
        return redirect(url_for('services'))
        
    except Exception as e:
        return f'Error processing file: {str(e)}', 400

@app.route('/services')
def services():
    return render_template('services.html')

def analyze_vmon_log(filepath):
    service_states = {}
    current_service = None
    
    with open(filepath, 'r') as f:
        for line in f:
            # 跳过非UTF-8编码的行
            try:
                line = line.strip()
            except UnicodeDecodeError:
                continue
                
            # 检查是否是服务状态相关的日志
            if '<' in line and '>' in line:
                # 提取服务名称
                service_name = line[line.find('<')+1:line.find('>')]
                
                # 移除 -healthcmd 后缀
                if service_name.endswith('-healthcmd'):
                    continue
                    
                # 移除 -prestart 后缀
                if service_name.endswith('-prestart'):
                    continue
                    
                # 移除 event-pub 服务
                if service_name == 'event-pub':
                    continue
                    
                current_service = service_name
                
                # 初始化服务状态为 unknown
                if current_service not in service_states:
                    service_states[current_service] = 'unknown'
            
            # 检查服务启动成功的消息
            if 'Service STARTED successfully' in line and current_service:
                service_states[current_service] = 'running'
            
            # 检查服务健康检查失败的消息
            elif 'Service api-health command\'s stderr' in line and current_service:
                if service_states[current_service] != 'running':
                    service_states[current_service] = 'failed'
            
            # 检查服务初始化中的消息
            elif 'Re-check service health since it is still initializing' in line and current_service:
                if service_states[current_service] != 'running':
                    service_states[current_service] = 'unknown'
                    
            # 检查服务停止的消息
            elif 'Skip service health check. State STOPPED' in line and current_service:
                service_states[current_service] = 'failed'
    
    return service_states

def load_services_config(version):
    # 根据版本加载对应的服务配置文件
    config_files = {
        '6.7': 'vmon-json-services/vcsa67-service.json',
        '7.0': 'vmon-json-services/vcsa70-service.json',
        '8.0': 'vmon-json-services/vcsa8-service.json'
    }
    filename = config_files.get(version)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件不存在: {filename}")
        return {"services": {}}
    except json.JSONDecodeError:
        print(f"配置文件格式错误: {filename}")
        return {"services": {}}

def update_services_status(services_config, service_states):
    # 更新服务配置中的状态
    for service_name, service_info in services_config['services'].items():
        service_info['status'] = service_states.get(service_name, 'unknown')

@app.route('/api/services')
def get_services():
    # 从 session 获取当前服务配置
    services_config = session.get('current_services')
    if not services_config:
        return jsonify({"nodes": [], "edges": []})
        
    nodes = []
    edges = []
    
    # 处理节点
    for service_name, service_info in services_config['services'].items():
        # 设置节点颜色
        if service_info['id'] <= 5:  # 级别1服务
            base_color = '#90CAF9'  # 浅蓝色
        elif service_info['id'] >= 42:  # 级别3服务
            base_color = '#CE93D8'  # 浅紫色
        else:
            base_color = {
                'running': '#4CAF50',  # 绿色
                'failed': '#F44336',   # 红色
                'unknown': '#9E9E9E'   # 灰色
            }[service_info['status']]
        
        # 创建节点
        node = {
            "id": service_name,
            "label": f"{service_info['id']}. {service_name}",
            "type": service_info['type'],
            "status": service_info['status'],
            "color": {
                "background": base_color,
                "border": '#2196F3' if service_info['type'] == 'system-control' else '#FF9800',
                "highlight": {
                    "background": base_color,
                    "border": '#1976D2' if service_info['type'] == 'system-control' else '#F57C00'
                },
                "hover": {
                    "background": base_color,
                    "border": '#1976D2' if service_info['type'] == 'system-control' else '#F57C00'
                }
            }
        }
        
        # 根据ID设置不同的区域位置
        if service_info['id'] <= 5:
            node['x'] = -800
            node['y'] = (service_info['id'] - 3) * 60
            node['fixed'] = True
            node['physics'] = False
        elif service_info['id'] >= 42:
            node['x'] = 2000
            node['y'] = (service_info['id'] - 43) * 60
            node['fixed'] = True
            node['physics'] = False
        else:
            node['physics'] = True
        
        nodes.append(node)
        
        # 处理依赖关系
        for dep in service_info['depends_on']:
            edges.append({
                "from": dep,
                "to": service_name
            })
    
    return jsonify({"nodes": nodes, "edges": edges})

if __name__ == '__main__':
    app.run(debug=True) 