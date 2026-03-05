import json
from typing import Any, Dict, Optional

import redis
from redis.connection import ConnectionPool

from ..config.settings import config
from .helpers import CacheError


class Cache:
    def __init__(self):
        self._pool = None
        self._client = None
        self._initialized = False
    
    def _ensure_initialized(self):
        if self._initialized:
            return
        
        redis_config = config.get_redis_config()
        
        self._pool = ConnectionPool(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            password=redis_config.get('password'),
            db=redis_config.get('db', 0),
            max_connections=redis_config.get('max_connections', 10),
            decode_responses=True
        )
        self._client = redis.Redis(connection_pool=self._pool)
        
        cache_config = config.get_cache_config()
        self.resume_parse_ttl = cache_config.get('resume_parse_ttl', 86400)
        self.job_parse_ttl = cache_config.get('job_parse_ttl', 604800)
        self.match_result_ttl = cache_config.get('match_result_ttl', 3600)
        self.semantic_match_ttl = cache_config.get('semantic_match_ttl', 604800)
        
        self._initialized = True
    
    @property
    def client(self):
        self._ensure_initialized()
        return self._client
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            raise CacheError(f"缓存读取失败: {str(e)}")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        """
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            if ttl:
                return self.client.setex(key, ttl, json_value)
            return self.client.set(key, json_value)
        except Exception as e:
            raise CacheError(f"缓存写入失败: {str(e)}")
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        """
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            raise CacheError(f"缓存删除失败: {str(e)}")
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        """
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            raise CacheError(f"缓存检查失败: {str(e)}")
    
    def get_resume_parse(self, file_hash: str) -> Optional[Dict]:
        """
        获取简历解析缓存
        """
        key = f"resume:parse:{file_hash}"
        return self.get(key)
    
    def set_resume_parse(self, file_hash: str, data: Dict, ttl: Optional[int] = None) -> bool:
        """
        设置简历解析缓存
        """
        key = f"resume:parse:{file_hash}"
        return self.set(key, data, ttl or self.resume_parse_ttl)
    
    def get_job_parse(self, job_hash: str) -> Optional[Dict]:
        """
        获取岗位解析缓存
        """
        key = f"job:parse:{job_hash}"
        return self.get(key)
    
    def set_job_parse(self, job_hash: str, data: Dict, ttl: Optional[int] = None) -> bool:
        """
        设置岗位解析缓存
        """
        key = f"job:parse:{job_hash}"
        return self.set(key, data, ttl or self.job_parse_ttl)
    
    def get_match_result(self, resume_hash: str, job_hash: str, mode: str = 'standard') -> Optional[Dict]:
        """
        获取匹配结果缓存
        """
        key = f"match:result:{resume_hash}:{job_hash}:{mode}"
        return self.get(key)
    
    def set_match_result(
        self, 
        resume_hash: str, 
        job_hash: str, 
        data: Dict, 
        mode: str = 'standard',
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置匹配结果缓存
        """
        key = f"match:result:{resume_hash}:{job_hash}:{mode}"
        return self.set(key, data, ttl or self.match_result_ttl)
    
    def get_semantic_match(self, resume_hash: str, job_hash: str) -> Optional[Dict]:
        """
        获取语义匹配缓存
        """
        key = f"semantic:match:{resume_hash}:{job_hash}"
        return self.get(key)
    
    def set_semantic_match(
        self, 
        resume_hash: str, 
        job_hash: str, 
        data: Dict, 
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置语义匹配缓存
        """
        key = f"semantic:match:{resume_hash}:{job_hash}"
        return self.set(key, data, ttl or self.semantic_match_ttl)
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        获取任务状态
        """
        key = f"task:{task_id}"
        return self.get(key)
    
    def set_task(self, task_id: str, data: Dict, ttl: int = 3600) -> bool:
        """
        设置任务状态
        """
        key = f"task:{task_id}"
        return self.set(key, data, ttl)
    
    def get_resume_list(self) -> Optional[Dict]:
        """
        获取简历列表缓存
        """
        key = "resume:list"
        return self.get(key)
    
    def set_resume_list(self, data: Dict, ttl: int = 3600) -> bool:
        """
        设置简历列表缓存
        """
        key = "resume:list"
        return self.set(key, data, ttl)
    
    def get_job_list(self) -> Optional[Dict]:
        """
        获取岗位列表缓存
        """
        key = "job:list"
        return self.get(key)
    
    def set_job_list(self, data: Dict, ttl: int = 3600) -> bool:
        """
        设置岗位列表缓存
        """
        key = "job:list"
        return self.set(key, data, ttl)


cache = None

def get_cache() -> Cache:
    """
    获取缓存客户端单例
    """
    global cache
    if cache is None:
        cache = Cache()
    return cache
