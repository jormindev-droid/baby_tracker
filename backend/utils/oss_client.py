import os
import yaml
import uuid
import oss2
from PIL import Image
import io
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OSSClient:
    """阿里云OSS客户端"""
    
    def __init__(self, config_path: str = None):
        """
        初始化OSS客户端
        
        Args:
            config_path: 配置文件路径，默认为用户目录下的.baby_tracker/config.yml
        """
        if config_path is None:
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, ".baby_tracker", "config.yml")
        
        self.config_path = config_path
        self.config = self._load_config()
        self._init_oss_client()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请创建配置文件，可以参考项目根目录下的config.example.yml"
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 验证必要的配置项
        required_keys = ['aliyun_oss']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"配置文件中缺少必要的键: {key}")
        
        oss_config = config['aliyun_oss']
        required_oss_keys = ['access_key_id', 'access_key_secret', 'endpoint', 'bucket_name']
        for key in required_oss_keys:
            if key not in oss_config:
                raise ValueError(f"阿里云OSS配置中缺少必要的键: {key}")
        
        return config
    
    def _init_oss_client(self):
        """初始化OSS客户端"""
        oss_config = self.config['aliyun_oss']
        
        # 创建认证对象
        auth = oss2.Auth(
            oss_config['access_key_id'],
            oss_config['access_key_secret']
        )
        
        # 创建Bucket对象
        self.bucket = oss2.Bucket(
            auth,
            oss_config['endpoint'],
            oss_config['bucket_name']
        )
        
        # 存储其他配置
        self.upload_prefix = oss_config.get('upload_prefix', 'baby_tracker/')
        self.thumbnail_suffix = oss_config.get('thumbnail_suffix', '_thumbnail')
        self.thumbnail_width = oss_config.get('thumbnail_width', 300)
        self.thumbnail_height = oss_config.get('thumbnail_height', 300)
        self.thumbnail_quality = oss_config.get('thumbnail_quality', 80)
        self.expire_time = oss_config.get('expire_time', 3600)
        self.max_size = oss_config.get('max_size', 10485760)  # 10MB
        
        logger.info(f"OSS客户端初始化成功，Bucket: {oss_config['bucket_name']}")
    
    def generate_object_key(self, filename: str, user_id: int, child_id: int) -> str:
        """
        生成OSS对象键
        
        Args:
            filename: 原始文件名
            user_id: 用户ID
            child_id: 宝宝ID
            
        Returns:
            OSS对象键
        """
        # 获取文件扩展名
        ext = os.path.splitext(filename)[1].lower()
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # 构建对象键：upload_prefix/user_id/child_id/unique_filename
        object_key = f"{self.upload_prefix}{user_id}/{child_id}/{unique_filename}"
        
        return object_key
    
    def generate_thumbnail_key(self, original_key: str) -> str:
        """
        生成缩略图的对象键
        
        Args:
            original_key: 原始图片的对象键
            
        Returns:
            缩略图的对象键
        """
        # 分离文件名和扩展名
        base, ext = os.path.splitext(original_key)
        
        # 添加缩略图后缀
        thumbnail_key = f"{base}{self.thumbnail_suffix}{ext}"
        
        return thumbnail_key
    
    def create_thumbnail(self, image_data: bytes) -> bytes:
        """
        创建缩略图
        
        Args:
            image_data: 原始图片数据
            
        Returns:
            缩略图数据
        """
        try:
            # 打开图片
            image = Image.open(io.BytesIO(image_data))
            
            # 转换模式为RGB（如果是RGBA）
            if image.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 计算缩略图尺寸，保持宽高比
            original_width, original_height = image.size
            ratio = min(
                self.thumbnail_width / original_width,
                self.thumbnail_height / original_height
            )
            
            if ratio < 1:
                # 需要缩小
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.thumbnail_quality, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"创建缩略图失败: {e}")
            raise
    
    def upload_file(self, file_data: bytes, object_key: str, content_type: str = None) -> str:
        """
        上传文件到OSS
        
        Args:
            file_data: 文件数据
            object_key: OSS对象键
            content_type: 文件类型
            
        Returns:
            文件的URL
        """
        try:
            # 上传文件
            result = self.bucket.put_object(
                object_key,
                file_data,
                headers={'Content-Type': content_type} if content_type else None
            )
            
            if result.status != 200:
                raise Exception(f"上传文件失败，状态码: {result.status}")
            
            # 生成文件的URL
            url = self.bucket.sign_url('GET', object_key, self.expire_time)
            
            logger.info(f"文件上传成功: {object_key}")
            return url
            
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            raise
    
    def upload_image_with_thumbnail(self, image_data: bytes, filename: str, 
                                   user_id: int, child_id: int) -> Tuple[str, str]:
        """
        上传图片并生成缩略图
        
        Args:
            image_data: 图片数据
            filename: 原始文件名
            user_id: 用户ID
            child_id: 宝宝ID
            
        Returns:
            (原始图片URL, 缩略图URL)
        """
        try:
            # 生成对象键
            original_key = self.generate_object_key(filename, user_id, child_id)
            
            # 上传原始图片
            original_url = self.upload_file(
                image_data,
                original_key,
                content_type=self._get_content_type(filename)
            )
            
            # 生成缩略图
            try:
                thumbnail_data = self.create_thumbnail(image_data)
                thumbnail_key = self.generate_thumbnail_key(original_key)
                thumbnail_url = self.upload_file(
                    thumbnail_data,
                    thumbnail_key,
                    content_type='image/jpeg'
                )
            except Exception as e:
                logger.warning(f"生成缩略图失败，继续使用原始图片: {e}")
                thumbnail_url = original_url
            
            return original_url, thumbnail_url
            
        except Exception as e:
            logger.error(f"上传图片失败: {e}")
            raise
    
    def delete_file(self, object_key: str):
        """
        删除OSS上的文件
        
        Args:
            object_key: OSS对象键
        """
        try:
            self.bucket.delete_object(object_key)
            logger.info(f"文件删除成功: {object_key}")
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            raise
    
    def move_to_deleted(self, original_key: str):
        """
        移动文件到deleted目录
        
        Args:
            original_key: 原始图片的对象键
        """
        try:
            # 生成deleted目录下的新对象键
            # 格式: deleted/{original_key}
            deleted_key = f"deleted/{original_key}"
            
            # 移动原始图片
            self.bucket.copy_object(self.bucket.bucket_name, original_key, deleted_key)
            self.bucket.delete_object(original_key)
            
            # 移动缩略图
            thumbnail_key = self.generate_thumbnail_key(original_key)
            deleted_thumbnail_key = f"deleted/{thumbnail_key}"
            self.bucket.copy_object(self.bucket.bucket_name, thumbnail_key, deleted_thumbnail_key)
            self.bucket.delete_object(thumbnail_key)
            
            logger.info(f"文件移动到deleted目录成功: {original_key}")
            
        except Exception as e:
            logger.error(f"移动文件到deleted目录失败: {e}")
            raise
    
    def delete_image_with_thumbnail(self, original_key: str):
        """
        删除图片及其缩略图
        
        Args:
            original_key: 原始图片的对象键
        """
        try:
            # 删除原始图片
            self.delete_file(original_key)
            
            # 删除缩略图
            thumbnail_key = self.generate_thumbnail_key(original_key)
            self.delete_file(thumbnail_key)
            
        except Exception as e:
            logger.error(f"删除图片失败: {e}")
            raise
    
    def get_presigned_url(self, object_key: str, method: str = 'GET', 
                         expire_time: int = None) -> str:
        """
        获取预签名URL
        
        Args:
            object_key: OSS对象键
            method: HTTP方法（GET/PUT等）
            expire_time: 过期时间（秒）
            
        Returns:
            预签名URL
        """
        if expire_time is None:
            expire_time = self.expire_time
        
        return self.bucket.sign_url(method, object_key, expire_time)
    
    def _get_content_type(self, filename: str) -> str:
        """根据文件名获取Content-Type"""
        ext = os.path.splitext(filename)[1].lower()
        
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
        }
        
        return content_types.get(ext, 'application/octet-stream')
    
    def validate_file_size(self, file_size: int) -> bool:
        """验证文件大小是否在限制范围内"""
        return file_size <= self.max_size
    
    def validate_file_extension(self, filename: str) -> bool:
        """验证文件扩展名是否允许"""
        ext = os.path.splitext(filename)[1].lower()
        
        allowed_extensions = self.config.get('upload', {}).get('allowed_extensions', 
            ['.jpg', '.jpeg', '.png', '.gif', '.bmp'])
        
        return ext in allowed_extensions