import json
from typing import Dict, Any

from ..config.settings import config
from ..utils.task_manager import get_task_manager


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    任务状态查询函数入口
    """
    try:
        config.load()
        
        if event.get('httpMethod') == 'OPTIONS':
            return _cors_response(200, {})
        
        path_parameters = event.get('pathParameters', {})
        task_id = path_parameters.get('task_id')
        
        if not task_id:
            query_parameters = event.get('queryStringParameters', {})
            task_id = query_parameters.get('task_id')
        
        if not task_id:
            path = event.get('path', '')
            if '/task/' in path:
                task_id = path.split('/task/')[-1].split('/')[0]
        
        if not task_id:
            return _cors_response(400, {
                'success': False,
                'error': '缺少task_id参数'
            })
        
        task_manager = get_task_manager()
        task_data = task_manager.get_task(task_id)
        
        if not task_data:
            return _cors_response(404, {
                'success': False,
                'error': '任务不存在'
            })
        
        return _cors_response(200, {
            'success': True,
            'data': task_data
        })
        
    except Exception as e:
        return _cors_response(500, {
            'success': False,
            'error': f'查询失败: {str(e)}'
        })


def _cors_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
