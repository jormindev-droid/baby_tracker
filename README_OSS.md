# 阿里云OSS集成指南

本文档介绍如何在宝宝成长追踪器中配置和使用阿里云OSS进行图片存储。

## 1. 创建阿里云OSS资源

### 1.1 开通OSS服务
1. 登录阿里云控制台：https://oss.console.aliyun.com/
2. 如果没有开通OSS服务，按照提示开通

### 1.2 创建Bucket
1. 点击"创建Bucket"
2. 配置Bucket：
   - **Bucket名称**：自定义一个唯一的名称（如：baby-growth-tracker）
   - **地域**：选择离您最近的区域（如：华东1（杭州））
   - **存储类型**：标准存储
   - **读写权限**：公共读（推荐）或私有（需要配置CORS）
   - **版本控制**：关闭
   - **实时日志查询**：关闭
3. 点击"确定"创建Bucket

### 1.3 获取访问密钥
1. 进入RAM访问控制：https://ram.console.aliyun.com/users
2. 创建用户或使用现有用户
3. 获取AccessKey ID和AccessKey Secret
4. 为用户添加AliyunOSSFullAccess权限

## 2. 配置应用程序

### 2.1 创建配置文件
1. 在用户目录下创建配置文件：
   ```bash
   mkdir -p ~/.baby_tracker
   cp config.example.yml ~/.baby_tracker/config.yml
   ```

2. 编辑配置文件：
   ```bash
   nano ~/.baby_tracker/config.yml
   ```

3. 修改以下配置项：
   ```yaml
   aliyun_oss:
     access_key_id: "您的AccessKey ID"
     access_key_secret: "您的AccessKey Secret"
     endpoint: "oss-cn-hangzhou.aliyuncs.com"  # 根据您的Bucket地域修改
     bucket_name: "您的Bucket名称"
     region: "cn-hangzhou"  # 根据您的Bucket地域修改
   ```

### 2.2 配置CORS（如果Bucket为私有）
如果Bucket设置为私有，需要配置CORS：

1. 在OSS控制台选择您的Bucket
2. 点击"权限管理" -> "跨域设置"
3. 点击"设置"
4. 添加以下规则：
   - **来源**：`*` 或您的域名
   - **允许Methods**：GET, PUT, POST, DELETE
   - **允许Headers**：`*`
   - **暴露Headers**：ETag
   - **缓存时间**：3600

## 3. 功能特性

### 3.1 Web直传
- 前端直接上传到OSS，减轻服务器负担
- 支持大文件上传
- 自动生成预签名URL

### 3.2 缩略图生成
- 自动生成300x300的缩略图
- 保持图片宽高比
- 支持多种图片格式

### 3.3 智能回退
- 如果OSS配置不可用，自动回退到本地存储
- 无缝切换，无需修改代码

## 4. 文件存储结构

```
baby_tracker/
├── {user_id}/
│   └── {child_id}/
│       ├── {uuid}.jpg          # 原始图片
│       └── {uuid}_thumbnail.jpg # 缩略图
```

## 5. API接口

### 5.1 获取上传签名
```
GET /api/oss/signature?child_id={child_id}&filename={filename}
```

**响应：**
```json
{
  "upload_url": "https://bucket.oss-cn-hangzhou.aliyuncs.com/...",
  "object_key": "baby_tracker/1/1/uuid.jpg",
  "expire_time": 3600
}
```

### 5.2 上传图片
1. 获取上传签名
2. 使用PUT方法直接上传到`upload_url`
3. 调用后端API创建图片记录

### 5.3 获取图片列表
```
GET /api/children/{child_id}/photos
```

**响应：**
```json
[
  {
    "id": 1,
    "filename": "photo.jpg",
    "original_url": "https://...",
    "thumbnail_url": "https://...",
    "description": "宝宝照片",
    "date_taken": "2024-01-01"
  }
]
```

## 6. 故障排除

### 6.1 上传失败
1. 检查AccessKey是否正确
2. 检查Bucket名称和地域是否正确
3. 检查Bucket权限设置
4. 检查CORS配置

### 6.2 图片无法显示
1. 检查图片URL是否正确
2. 检查Bucket是否为公共读
3. 检查网络连接

### 6.3 缩略图未生成
1. 检查Pillow库是否正确安装
2. 检查图片格式是否支持
3. 查看服务器日志

## 7. 性能优化建议

### 7.1 CDN加速
- 为OSS Bucket配置CDN加速
- 减少图片加载时间

### 7.2 图片优化
- 前端上传前压缩图片
- 使用WebP格式减少文件大小
- 设置合适的缩略图尺寸

### 7.3 监控告警
- 配置OSS监控告警
- 监控存储空间使用情况
- 设置流量告警

## 8. 安全注意事项

1. **保护AccessKey**：不要将AccessKey提交到代码仓库
2. **最小权限原则**：为RAM用户分配最小必要权限
3. **定期轮换密钥**：定期更换AccessKey
4. **监控异常访问**：定期检查访问日志
5. **设置防盗链**：配置Referer白名单

## 9. 成本控制

1. **存储费用**：根据实际使用量计费
2. **流量费用**：外网下载会产生流量费用
3. **请求费用**：API调用次数计费
4. **CDN费用**：如果使用CDN加速

建议：
- 定期清理不需要的图片
- 使用合适的存储类型
- 配置生命周期规则自动清理旧文件

## 10. 迁移指南

### 10.1 从本地存储迁移到OSS
1. 配置OSS并测试上传功能
2. 编写迁移脚本将现有图片上传到OSS
3. 更新数据库中的图片URL
4. 验证迁移后的功能

### 10.2 从OSS迁移到其他存储
1. 下载所有OSS文件到本地
2. 配置新的存储服务
3. 上传文件到新存储
4. 更新数据库中的图片URL

## 支持与反馈

如有问题，请：
1. 查看服务器日志
2. 检查配置文件
3. 参考阿里云官方文档
4. 提交Issue到项目仓库