from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import json
import os
import requests
from werkzeug.utils import secure_filename
import yaml
import math
import re
from datetime import datetime

from utils.log_processor import LogProcessor
from utils.config import PROFILE_SERVICES, STATUS_COLORS, ALLOWED_EXTENSIONS

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your-secret-key'  # 请更改为随机密钥

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_log_file(filepath, version):
    """处理日志文件并返回分析结果"""
    try:
        print(f"开始处理日志文件: {filepath}")
        print(f"选择的vCenter版本: {version}")
        
        # 创建日志处理器实例
        log_processor = LogProcessor(app.config['UPLOAD_FOLDER'])
        
        # 处理日志文件
        df_logs = log_processor.process_log_file(filepath)
        if df_logs is not None:
            print(f"成功读取日志文件，日志条数: {len(df_logs)}")
            
            # 分析服务状态
            print("开始分析服务状态...")
            df_status = log_processor.analyze_log_df(df_logs, PROFILE_SERVICES)
            
            if df_status is not None and not df_status.empty:
                # 将状态信息存储到session中供UI使用
                service_states = {row['Service']: row['Status'] for _, row in df_status.iterrows()}
                print(f"分析得到的服务状态数量: {len(service_states)}")
                print("服务状态详情:")
                for service, status in service_states.items():
                    print(f"  {service}: {status}")
                
                session['service_states'] = service_states
                session['vcenter_version'] = version
                return True
            else:
                print("未能生成服务状态报告")
        else:
            print("日志文件处理失败")
        
        return False
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def get_timestamped_filename(original_filename):
    """为文件名添加时间戳
    Args:
        original_filename: 原始文件名
    Returns:
        str: 添加时间戳后的文件名
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(original_filename)
    return f"{name}_{timestamp}{ext}"

@app.route('/', methods=['GET', 'POST'])
def upload_page():
    return render_template('upload.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("没有文件被上传")
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    version = request.form.get('version', '8.0U3')  # 默认使用8.0U3版本
    
    if file.filename == '':
        print("文件名为空")
        return redirect(url_for('upload_page'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamped_filename = get_timestamped_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], timestamped_filename)
        file.save(filepath)
        
        if process_log_file(filepath, version):
            return redirect(url_for('matrix_view'))
    
    return redirect(url_for('upload_page'))

@app.route('/download_file', methods=['POST'])
def download_file():
    url = request.form.get('url')
    version = request.form.get('version', '8.0U3')  # 默认使用8.0U3版本
    
    if not url:
        print("未提供URL")
        return redirect(url_for('upload_page'))
    
    try:
        # 下载文件
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # 从URL中提取文件名，如果没有则使用默认名称
            filename = url.split('/')[-1]
            if not filename or not allowed_file(filename):
                filename = 'downloaded.log'
            
            timestamped_filename = get_timestamped_filename(filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(timestamped_filename))
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if process_log_file(filepath, version):
                return redirect(url_for('matrix_view'))
        else:
            print(f"下载文件失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"下载文件时出错: {e}")
        import traceback
        print(traceback.format_exc())
    
    return redirect(url_for('upload_page'))

@app.route('/matrix')
def matrix_view():
    return render_template('matrix.html')

def merge_service_info(services_config, service_states):
    """合并服务配置和状态信息
    Args:
        services_config: 从YAML文件读取的服务配置
        service_states: 从session中获取的服务状态字典
    Returns:
        tuple: (services_list, dependencies_dict)
    """
    services_list = []
    dependencies_dict = {}
    
    def process_service(service_name, service_info):
        # 获取服务基本信息
        service_id = str(service_info.get('id', ''))
        name_in_log = service_info.get('nameinlog', service_name)
        service_level = service_info.get('level', 2)  # 默认级别为2
        service_type = service_info.get('type', '')
        
        # 获取服务状态
        status = 'unknown'
        if service_level in [1, 3] and service_type == 'system-control':
            # 对于级别1和3的系统控制服务，使用特殊状态
            status = 'system-control'
        else:
            # 对于其他服务，使用从session中获取的状态
            status = service_states.get(name_in_log, 'unknown')
        
        # 创建服务信息字典，添加前端需要的所有字段
        service_dict = {
            'id': service_id,
            'name': name_in_log,
            'label': service_name,
            'level': service_level,
            'type': service_type,
            'description': service_info.get('description', ''),
            'status': status,
            'color': STATUS_COLORS.get(status, '#9E9E9E'),
            'log': service_info.get('log', []),
            'numeric_id': int(service_id) if service_id.isdigit() else 0
        }
        
        # 处理依赖关系
        dependencies = []
        if 'dp_service' in service_info:
            dependencies = service_info['dp_service']
            dependencies_dict[name_in_log] = dependencies
            
        service_dict['dependencies'] = dependencies
        
        # 将当前服务添加到列表中
        services_list.append(service_dict)
        
        # 递归处理子服务
        if 'sub_services' in service_info:
            for sub_name, sub_info in service_info['sub_services'].items():
                process_service(sub_name, sub_info)
    
    # 处理所有服务
    if services_config and 'services' in services_config:
        for service_name, service_info in services_config['services'].items():
            process_service(service_name, service_info)
    
    # 按照numeric_id排序
    services_list.sort(key=lambda x: x['numeric_id'])
    
    return services_list, dependencies_dict

def generate_matrix(services, service_dependencies):
    """
    生成8x7的服务状态矩阵
    Args:
        services: 服务信息列表
        service_dependencies: 服务依赖关系字典
    Returns:
        matrix: 8x7的矩阵，包含服务信息
        total_services: 服务总数
    """
    matrix = []
    for i in range(7):  # 7行
        row = []
        for j in range(8):  # 8列
            index = i * 8 + j
            if index < len(services):
                service = services[index].copy()  # 创建副本避免修改原始数据
                # 使用服务名称而不是ID来获取依赖关系
                service['dependencies_info'] = service_dependencies.get(service['name'], [])
                row.append(service)
            else:
                row.append(None)  # 空单元格
        matrix.append(row)
    
    return matrix, len(services)

@app.route('/api/services/matrix')
def get_services_matrix():
    try:
        # 使用绝对路径读取YAML配置文件
        version = session.get('vcenter_version', '8.0U3')
        print(f"\n=== 开始生成服务矩阵 ===")
        print(f"当前版本: {version}")
        
        # 根据版本生成正确的配置文件名
        version_map = {
            '7.0': 'vcsa-7',
            '8.0U1': 'vcsa-8U1',
            '8.0U2': 'vcsa-8U2',
            '8.0U3': 'vcsa-8U3'
        }
        version_prefix = version_map.get(version, 'vcsa-8U3')
        config_filename = f'{version_prefix}-profile-all-default.yaml'
        
        config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vmon-json-services', config_filename)
        print(f"尝试读取配置文件: {config_file_path}")
        
        if not os.path.exists(config_file_path):
            print(f"配置文件 {config_filename} 不存在，使用默认配置")
            config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                          'vmon-json-services', 
                                          'vcsa-8U3-profile-all-default.yaml')
        
        with open(config_file_path, 'r', encoding='utf-8') as f:
            services_config = yaml.safe_load(f)
            print(f"读取到的服务配置数量: {len(services_config.get('services', {}))}")
        
        # 从session获取服务状态
        service_states = session.get('service_states', {})
        print(f"从session获取的服务状态数量: {len(service_states)}")
        
        # 合并服务配置和状态信息
        services, dependencies = merge_service_info(services_config, service_states)
        print(f"合并后的服务数量: {len(services)}")
        print(f"依赖关系数量: {len(dependencies)}")
        
        # 生成矩阵数据
        matrix, total_services = generate_matrix(services, dependencies)
        print(f"矩阵大小: {len(matrix)}x{len(matrix[0]) if matrix else 0}")
        print(f"总服务数: {total_services}")
        
        # 处理依赖关系
        processed_dependencies = {}
        for service_name, deps in dependencies.items():
            processed_dependencies[service_name] = {
                'depends_on': deps,  # 该服务依赖的服务
                'depended_by': []    # 依赖该服务的服务
            }
        
        # 填充被依赖关系
        for service_name, deps in dependencies.items():
            for dep in deps:
                if dep in processed_dependencies:
                    processed_dependencies[dep]['depended_by'].append(service_name)
                else:
                    processed_dependencies[dep] = {
                        'depends_on': [],
                        'depended_by': [service_name]
                    }
        
        return jsonify({
            'matrix': matrix,
            'total_services': total_services,
            'dependencies': processed_dependencies
        })
        
    except Exception as e:
        print(f"生成服务矩阵时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 