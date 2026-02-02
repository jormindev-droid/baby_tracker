import os
import yaml
from typing import Dict, Any

class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def load_config(config_path: str = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，默认为用户目录下的.baby_tracker/config.yml
            
        Returns:
            配置字典
        """
        if config_path is None:
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, ".baby_tracker", "config.yml")
        
        if not os.path.exists(config_path):
            # 尝试从项目根目录加载示例配置
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            example_config = os.path.join(project_root, "config.example.yml")
            
            if os.path.exists(example_config):
                raise FileNotFoundError(
                    f"配置文件不存在: {config_path}\n"
                    f"请创建配置文件，可以参考: {example_config}\n"
                    f"或者运行: cp {example_config} {config_path} 并编辑配置"
                )
            else:
                raise FileNotFoundError(
                    f"配置文件不存在: {config_path}\n"
                    f"请创建配置文件，包含阿里云OSS配置"
                )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    @staticmethod
    def get_oss_config(config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取OSS配置
        
        Args:
            config: 配置字典，如果为None则从默认路径加载
            
        Returns:
            OSS配置字典
        """
        if config is None:
            config = ConfigLoader.load_config()
        
        if 'aliyun_oss' not in config:
            raise ValueError("配置文件中缺少 'aliyun_oss' 配置")
        
        return config['aliyun_oss']
    
    @staticmethod
    def get_app_config(config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取应用配置
        
        Args:
            config: 配置字典，如果为None则从默认路径加载
            
        Returns:
            应用配置字典
        """
        if config is None:
            config = ConfigLoader.load_config()
        
        return config.get('app', {})
    
    @staticmethod
    def get_upload_config(config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取上传配置
        
        Args:
            config: 配置字典，如果为None则从默认路径加载
            
        Returns:
            上传配置字典
        """
        if config is None:
            config = ConfigLoader.load_config()
        
        return config.get('upload', {})