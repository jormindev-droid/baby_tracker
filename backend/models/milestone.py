"""
里程碑模型
"""
from . import db

class Milestone(db.Model):
    """里程碑表"""
    __tablename__ = 'milestone'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_achieved = db.Column(db.Date, nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    
    def __repr__(self):
        return f'<Milestone {self.title}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date_achieved': self.date_achieved.strftime('%Y-%m-%d'),
            'child_id': self.child_id
        }