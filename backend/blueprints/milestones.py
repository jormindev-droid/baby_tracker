"""
里程碑蓝图
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import db, Child, Milestone

milestones_bp = Blueprint('milestones', __name__, url_prefix='/api/children/<int:child_id>/milestones')

@milestones_bp.route('', methods=['GET'])
@jwt_required()
def get_milestones(child_id):
    """获取宝宝的里程碑"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
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

@milestones_bp.route('', methods=['POST'])
@jwt_required()
def add_milestone(child_id):
    """添加里程碑"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['title', 'date_achieved']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'缺少必填字段: {field}'}), 400
    
    try:
        milestone = Milestone(
            title=data['title'],
            description=data.get('description', ''),
            date_achieved=datetime.strptime(data['date_achieved'], '%Y-%m-%d').date(),
            child_id=child_id
        )
        
        db.session.add(milestone)
        db.session.commit()
        
        return jsonify({'message': '成长里程碑添加成功'}), 201
        
    except ValueError as e:
        return jsonify({'message': f'日期格式不正确: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'服务器内部错误: {str(e)}'}), 500