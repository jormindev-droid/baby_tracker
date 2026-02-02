"""
宝宝模型
"""
from . import db

class Child(db.Model):
    """宝宝表"""
    __tablename__ = 'child'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 关系
    growth_records = db.relationship('GrowthRecord', backref='child', lazy=True)
    photos = db.relationship('Photo', backref='child', lazy=True)
    milestones = db.relationship('Milestone', backref='child', lazy=True)
    
    def __repr__(self):
        return f'<Child {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'birth_date': self.birth_date.strftime('%Y-%m-%d'),
            'gender': self.gender,
            'user_id': self.user_id
        }