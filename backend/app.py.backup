from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import uuid
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baby_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-jwt-key-with-at-least-32-characters'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
jwt = JWTManager(app)

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
    description = db.Column(db.Text)
    date_taken = db.Column(db.Date, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_achieved = db.Column(db.Date, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)

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
        result.append({
            'id': child.id,
            'name': child.name,
            'birth_date': child.birth_date.strftime('%Y-%m-%d'),
            'gender': child.gender
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
        print(f"添加宝宝时发生错误: {str(e)}")
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

@app.route('/api/children/<int:child_id>/photos', methods=['GET'])
@jwt_required()
def get_photos(child_id):
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    photos = Photo.query.filter_by(child_id=child_id).order_by(Photo.date_taken.desc()).all()
    
    result = []
    for photo in photos:
        result.append({
            'id': photo.id,
            'filename': photo.filename,
            'description': photo.description,
            'date_taken': photo.date_taken.strftime('%Y-%m-%d'),
            'url': f'/uploads/{photo.filename}'
        })
    
    return jsonify(result), 200

@app.route('/api/children/<int:child_id>/photos', methods=['POST'])
@jwt_required()
def add_photo(child_id):
    user_id_str = get_jwt_identity()
    # 将字符串转换回整数进行数据库查询
    user_id = int(user_id_str)
    child = Child.query.filter_by(id=child_id, user_id=user_id).first()
    
    if not child:
        return jsonify({'message': '未找到宝宝信息'}), 404
    
    if 'photo' not in request.files:
        return jsonify({'message': '没有选择文件'}), 400
    
    file = request.files['photo']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if file:
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        photo = Photo(
            filename=filename,
            description=description,
            date_taken=datetime.now().date(),
            child_id=child_id
        )
        
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({'message': '照片上传成功', 'photo_id': photo.id}), 201
    
    return jsonify({'message': '上传失败'}), 500

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
