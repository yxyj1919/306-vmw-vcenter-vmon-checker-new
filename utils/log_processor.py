import pandas as pd
import re
import os

class LogProcessor:
    def __init__(self, upload_folder):
        """初始化日志处理器
        Args:
            upload_folder: 上传文件的目录路径
        """
        self.upload_folder = upload_folder

    def process_log_file(self, filepath):
        """处理日志文件
        Args:
            filepath: 日志文件的完整路径
        Returns:
            DataFrame: 处理后的日志数据
        """
        try:
            # 打开日志文件并逐行读取
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_lines = f.readlines()

            # 初始化 DataFrame，包含解析后的列
            df = pd.DataFrame(columns=['Time', 'Level', 'Host', 'Log', 'Complete Log'])

            # 存储解析后的行
            rows_list = []

            for log_entry in raw_lines:
                log_entry = log_entry.strip()  # 去掉多余的换行和空格
                # 使用正则表达式解析日志（假设日志格式为：时间 主机名 等级 消息）
                match = re.match(r'(\S+)\s+(\S+)\s+(\S+)\s+(.*)', log_entry)

                if match:
                    # 提取日志各部分信息
                    time, level, host, log = match.groups()
                else:
                    # 如果格式不匹配，将整行作为日志内容
                    time, level, host, log = '', '', '', log_entry

                # 检查是否包含启动配置的特定关键词
                if "Starting vMon with profile" in log:
                    profile = log.split("Starting vMon with profile")[-1].strip()
                    print('------------------------------')
                    print("Start profile: " + profile)

                # 将解析后的数据存入字典
                rows_list.append({
                    "Time": time,
                    "Level": level,
                    "Host": host,
                    "Log": log,
                    "Complete Log": log_entry
                })

            # 将所有解析结果转换为 DataFrame
            df = pd.DataFrame(rows_list)

            # 保存处理后的日志到CSV文件
            df_log_path = os.path.join(self.upload_folder, 'df_log.csv')
            df.to_csv(df_log_path, index=False)

            return df

        except FileNotFoundError:
            print(f"文件未找到：{filepath}")
        except pd.errors.EmptyDataError:
            print("日志文件为空，无法解析。")
        except Exception as e:
            print(f"解析日志文件时发生错误：{e}")
            import traceback
            print(traceback.format_exc())
        return None

    def analyze_log_df(self, df, profile_services):
        """分析日志DataFrame并生成服务状态报告
        Args:
            df: 日志DataFrame
            profile_services: 服务配置信息
        Returns:
            DataFrame: 服务状态报告
        """
        try:
            # 筛选包含关键词的日志
            all_idx = df['Log'].str.contains('STARTED', regex=False) | \
                     df['Log'].str.contains('STOPPED', regex=False) | \
                     df['Log'].str.contains('Service exited', regex=False) | \
                     df['Log'].str.contains('Service crashed', regex=False) | \
                     df['Log'].str.contains('Service terminated', regex=False) | \
                     df['Log'].str.contains('Service start operation timed out.', regex=False)
            all_log = df[all_idx]

            # 提取服务名称和状态
            service_data = []
            for _, log_entry in all_log.iterrows():
                service = self.extract_service(log_entry)
                if service:
                    status = self.get_service_status(df, service)
                    service_data.append({
                        'Service': service,
                        'Status': status
                    })

            # 创建服务状态DataFrame
            services_df = pd.DataFrame(service_data)
            if not services_df.empty:
                # 如果有重复的服务，保留最后一个状态
                services_df = services_df.drop_duplicates(subset=['Service'], keep='last')
                
                # 保存服务状态到CSV文件
                status_file_path = os.path.join(self.upload_folder, 'service_status.csv')
                services_df.to_csv(status_file_path, index=False)
                return services_df

            return None

        except Exception as e:
            print(f"分析日志时发生错误：{e}")
            import traceback
            print(traceback.format_exc())
            return None

    def extract_service(self, log_entry):
        """提取日志中的服务名称"""
        try:
            log_str = str(log_entry['Log'] if isinstance(log_entry, pd.Series) else log_entry)
            start_idx = log_str.find('<') + 1
            end_idx = log_str.find('>')
            if start_idx > 0 and end_idx > start_idx:
                return log_str[start_idx:end_idx]
            return None
        except (ValueError, AttributeError):
            return None

    def get_service_status(self, df_logs, service_name):
        """获取服务的当前状态
        Args:
            df_logs: 日志DataFrame
            service_name: 服务名称
        Returns:
            str: 服务状态 (running/failed to start/not running/unknown)
        """
        try:
            # 筛选指定服务的日志
            service_logs = df_logs[df_logs['Log'].str.contains(f'<{service_name}>', regex=False)]
            
            # 如果没有找到服务的日志,返回 unknown
            if service_logs.empty:
                return 'unknown'

            # 检查是否有启动失败的情况
            failed_logs = service_logs[service_logs['Log'].str.contains('Service exited|Service crashed|Service terminated|Service start operation timed out', regex=True)]
            if not failed_logs.empty:
                return 'failed to start'

            # 检查是否成功启动
            started_logs = service_logs[service_logs['Log'].str.contains('STARTED', regex=False)]
            if not started_logs.empty:
                return 'running'

            # 检查是否已停止
            stopped_logs = service_logs[service_logs['Log'].str.contains('STOPPED', regex=False)]
            if not stopped_logs.empty:
                return 'not running'

            # 如果以上状态都不匹配,返回 unknown
            return 'unknown'

        except Exception as e:
            print(f"获取服务状态时发生错误：{e}")
            return 'unknown'