"""
成长记录蓝图
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import db, Child, GrowthRecord

growth_bp = Blueprint('growth', __name__, url_prefix='/api/children/<int:child_id>/growth')

@growth_bp.route('', methods=['GET'])
@jwt_required()
def get_growth_records(child_id):
    """获取宝宝的成长记录"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
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

@growth_bp.route('', methods=['POST'])
@jwt_required()
def add_growth_record(child_id):
    """添加成长记录"""
    user_id_str = get_jwt_identity()
    user_id = int(user_id_str)
    
    # 验证宝宝是否属于当前用户
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['height', 'weight', 'date_recorded']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'缺少必填字段: {field}'}), 400
    
    try:
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
        
    except ValueError as e:
        return jsonify({'message': f'日期格式不正确: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'服务器内部错误: {str(e)}'}), 500