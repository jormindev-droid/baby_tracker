"""
成长记录模型
"""
from . import db

class GrowthRecord(db.Model):
    """成长记录表"""
    __tablename__ = 'growth_record'
    
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    head_circumference = db.Column(db.Float)
    date_recorded = db.Column(db.Date, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    
    def __repr__(self):
        return f'<GrowthRecord {self.date_recorded}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'height': self.height,
            'weight': self.weight,
            'head_circumference': self.head_circumference,
            'date_recorded': self.date_recorded.strftime('%Y-%m-%d'),
            'child_id': self.child_id
        }