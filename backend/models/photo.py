"""
照片模型
"""
from . import db

class Photo(db.Model):
    """照片表"""
    __tablename__ = 'photo'
    
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
    
    def __repr__(self):
        return f'<Photo {self.filename}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'object_key': self.object_key,
            'original_url': self.original_url,
            'thumbnail_url': self.thumbnail_url,
            'description': self.description,
            'date_taken': self.date_taken.strftime('%Y-%m-%d'),
            'child_id': self.child_id,
            'deleted': self.deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }