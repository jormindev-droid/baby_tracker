"""
宝宝管理蓝图
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import db, Child, GrowthRecord, Photo, Milestone

children_bp = Blueprint('children', __name__, url_prefix='/api/children')

@children_bp.route('', methods=['GET'])
@jwt_required()
def get_children():
    """获取用户的所有宝宝"""
    user_id_str = get_jwt_identity()
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

@children_bp.route('', methods=['POST'])
@jwt_required()
def add_child():
    """添加宝宝"""
    try:
        user_id_str = get_jwt_identity()
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
        return jsonify({'message': f'服务器内部错误: {str(e)}'}), 500