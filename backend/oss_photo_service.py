"""
阿里云OSS照片服务模块
将OSS相关功能从app.py中分离出来
"""
import os
import logging
from typing import Dict, Any, Optional, Tuple
from flask import request, jsonify
from datetime import datetime
import uuid

from utils.oss_client import OSSClient
from utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class OSSPhotoService:
    """OSS照片服务"""
    
    def __init__(self):
        self.oss_client = None
        self.config = None
        self._init_oss_client()
    
    def _init_oss_client(self):
        """初始化OSS客户端"""
        try:
            # 尝试加载配置文件
            config = ConfigLoader.load_config()
            self.config = config
            
            # 初始化OSS客户端
            self.oss_client = OSSClient()
            logger.info("阿里云OSS客户端初始化成功")
            
        except Exception as e:
            logger.warning(f"阿里云OSS客户端初始化失败，将使用本地存储: {e}")
            self.oss_client = None
    
    def is_oss_available(self) -> bool:
        """检查OSS是否可用"""
        return self.oss_client is not None
    
    def get_oss_signature(self, user_id: int, child_id: int, filename: str) -> Dict[str, Any]:
        """
        获取OSS Web直传签名
        
        Args:
            user_id: 用户ID
            child_id: 宝宝ID
            filename: 文件名
            
        Returns:
            包含上传URL和对象键的字典
        """
        if not self.is_oss_available():
            return {
                'error': 'OSS服务未配置',
                'status': 503
            }
        
        try:
            # 验证文件扩展名
            if not self.oss_client.validate_file_extension(filename):
                return {
                    'error': '不支持的文件类型',
                    'status': 400
                }
            
            # 生成对象键
            object_key = self.oss_client.generate_object_key(filename, user_id, child_id)
            
            # 生成预签名URL（用于PUT上传）
            upload_url = self.oss_client.bucket.sign_url('PUT', object_key, 3600)
            
            # 解码URL，确保格式正确
            import urllib.parse
            decoded_url = urllib.parse.unquote(upload_url)
            
            return {
                'upload_url': decoded_url,
                'object_key': object_key,
                'expire_time': 3600,
                'status': 200
            }
            
        except Exception as e:
            logger.error(f"获取OSS签名失败: {e}")
            return {
                'error': f'获取上传签名失败: {str(e)}',
                'status': 500
            }
    
    def upload_photo_via_backend(self, file, user_id: int, child_id: int, description: str = '') -> Dict[str, Any]:
        """
        通过后端代理上传照片到OSS
        
        Args:
            file: 上传的文件对象
            user_id: 用户ID
            child_id: 宝宝ID
            description: 照片描述
            
        Returns:
            包含照片信息的字典
        """
        if not self.is_oss_available():
            return {
                'error': 'OSS服务未配置',
                'status': 503
            }
        
        try:
            # 读取文件数据
            file_data = file.read()
            
            # 上传到OSS
            original_url, thumbnail_url = self.oss_client.upload_image_with_thumbnail(
                file_data, file.filename, user_id, child_id
            )
            
            # 从URL中提取object_key
            import urllib.parse
            parsed_url = urllib.parse.urlparse(original_url)
            object_key = parsed_url.path.lstrip('/').split('?')[0]
            
            # 从object_key中提取UUID文件名
            uuid_filename = os.path.basename(object_key)
            
            return {
                'filename': uuid_filename,
                'object_key': object_key,
                'original_url': original_url,
                'thumbnail_url': thumbnail_url,
                'description': description,
                'date_taken': datetime.now().date(),
                'status': 201
            }
            
        except Exception as e:
            logger.error(f"上传到OSS失败: {e}")
            return {
                'error': f'上传到OSS失败: {str(e)}',
                'status': 500
            }
    
    def get_photo_urls(self, photo_object_key: str) -> Dict[str, str]:
        """
        获取照片的URL（带签名）
        
        Args:
            photo_object_key: 照片的对象键
            
        Returns:
            包含原始URL和缩略图URL的字典
        """
        if not self.is_oss_available() or not photo_object_key:
            return {
                'original_url': None,
                'thumbnail_url': None
            }
        
        try:
            # 生成新的带签名URL
            original_url = self.oss_client.get_presigned_url(photo_object_key, 'GET')
            
            # 生成缩略图的带签名URL
            thumbnail_key = self.oss_client.generate_thumbnail_key(photo_object_key)
            try:
                # 检查缩略图是否存在
                self.oss_client.bucket.get_object_meta(thumbnail_key)
                thumbnail_url = self.oss_client.get_presigned_url(thumbnail_key, 'GET')
            except:
                # 缩略图不存在，使用原始图片
                thumbnail_url = original_url
            
            return {
                'original_url': original_url,
                'thumbnail_url': thumbnail_url
            }
            
        except Exception as e:
            logger.warning(f"生成临时URL失败: {e}")
            return {
                'original_url': None,
                'thumbnail_url': None
            }
    
    def delete_photo(self, photo_object_key: str) -> bool:
        """
        逻辑删除照片（移动到deleted目录）
        
        Args:
            photo_object_key: 照片的对象键
            
        Returns:
            是否成功
        """
        if not self.is_oss_available() or not photo_object_key:
            return False
        
        try:
            # 将OSS文件移动到deleted目录
            self.oss_client.move_to_deleted(photo_object_key)
            return True
            
        except Exception as e:
            logger.warning(f"移动OSS文件到deleted目录失败: {e}")
            return False
    
    def restore_photo(self, photo_object_key: str) -> bool:
        """
        恢复已删除的照片
        
        Args:
            photo_object_key: 照片的对象键
            
        Returns:
            是否成功
        """
        if not self.is_oss_available() or not photo_object_key:
            return False
        
        try:
            # 从deleted目录移回原位置
            deleted_key = f"deleted/{photo_object_key}"
            
            # 复制回来，然后删除deleted目录中的文件
            self.oss_client.bucket.copy_object(self.oss_client.bucket.bucket_name, deleted_key, photo_object_key)
            self.oss_client.bucket.delete_object(deleted_key)
            
            # 恢复缩略图
            thumbnail_key = self.oss_client.generate_thumbnail_key(photo_object_key)
            deleted_thumbnail_key = f"deleted/{thumbnail_key}"
            self.oss_client.bucket.copy_object(self.oss_client.bucket.bucket_name, deleted_thumbnail_key, thumbnail_key)
            self.oss_client.bucket.delete_object(deleted_thumbnail_key)
            
            return True
            
        except Exception as e:
            logger.warning(f"从deleted目录恢复OSS文件失败: {e}")
            return False

# 创建全局OSS照片服务实例
oss_photo_service = OSSPhotoService()