import json
from typing import Dict, Any, List

from ..config.settings import config
from ..utils.cache import get_cache
from ..utils.task_manager import get_task_manager
from ..core.dual_matcher import get_dual_matcher


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    批量匹配函数入口（异步处理）
    """
    try:
        config.load()
        
        body = _parse_event_body(event)
        resume_hashes = body.get('resume_hashes', [])
        job_hashes = body.get('job_hashes', [])
        mode = body.get('mode', 'quick')
        
        if not resume_hashes or not job_hashes:
            return _response(400, {
                'success': False,
                'error': '缺少简历或岗位参数'
            })
        
        task_manager = get_task_manager()
        task_id = task_manager.create_task('batch_match', {
            'resume_hashes': resume_hashes,
            'job_hashes': job_hashes,
            'mode': mode
        })
        
        task_manager.start_task(task_id, '正在加载数据')
        
        cache = get_cache()
        
        resume_data_list = []
        for i, resume_hash in enumerate(resume_hashes):
            resume_data = cache.get_resume_parse(resume_hash)
            if resume_data:
                resume_data['resume_hash'] = resume_hash
                resume_data_list.append(resume_data)
        
        job_data_list = []
        for job_hash in job_hashes:
            job_data = cache.get_job_parse(job_hash)
            if job_data:
                job_data['job_hash'] = job_hash
                job_data_list.append(job_data)
        
        task_manager.progress_task(task_id, 30, '正在进行批量匹配')
        
        dual_matcher = get_dual_matcher()
        results = dual_matcher.batch_match(resume_data_list, job_data_list, mode)
        
        task_manager.progress_task(task_id, 90, '正在保存结果')
        
        for result in results:
            resume_hash = result.get('resume_hash')
            job_hash = result.get('job_hash')
            if resume_hash and job_hash:
                cache.set_match_result(resume_hash, job_hash, result)
        
        task_manager.complete_task(task_id, {
            'total': len(results),
            'results': results
        })
        
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
            'error': f'批量匹配失败: {str(e)}'
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
