"""
宝宝成长追踪器 - 主应用入口
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import config
from models import db
from blueprints import blueprints

def create_app(config_name='default'):
    """创建Flask应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    Migrate(app, db)
    
    # 注册蓝图
    for bp in blueprints:
        app.register_blueprint(bp)
    
    return app

if __name__ == '__main__':
    # 创建应用
    app = create_app('development')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 启动服务器
    app.run(debug=True, port=5001)