import json
from typing import Dict, Any

from ..config.settings import config
from ..utils.cache import get_cache
from ..utils.task_manager import get_task_manager
from ..core.dual_matcher import get_dual_matcher


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    匹配评分函数入口（异步处理）
    """
    try:
        config.load()
        
        body = _parse_event_body(event)
        resume_hash = body.get('resume_hash')
        job_hash = body.get('job_hash')
        mode = body.get('mode', 'standard')
        
        if not resume_hash or not job_hash:
            return _response(400, {
                'success': False,
                'error': '缺少必要参数'
            })
        
        cache = get_cache()
        
        cached_result = cache.get_match_result(resume_hash, job_hash)
        if cached_result:
            return _response(200, {
                'success': True,
                'data': cached_result,
                'cached': True
            })
        
        task_manager = get_task_manager()
        task_id = task_manager.create_task('match', {
            'resume_hash': resume_hash,
            'job_hash': job_hash,
            'mode': mode
        })
        
        task_manager.start_task(task_id, '正在加载简历数据')
        
        resume_data = cache.get_resume_parse(resume_hash)
        if not resume_data:
            task_manager.fail_task(task_id, '简历数据不存在')
            return _response(404, {
                'success': False,
                'error': '简历数据不存在'
            })
        
        task_manager.progress_task(task_id, 30, '正在加载岗位数据')
        
        job_data = cache.get_job_parse(job_hash)
        if not job_data:
            task_manager.fail_task(task_id, '岗位数据不存在')
            return _response(404, {
                'success': False,
                'error': '岗位数据不存在'
            })
        
        resume_data['resume_hash'] = resume_hash
        job_data['job_hash'] = job_hash
        
        task_manager.progress_task(task_id, 50, '正在进行规则匹配')
        
        dual_matcher = get_dual_matcher()
        result = dual_matcher.match(resume_data, job_data, mode)
        
        task_manager.progress_task(task_id, 90, '正在保存结果')
        
        result['resume_hash'] = resume_hash
        result['job_hash'] = job_hash
        
        cache.set_match_result(resume_hash, job_hash, result)
        
        task_manager.complete_task(task_id, result)
        
        return _response(200, {
            'success': True,
            'task_id': task_id
        })
        
    except Exception as e:
        if 'task_id' in dir():
            task_manager = get_task_manager()
            task_manager.fail_task(task_id, str(e))
        
        return _response(500, {
            'success': False,
            'error': f'匹配失败: {str(e)}'
        })


def _parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get('body', '{}')
    if isinstance(body, str):
        return json.loads(body)
    return body


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
