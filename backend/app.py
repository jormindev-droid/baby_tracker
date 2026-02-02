from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import uuid
import bcrypt
import logging
from typing import Dict, Any

# 导入自定义工具
from utils.oss_client import OSSClient
from utils.config_loader import ConfigLoader

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

try:
    # 尝试加载配置文件
    config = ConfigLoader.load_config()
    
    # 应用配置
    app_config = ConfigLoader.get_app_config(config)
    app.config['SECRET_KEY'] = app_config.get('secret_key', 'your-secret-key-here')
    app.config['JWT_SECRET_KEY'] = app_config.get('secret_key', 'super-secret-jwt-key-with-at-least-32-characters')
    
    # 数据库配置
    db_config = config.get('database', {})
    app.config['SQLALCHEMY_DATABASE_URI'] = db_config.get('uri', 'sqlite:///baby_tracker.db')
    
    # 上传配置
    upload_config = ConfigLoader.get_upload_config(config)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = upload_config.get('max_file_size', 10485760)  # 10MB
    
    # OSS配置
    oss_config = ConfigLoader.get_oss_config(config)
    app.config['ALLOWED_EXTENSIONS'] = upload_config.get('allowed_extensions', ['.jpg', '.jpeg', '.png', '.gif', '.bmp'])
    
except Exception as e:
    logger.warning(f"加载配置文件失败，使用默认配置: {e}")
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baby_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-jwt-key-with-at-least-32-characters'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 10485760  # 10MB
    app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
jwt = JWTManager(app)

# 初始化OSS客户端（如果配置可用）
oss_client = None
try:
    oss_client = OSSClient()
    logger.info("阿里云OSS客户端初始化成功")
except Exception as e:
    logger.warning(f"阿里云OSS客户端初始化失败，将使用本地存储: {e}")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    children = db.relationship('Child', backref='user', lazy=True)

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    growth_records = db.relationship('GrowthRecord', backref='child', lazy=True)
    photos = db.relationship('Photo', backref='child', lazy=True)
    milestones = db.relationship('Milestone', backref='child', lazy=True)

class GrowthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    head_circumference = db.Column(db.Float)
    date_recorded = db.Column(db.Date, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    object_key = db.Column(db.String(500))  # OSS对象键
    original_url = db.Column(db.String(500))  # 原始图片URL
    thumbnail_url = db.Column(db.String(500))  # 缩略图URL
    description = db.Column(db.Text)
    date_taken = db.Column(db.Date, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    deleted = db.Column(db.Boolean, default=False)  # 逻辑删除标记
    deleted_at = db.Column(db.DateTime)  # 删除时间

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_achieved = db.Column(db.Date, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)

def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext.replace('.', '') for ext in app.config['ALLOWED_EXTENSIONS']]

@app.route('/api/register', methods=['POST'])
def register():
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

@app.route('/api/login', methods=['POST'])
def login():
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

@app.route('/api/children', methods=['GET'])
@jwt_required()
def get_children():
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    children = Child.query.filter_by(user_id=user_id).all()
    
    result = []
    for child in children:
        # 获取最新的成长记录
        latest_growth = GrowthRecord.query.filter_by(child_id=child.id).order_by(GrowthRecord.date_recorded.desc()).first()
        
        # 获取照片和里程碑数量（只统计未删除的）
        photos_count = Photo.query.filter_by(child_id=child.id, deleted=False).count()
        milestones_count = Milestone.query.filter_by(child_id=child.id).count()
        
        result.append({
            'id': child.id,
            'name': child.name,
            'birth_date': child.birth_date.strftime('%Y-%m-%d'),
            'gender': child.gender,
            'latestGrowth': {
                'height': latest_growth.height if latest_growth else None,
                'weight': latest_growth.weight if latest_growth else None
            } if latest_growth else None,
            'photos_count': photos_count,
            'milestones_count': milestones_count
        })
    
    return jsonify(result), 200

@app.route('/api/children', methods=['POST'])
@jwt_required()
def add_child():
    try:
        user_id_str = get_jwt_identity()
        # 将字符串转换回整数进行数据库查询
        user_id = int(user_id_str)
        data = request.get_json()
        
        # 验证必填字段
        if not data:
            return jsonify({'message': '请求数据不能为空'}), 400
        
        required_fields = ['name', 'birth_date', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'缺少必填字段: {field}'}), 400
        
        # 验证性别字段
        if data['gender'] not in ['male', 'female']:
            return jsonify({'message': '性别必须是 male 或 female'}), 400
        
        # 验证日期格式
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': '出生日期格式不正确，请使用 YYYY-MM-DD 格式'}), 400
        
        # 验证出生日期不能是未来日期
        if birth_date > datetime.now().date():
            return jsonify({'message': '出生日期不能是未来日期'}), 400
        
        child = Child(
            name=data['name'].strip(),
            birth_date=birth_date,
            gender=data['gender'],
            user_id=user_id
        )
        
        db.session.add(child)
        db.session.commit()
        
        return jsonify({
            'message': '宝宝信息添加成功', 
            'child_id': child.id,
            'child': {
                'id': child.id,
                'name': child.name,
                'birth_date': child.birth_date.strftime('%Y-%m-%d'),
                'gender': child.gender
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加宝宝时发生错误: {str(e)}")
        return jsonify({'message': '服务器内部错误，请稍后重试'}), 500

@app.route('/api/children/<int:child_id>/growth', methods=['GET'])
@jwt_required()
def get_growth_records(child_id):
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    records = GrowthRecord.query.filter_by(child_id=child_id).order_by(GrowthRecord.date_recorded).all()
    
    result = []
    for record in records:
        result.append({
            'id': record.id,
            'height': record.height,
            'weight': record.weight,
            'head_circumference': record.head_circumference,
            'date_recorded': record.date_recorded.strftime('%Y-%m-%d')
        })
    
    return jsonify(result), 200

@app.route('/api/children/<int:child_id>/growth', methods=['POST'])
@jwt_required()
def add_growth_record(child_id):
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    data = request.get_json()
    
    record = GrowthRecord(
        height=data['height'],
        weight=data['weight'],
        head_circumference=data.get('head_circumference'),
        date_recorded=datetime.strptime(data['date_recorded'], '%Y-%m-%d').date(),
        child_id=child_id
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'message': '成长记录添加成功'}), 201

@app.route('/api/oss/signature', methods=['GET'])
@jwt_required()
def get_oss_signature():
    """获取OSS Web直传签名（简化版）"""
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        if not oss_client:
            return jsonify({'message': 'OSS服务未配置'}), 503
        
        # 获取请求参数
        child_id = request.args.get('child_id', type=int)
        filename = request.args.get('filename')
        
        if not child_id or not filename:
            return jsonify({'message': '缺少必要参数: child_id 或 filename'}), 400
        
        # 验证宝宝是否属于当前用户
        child = Child.query.filter_by(id=child_id, user_id=user_id).first()
        if not child:
            return jsonify({'message': '未找到宝宝信息'}), 404
        
        # 验证文件扩展名
        if not oss_client.validate_file_extension(filename):
            return jsonify({'message': '不支持的文件类型'}), 400
        
        # 生成对象键
        object_key = oss_client.generate_object_key(filename, user_id, child_id)
        
        # 直接使用OSS SDK生成预签名URL
        # 对于PUT操作，我们需要生成一个可以上传的URL
        upload_url = oss_client.bucket.sign_url('PUT', object_key, 3600)
        
        # 解码URL，确保格式正确
        import urllib.parse
        decoded_url = urllib.parse.unquote(upload_url)
        
        return jsonify({
            'upload_url': decoded_url,
            'object_key': object_key,
            'expire_time': 3600
        }), 200
        
    except Exception as e:
        logger.error(f"获取OSS签名失败: {e}")
        return jsonify({'message': f'获取上传签名失败: {str(e)}'}), 500

@app.route('/api/children/<int:child_id>/photos', methods=['GET'])
@jwt_required()
def get_photos(child_id):
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    # 只查询未删除的照片
    photos = Photo.query.filter_by(child_id=child_id, deleted=False).order_by(Photo.date_taken.desc()).all()
    
    result = []
    for photo in photos:
        # 生成新的带签名的URL
        original_url = photo.original_url
        thumbnail_url = photo.thumbnail_url or photo.original_url
        
        # 如果使用OSS，生成新的临时URL
        if oss_client and photo.object_key:
            try:
                # 使用数据库中存储的object_key
                object_key = photo.object_key
                
                # 生成新的带签名URL
                original_url = oss_client.get_presigned_url(object_key, 'GET')
                
                # 生成缩略图的带签名URL
                thumbnail_key = oss_client.generate_thumbnail_key(object_key)
                try:
                    # 检查缩略图是否存在
                    oss_client.bucket.get_object_meta(thumbnail_key)
                    thumbnail_url = oss_client.get_presigned_url(thumbnail_key, 'GET')
                except:
                    # 缩略图不存在，使用原始图片
                    thumbnail_url = original_url
                    
            except Exception as e:
                logger.warning(f"生成临时URL失败: {e}")
                # 如果生成失败，使用数据库中的URL
        
        result.append({
            'id': photo.id,
            'filename': photo.filename,
            'description': photo.description,
            'date_taken': photo.date_taken.strftime('%Y-%m-%d'),
            'original_url': original_url,
            'thumbnail_url': thumbnail_url
        })
    
    return jsonify(result), 200

@app.route('/api/children/<int:child_id>/photos', methods=['POST'])
@jwt_required()
def add_photo(child_id):
    """添加照片（支持本地存储和OSS存储）"""
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': '请求数据不能为空'}), 400
        
        required_fields = ['filename', 'object_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'缺少必填字段: {field}'}), 400
        
        original_filename = data['filename']
        object_key = data['object_key']
        description = data.get('description', '')
        
        # 验证文件扩展名
        if not allowed_file(original_filename):
            return jsonify({'message': '不支持的文件类型'}), 400
        
        # 从object_key中提取UUID文件名
        # object_key格式: baby_tracker/{user_id}/{child_id}/{uuid}{ext}
        import os
        uuid_filename = os.path.basename(object_key)
        
        # 构建图片URL
        original_url = None
        thumbnail_url = None
        
        if oss_client:
            try:
                # 使用OSS存储
                original_url = oss_client.get_presigned_url(object_key, 'GET')
                
                # 尝试获取缩略图URL
                thumbnail_key = oss_client.generate_thumbnail_key(object_key)
                try:
                    # 检查缩略图是否存在
                    oss_client.bucket.get_object_meta(thumbnail_key)
                    thumbnail_url = oss_client.get_presigned_url(thumbnail_key, 'GET')
                except:
                    # 缩略图不存在，使用原始图片
                    thumbnail_url = original_url
                    
            except Exception as e:
                logger.error(f"获取OSS URL失败: {e}")
                return jsonify({'message': '获取图片URL失败'}), 500
        else:
            # 使用本地存储 - 这里也需要使用UUID文件名
            original_url = f"/uploads/{uuid_filename}"
            thumbnail_url = original_url
        
        # 创建照片记录 - 使用UUID文件名
        photo = Photo(
            filename=uuid_filename,
            object_key=object_key,
            original_url=original_url,
            thumbnail_url=thumbnail_url,
            description=description,
            date_taken=datetime.now().date(),
            child_id=child_id
        )
        
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({
            'message': '照片上传成功',
            'photo': {
                'id': photo.id,
                'filename': photo.filename,
                'description': photo.description,
                'date_taken': photo.date_taken.strftime('%Y-%m-%d'),
                'original_url': photo.original_url,
                'thumbnail_url': photo.thumbnail_url
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加照片失败: {e}")
        return jsonify({'message': '添加照片失败'}), 500

@app.route('/api/children/<int:child_id>/photos/<int:photo_id>', methods=['DELETE'])
@jwt_required()
def delete_photo(child_id, photo_id):
    """逻辑删除照片（移动到deleted目录）"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    # 查找照片
    photo = Photo.query.filter_by(id=photo_id, child_id=child_id, deleted=False).first()
    if not photo:
        return jsonify({'message': '未找到照片或照片已被删除'}), 404
    
    try:
        # 如果使用OSS，将文件移动到deleted目录
        if oss_client and photo.object_key:
            try:
                # 使用数据库中存储的object_key
                object_key = photo.object_key
                
                # 将OSS文件移动到deleted目录
                oss_client.move_to_deleted(object_key)
            except Exception as e:
                logger.warning(f"移动OSS文件到deleted目录失败: {e}")
                # 即使移动失败，也继续标记为删除
        
        # 逻辑删除：标记为已删除，设置删除时间
        photo.deleted = True
        photo.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({'message': '照片已移动到回收站'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除照片失败: {e}")
        return jsonify({'message': '删除照片失败'}), 500

@app.route('/api/children/<int:child_id>/photos/<int:photo_id>/restore', methods=['POST'])
@jwt_required()
def restore_photo(child_id, photo_id):
    """恢复已删除的照片"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    # 查找已删除的照片
    photo = Photo.query.filter_by(id=photo_id, child_id=child_id, deleted=True).first()
    if not photo:
        return jsonify({'message': '未找到已删除的照片'}), 404
    
    try:
        # 如果使用OSS，将文件从deleted目录移回原位置
        if oss_client and photo.object_key:
            try:
                # 从deleted目录移回原位置
                deleted_key = f"deleted/{photo.object_key}"
                # 注意：这里需要实现从deleted目录恢复的功能
                # 由于OSS的copy_object需要源和目标都在同一个bucket中
                # 我们可以先复制回来，然后删除deleted目录中的文件
                oss_client.bucket.copy_object(oss_client.bucket.bucket_name, deleted_key, photo.object_key)
                oss_client.bucket.delete_object(deleted_key)
                
                # 恢复缩略图
                thumbnail_key = oss_client.generate_thumbnail_key(photo.object_key)
                deleted_thumbnail_key = f"deleted/{thumbnail_key}"
                oss_client.bucket.copy_object(oss_client.bucket.bucket_name, deleted_thumbnail_key, thumbnail_key)
                oss_client.bucket.delete_object(deleted_thumbnail_key)
                
            except Exception as e:
                logger.warning(f"从deleted目录恢复OSS文件失败: {e}")
                # 即使恢复失败，也继续标记为未删除
        
        # 恢复照片：标记为未删除，清除删除时间
        photo.deleted = False
        photo.deleted_at = None
        db.session.commit()
        
        return jsonify({'message': '照片已恢复'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"恢复照片失败: {e}")
        return jsonify({'message': '恢复照片失败'}), 500

@app.route('/api/children/<int:child_id>/milestones', methods=['GET'])
@jwt_required()
def get_milestones(child_id):
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    milestones = Milestone.query.filter_by(child_id=child_id).order_by(Milestone.date_achieved.desc()).all()
    
    result = []
    for milestone in milestones:
        result.append({
            'id': milestone.id,
            'title': milestone.title,
            'description': milestone.description,
            'date_achieved': milestone.date_achieved.strftime('%Y-%m-%d')
        })
    
    return jsonify(result), 200

@app.route('/api/children/<int:child_id>/milestones', methods=['POST'])
@jwt_required()
def add_milestone(child_id):
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    data = request.get_json()
    
    milestone = Milestone(
        title=data['title'],
        description=data.get('description', ''),
        date_achieved=datetime.strptime(data['date_achieved'], '%Y-%m-%d').date(),
        child_id=child_id
    )
    
    db.session.add(milestone)
    db.session.commit()
    
    return jsonify({'message': '成长里程碑添加成功'}), 201

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供本地存储的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
