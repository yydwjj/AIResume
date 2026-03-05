import json
from typing import Dict, Any

from ..config.settings import config
from ..utils.cache import get_cache
from ..utils.helpers import generate_text_hash
from ..core.job_parser import get_job_parser


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    岗位解析函数入口
    """
    try:
        config.load()
        
        if event.get('httpMethod') == 'OPTIONS':
            return _cors_response(200, {})
        
        body = _parse_event_body(event)
        job_description = body.get('job_description', '')
        
        if not job_description:
            return _cors_response(400, {
                'success': False,
                'error': '岗位描述不能为空'
            })
        
        job_hash = generate_text_hash(job_description)
        
        cache = get_cache()
        cached_result = cache.get_job_parse(job_hash)
        if cached_result:
            return _cors_response(200, {
                'success': True,
                'data': cached_result,
                'cached': True
            })
        
        job_parser = get_job_parser()
        result = job_parser.parse(job_description)
        
        cache.set_job_parse(job_hash, result)
        
        _update_job_list(cache, job_hash, result)
        
        return _cors_response(200, {
            'success': True,
            'data': result,
            'cached': False
        })
        
    except Exception as e:
        return _cors_response(500, {
            'success': False,
            'error': f'解析失败: {str(e)}'
        })


def _parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get('body', '{}')
    if isinstance(body, str):
        return json.loads(body)
    return body


def _update_job_list(cache, job_hash: str, result: Dict) -> None:
    """
    更新岗位列表
    """
    job_list = cache.get_job_list() or {'jobs': []}
    
    job_item = {
        'hash': job_hash,
        'title': result.get('job_title', '未知岗位'),
    }
    
    existing_index = None
    for i, item in enumerate(job_list['jobs']):
        if item.get('hash') == job_hash:
            existing_index = i
            break
    
    if existing_index is not None:
        job_list['jobs'][existing_index] = job_item
    else:
        job_list['jobs'].append(job_item)
    
    cache.set_job_list(job_list)


def _cors_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
