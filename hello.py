# 导入必要的库
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# 创建 Flask 应用实例
app = Flask(__name__)
# 配置数据库 URI，这里使用 SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# 创建数据库实例
db = SQLAlchemy(app)

# 定义数据模型
class Data(db.Model):
    """
    数据表模型
    包含用户名和邮箱信息
    """
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user = db.Column(db.String(80), unique=True, nullable=False)  # 用户名，不可重复
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱，不可重复

# 定义路由
@app.route('/')
def index():
    # 查询所有数据
    all_data = Data.query.all()
    # 渲染模板并传递数据
    return render_template('index.html', data=all_data)

if __name__ == '__main__':
    # 确保数据库和表已创建
    with app.app_context():
        db.create_all()
    # 启动应用
    app.run(debug=True)