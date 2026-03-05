import yaml
import os
from typing import Any, Optional


class Config:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, config_path: str = "config.yaml") -> None:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        self._override_from_env()
    
    def _override_from_env(self) -> None:
        if os.getenv('DEEPSEEK_API_KEY'):
            if self._config and 'deepseek' in self._config:
                self._config['deepseek']['api_key'] = os.getenv('DEEPSEEK_API_KEY')
        if os.getenv('REDIS_HOST'):
            if self._config and 'redis' in self._config:
                self._config['redis']['host'] = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PASSWORD'):
            if self._config and 'redis' in self._config:
                self._config['redis']['password'] = os.getenv('REDIS_PASSWORD')
        if os.getenv('OSS_ACCESS_KEY_ID'):
            if self._config and 'oss' in self._config:
                self._config['oss']['access_key_id'] = os.getenv('OSS_ACCESS_KEY_ID')
        if os.getenv('OSS_ACCESS_KEY_SECRET'):
            if self._config and 'oss' in self._config:
                self._config['oss']['access_key_secret'] = os.getenv('OSS_ACCESS_KEY_SECRET')
    
    def get(self, key: str, default: Any = None) -> Any:
        if self._config is None:
            return default
        
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def get_deepseek_config(self) -> dict:
        return self.get('deepseek', {})
    
    def get_redis_config(self) -> dict:
        return self.get('redis', {})
    
    def get_oss_config(self) -> dict:
        return self.get('oss', {})
    
    def get_cache_config(self) -> dict:
        return self.get('cache', {})
    
    def get_match_config(self) -> dict:
        return self.get('match', {})
    
    def get_pdf_config(self) -> dict:
        return self.get('pdf', {})


config = Config()
