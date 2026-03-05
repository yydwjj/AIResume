import os
from typing import Dict, Optional

from ..config.settings import config
from .helpers import generate_file_hash


class LocalStorage:
    def __init__(self):
        self.storage_dir = 'local_storage'
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, 'resumes'), exist_ok=True)
    
    def upload_file(
        self, 
        file_content: bytes, 
        file_name: str,
        folder: str = "resumes"
    ) -> Dict:
        """
        上传文件到本地存储
        
        Returns:
            {
                'file_hash': '文件哈希',
                'object_key': '本地文件路径',
                'url': '文件URL'
            }
        """
        file_hash = generate_file_hash(file_content)
        extension = os.path.splitext(file_name)[1] or '.pdf'
        
        folder_path = os.path.join(self.storage_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, f"{file_hash}{extension}")
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        object_key = f"{folder}/{file_hash}{extension}"
        url = f"file://{os.path.abspath(file_path)}"
        
        return {
            'file_hash': file_hash,
            'object_key': object_key,
            'url': url
        }
    
    def download_file(self, object_key: str) -> bytes:
        """
        从本地存储下载文件
        """
        file_path = os.path.join(self.storage_dir, object_key)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {object_key}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def delete_file(self, object_key: str) -> bool:
        """
        删除本地文件
        """
        try:
            file_path = os.path.join(self.storage_dir, object_key)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False
    
    def file_exists(self, object_key: str) -> bool:
        """
        检查文件是否存在
        """
        file_path = os.path.join(self.storage_dir, object_key)
        return os.path.exists(file_path)
    
    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """
        获取文件URL
        """
        file_path = os.path.join(self.storage_dir, object_key)
        return f"file://{os.path.abspath(file_path)}"
    
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
        获取简历文件URL
        """
        object_key = f"resumes/{file_hash}.pdf"
        return self.get_file_url(object_key, expires)


local_storage = None

def get_local_storage() -> LocalStorage:
    """
    获取本地存储客户端单例
    """
    global local_storage
    if local_storage is None:
        local_storage = LocalStorage()
    return local_storage
