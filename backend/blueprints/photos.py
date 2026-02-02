"""
照片蓝图
"""
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

from models import db, Child, Photo
from config import Config

photos_bp = Blueprint('photos', __name__, url_prefix='/api/children/<int:child_id>/photos')

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext.replace('.', '') for ext in Config.ALLOWED_EXTENSIONS]

@photos_bp.route('', methods=['GET'])
@jwt_required()
def get_photos(child_id):
    """获取宝宝的照片"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    # 只查询未删除的照片
    photos = Photo.query.filter_by(child_id=child_id, deleted=False).order_by(Photo.date_taken.desc()).all()
    
    result = []
    for photo in photos:
        # 如果使用OSS，使用OSS的URL，否则使用本地URL
        if photo.object_key and photo.original_url:
            url = photo.original_url
        else:
            url = f'/uploads/{photo.filename}'
        
        result.append({
            'id': photo.id,
            'filename': photo.filename,
            'description': photo.description,
            'date_taken': photo.date_taken.strftime('%Y-%m-%d'),
            'url': url
        })
    
    return jsonify(result), 200

@photos_bp.route('', methods=['POST'])
@jwt_required()
def add_photo(child_id):
    """上传照片"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    if 'photo' not in request.files:
        return jsonify({'message': '没有选择文件'}), 400
    
    file = request.files['photo']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'message': '不支持的文件类型'}), 400
    
    try:
        # 生成唯一文件名
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # 确保上传目录存在
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # 保存文件
        file.save(file_path)
        
        # 创建照片记录
        photo = Photo(
            filename=filename,
            description=description,
            date_taken=datetime.now().date(),
            child_id=child_id
        )
        
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({
            'message': '照片上传成功',
            'photo_id': photo.id,
            'photo': {
                'id': photo.id,
                'filename': photo.filename,
                'description': photo.description,
                'date_taken': photo.date_taken.strftime('%Y-%m-%d'),
                'url': f'/uploads/{photo.filename}'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'上传失败: {str(e)}'}), 500

# 静态文件路由
@photos_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供本地存储的文件"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)