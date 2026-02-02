"""
数据库模型定义
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入所有模型
from .user import User
from .child import Child
from .growth_record import GrowthRecord
from .photo import Photo
from .milestone import Milestone

__all__ = ['db', 'User', 'Child', 'GrowthRecord', 'Photo', 'Milestone']