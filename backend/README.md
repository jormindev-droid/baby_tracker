# 宝宝成长追踪器 - 后端

基于Flask的宝宝成长追踪器后端服务，采用模块化架构设计。

## 项目结构

```
backend/
├── app.py                    # 应用入口文件
├── requirements.txt          # Python依赖
├── test_app.py              # 应用测试脚本
├── uploads/                 # 文件上传目录
├── migrations/              # 数据库迁移目录
├── config/                  # 配置模块
│   ├── __init__.py         # 配置基类
├── models/                  # 数据模型
│   ├── __init__.py         # 数据库实例和模型导入
│   ├── user.py             # 用户模型
│   ├── child.py            # 宝宝模型
│   ├── growth_record.py    # 成长记录模型
│   ├── photo.py            # 照片模型
│   └── milestone.py        # 里程碑模型
├── blueprints/             # 蓝图模块
│   ├── __init__.py         # 蓝图注册
│   ├── auth.py             # 认证蓝图
│   ├── children.py         # 宝宝管理蓝图
│   ├── growth.py           # 成长记录蓝图
│   ├── photos.py           # 照片管理蓝图
│   └── milestones.py       # 里程碑蓝图
├── services/               # 服务层（可选）
├── utils/                  # 工具模块
│   ├── config_loader.py    # 配置加载器
│   └── oss_client.py       # OSS客户端
└── oss_photo_service.py    # OSS照片服务
```

## 架构设计

### 1. 模块化设计
- **app.py**: 应用入口，只负责启动和配置
- **config/**: 配置管理，支持不同环境配置
- **models/**: 数据模型定义，使用SQLAlchemy ORM
- **blueprints/**: 业务逻辑，按功能模块拆分
- **utils/**: 工具函数和第三方服务集成

### 2. 配置管理
支持开发环境和生产环境配置：
```python
# 开发环境
app = create_app('development')

# 生产环境
app = create_app('production')
```

### 3. 数据库
- 使用SQLite作为默认数据库
- 支持Flask-Migrate进行数据库迁移
- 模型定义在`models/`目录中

### 4. API设计
- RESTful API设计
- JWT认证
- 按功能模块组织路由

## 快速开始

### 1. 安装依赖
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. 启动服务器
```bash
python app.py
```
服务器将在 http://localhost:5001 启动

### 4. 测试应用
```bash
python test_app.py
```

## API文档

### 认证
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录

### 宝宝管理
- `GET /api/children` - 获取所有宝宝
- `POST /api/children` - 添加宝宝

### 成长记录
- `GET /api/children/<child_id>/growth` - 获取成长记录
- `POST /api/children/<child_id>/growth` - 添加成长记录

### 照片管理
- `GET /api/children/<child_id>/photos` - 获取照片
- `POST /api/children/<child_id>/photos` - 上传照片
- `GET /api/children/<child_id>/photos/uploads/<filename>` - 获取照片文件

### 里程碑
- `GET /api/children/<child_id>/milestones` - 获取里程碑
- `POST /api/children/<child_id>/milestones` - 添加里程碑

## 配置说明

### 环境变量
- `SECRET_KEY`: Flask应用密钥
- `JWT_SECRET_KEY`: JWT密钥
- `DATABASE_URL`: 数据库连接URL

### 配置文件
可以通过环境变量或修改`config/__init__.py`中的配置类来调整应用配置。

## 开发指南

### 1. 添加新功能
1. 在`models/`中添加数据模型
2. 在`blueprints/`中添加蓝图
3. 在`config/`中更新配置（如果需要）
4. 运行数据库迁移

### 2. 数据库迁移
```bash
# 创建迁移
flask db migrate -m "描述"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

### 3. 测试
```bash
# 运行应用测试
python test_app.py

# 启动开发服务器
python app.py
```

## 部署

### 生产环境配置
1. 设置环境变量：
   ```bash
   export SECRET_KEY='your-secret-key'
   export JWT_SECRET_KEY='your-jwt-secret-key'
   export DATABASE_URL='sqlite:///production.db'
   ```

2. 使用生产配置启动：
   ```python
   app = create_app('production')
   ```

### 使用Gunicorn部署
```bash
gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app('production')"
```

## 故障排除

### 常见问题
1. **数据库连接失败**: 检查数据库文件权限
2. **导入错误**: 确保所有依赖已安装
3. **路由404**: 检查蓝图注册是否正确

### 日志
应用日志会输出到控制台，可以通过配置调整日志级别。

## 许可证
MIT License