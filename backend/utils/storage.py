import os
from typing import Dict, Optional

import oss2

from ..config.settings import config
from .helpers import generate_file_hash


class Storage:
    def __init__(self):
        oss_config = config.get_oss_config()
        
        self.auth = oss2.Auth(
            oss_config.get('access_key_id'),
            oss_config.get('access_key_secret')
        )
        self.bucket = oss2.Bucket(
            self.auth,
            oss_config.get('endpoint'),
            oss_config.get('bucket')
        )
        self.bucket_name = oss_config.get('bucket')
    
    def upload_file(
        self, 
        file_content: bytes, 
        file_name: str,
        folder: str = "resumes"
    ) -> Dict:
        """
        上传文件到OSS
        
        Returns:
            {
                'file_hash': '文件哈希',
                'object_key': 'OSS对象键',
                'url': '访问URL'
            }
        """
        file_hash = generate_file_hash(file_content)
        extension = os.path.splitext(file_name)[1] or '.pdf'
        object_key = f"{folder}/{file_hash}{extension}"
        
        self.bucket.put_object(object_key, file_content)
        
        url = f"https://{self.bucket_name}.oss-cn-hangzhou.aliyuncs.com/{object_key}"
        
        return {
            'file_hash': file_hash,
            'object_key': object_key,
            'url': url
        }
    
    def download_file(self, object_key: str) -> bytes:
        """
        从OSS下载文件
        """
        result = self.bucket.get_object(object_key)
        return result.read()
    
    def delete_file(self, object_key: str) -> bool:
        """
        删除OSS文件
        """
        try:
            self.bucket.delete_object(object_key)
            return True
        except Exception:
            return False
    
    def file_exists(self, object_key: str) -> bool:
        """
        检查文件是否存在
        """
        return self.bucket.object_exists(object_key)
    
    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """
        获取文件签名URL
        """
        return self.bucket.sign_url('GET', object_key, expires)
    
    def upload_resume(self, file_content: bytes, file_name: str) -> Dict:
        """
        上传简历文件
        """
        return self.upload_file(file_content, file_name, folder="resumes")
    
    def download_resume(self, file_hash: str) -> bytes:
        """
        下载简历文件
        """
        object_key = f"resumes/{file_hash}.pdf"
        return self.download_file(object_key)
    
    def get_resume_url(self, file_hash: str, expires: int = 3600) -> str:
        """
        获取简历文件签名URL
        """
        object_key = f"resumes/{file_hash}.pdf"
        return self.get_file_url(object_key, expires)


storage = None

def get_storage() -> Storage:
    """
    获取存储客户端单例
    """
    global storage
    if storage is None:
        storage = Storage()
    return storage
