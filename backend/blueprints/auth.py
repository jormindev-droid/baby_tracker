"""
认证蓝图
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import bcrypt
from datetime import timedelta

from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    if len(username) < 3:
        return jsonify({'message': '用户名至少需要3个字符'}), 400
    
    if len(password) < 6:
        return jsonify({'message': '密码至少需要6个字符'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    # 使用bcrypt哈希密码
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user = User(username=username, password=hashed_password.decode('utf-8'))
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message': '用户名或密码错误'}), 401
    
    # 检查密码是否有效
    password_valid = False
    
    try:
        # 首先尝试使用bcrypt验证（新用户）
        password_valid = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
    except ValueError:
        # 如果bcrypt验证失败（可能是无效的salt），尝试明文验证（旧用户）
        if user.password == password:
            password_valid = True
            # 将明文密码升级为bcrypt哈希
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')
            db.session.commit()
    
    if password_valid:
        # 将user.id转换为字符串，因为JWT identity必须是字符串类型
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user_id': user.id
        }), 200
    
    return jsonify({'message': '用户名或密码错误'}), 401