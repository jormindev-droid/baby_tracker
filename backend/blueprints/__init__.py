"""
蓝图模块
"""
from .auth import auth_bp
from .children import children_bp
from .growth import growth_bp
from .photos import photos_bp
from .milestones import milestones_bp

# 所有蓝图
blueprints = [
    auth_bp,
    children_bp,
    growth_bp,
    photos_bp,
    milestones_bp
]

__all__ = ['blueprints', 'auth_bp', 'children_bp', 'growth_bp', 'photos_bp', 'milestones_bp']