import uuid
from datetime import datetime
from typing import Dict, Optional

from ..utils.cache import get_cache


class TaskManager:
    def __init__(self):
        self.cache = get_cache()
        self.task_ttl = 7200
    
    def create_task(self, task_type: str, params: Dict) -> str:
        """
        创建任务
        """
        task_id = f"{task_type}_{uuid.uuid4().hex[:12]}"
        
        task_data = {
            'task_id': task_id,
            'type': task_type,
            'status': 'pending',
            'progress': 0,
            'stage': '初始化',
            'params': params,
            'result': None,
            'error': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.cache.set_task(task_id, task_data, self.task_ttl)
        return task_id
    
    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        stage: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        更新任务状态
        """
        task_data = self.cache.get_task(task_id)
        if not task_data:
            return False
        
        if status:
            task_data['status'] = status
        if progress is not None:
            task_data['progress'] = progress
        if stage:
            task_data['stage'] = stage
        if result:
            task_data['result'] = result
        if error:
            task_data['error'] = error
        
        task_data['updated_at'] = datetime.now().isoformat()
        
        self.cache.set_task(task_id, task_data, self.task_ttl)
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        获取任务状态
        """
        return self.cache.get_task(task_id)
    
    def start_task(self, task_id: str, stage: str = "处理中") -> bool:
        """
        开始任务
        """
        return self.update_task(
            task_id,
            status='processing',
            progress=10,
            stage=stage
        )
    
    def progress_task(self, task_id: str, progress: int, stage: str) -> bool:
        """
        更新任务进度
        """
        return self.update_task(
            task_id,
            progress=progress,
            stage=stage
        )
    
    def complete_task(self, task_id: str, result: Dict) -> bool:
        """
        完成任务
        """
        task_data = self.cache.get_task(task_id)
        if not task_data:
            return False
        
        task_data['status'] = 'completed'
        task_data['progress'] = 100
        task_data['stage'] = '完成'
        task_data['result'] = result
        task_data['updated_at'] = datetime.now().isoformat()
        
        self.cache.set_task(task_id, task_data, 86400)
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """
        任务失败
        """
        return self.update_task(
            task_id,
            status='failed',
            stage='失败',
            error=error
        )


task_manager = None

def get_task_manager() -> TaskManager:
    global task_manager
    if task_manager is None:
        task_manager = TaskManager()
    return task_manager
