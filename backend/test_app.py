"""
测试应用
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_app():
    """测试应用创建和路由"""
    print("=== 测试宝宝成长追踪器应用 ===")
    
    # 创建应用
    app = create_app()
    print("✓ 应用创建成功")
    
    # 检查路由
    routes = list(app.url_map.iter_rules())
    print(f"✓ 注册了 {len(routes)} 个路由")
    
    # 显示API路由
    print("\nAPI路由:")
    for route in routes:
        if route.rule.startswith('/api'):
            print(f"  {route.rule}")
    
    # 检查数据库连接
    with app.app_context():
        from models import db
        try:
            db.engine.connect()
            print("✓ 数据库连接成功")
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_app()