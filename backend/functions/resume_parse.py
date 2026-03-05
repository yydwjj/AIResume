import json
from typing import Dict, Any

from ..config.settings import config
from ..utils.storage import get_storage
from ..utils.cache import get_cache
from ..utils.task_manager import get_task_manager
from ..core.pdf_parser import get_pdf_parser
from ..core.text_cleaner import get_text_cleaner
from ..core.info_extractor import get_info_extractor


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    简历解析函数入口（异步处理）
    """
    try:
        config.load()
        
        body = _parse_event_body(event)
        task_id = body.get('task_id')
        file_hash = body.get('file_hash')
        object_key = body.get('object_key')
        
        if not task_id or not file_hash:
            return _response(400, {
                'success': False,
                'error': '缺少必要参数'
            })
        
        cache = get_cache()
        cached_result = cache.get_resume_parse(file_hash)
        if cached_result:
            _update_resume_list(cache, file_hash, cached_result)
            return _response(200, {
                'success': True,
                'data': cached_result,
                'cached': True
            })
        
        task_manager = get_task_manager()
        task_manager.start_task(task_id, '正在解析PDF')
        
        storage = get_storage()
        file_content = storage.download_file(object_key)
        
        task_manager.progress_task(task_id, 30, '正在提取文本')
        
        pdf_parser = get_pdf_parser()
        raw_text, metadata = pdf_parser.parse(file_content)
        
        task_manager.progress_task(task_id, 50, '正在清洗文本')
        
        text_cleaner = get_text_cleaner()
        cleaned_result = text_cleaner.clean_and_structure(raw_text)
        
        task_manager.progress_task(task_id, 70, '正在提取关键信息')
        
        info_extractor = get_info_extractor()
        extracted_info = info_extractor.extract(cleaned_result['cleaned_text'])
        
        task_manager.progress_task(task_id, 90, '正在保存结果')
        
        result = {
            'resume_hash': file_hash,
            'metadata': metadata,
            'raw_text': cleaned_result['raw_text'],
            'cleaned_text': cleaned_result['cleaned_text'],
            'structured_text': cleaned_result['structured_text'],
            'basic_info': extracted_info.get('basic_info', {}),
            'job_info': extracted_info.get('job_info', {}),
            'background_info': extracted_info.get('background_info', {}),
            'skills': extracted_info.get('skills', []),
            'skill_summary': extracted_info.get('skill_summary', {})
        }
        
        cache = get_cache()
        cache.set_resume_parse(file_hash, result)
        
        _update_resume_list(cache, file_hash, result)
        
        task_manager.complete_task(task_id, result)
        
        return _response(200, {
            'success': True,
            'task_id': task_id
        })
        
    except Exception as e:
        if task_id:
            task_manager = get_task_manager()
            task_manager.fail_task(task_id, str(e))
        
        return _response(500, {
            'success': False,
            'error': f'解析失败: {str(e)}'
        })


def _parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get('body', '{}')
    if isinstance(body, str):
        return json.loads(body)
    return body


def _update_resume_list(cache, file_hash: str, result: Dict) -> None:
    """
    更新简历列表
    """
    resume_list = cache.get_resume_list() or {'resumes': []}
    
    resume_item = {
        'hash': file_hash,
        'name': result.get('basic_info', {}).get('name', '未知'),
        'parse_time': result.get('metadata', {}).get('parse_time', '')
    }
    
    existing_index = None
    for i, item in enumerate(resume_list['resumes']):
        if item.get('hash') == file_hash:
            existing_index = i
            break
    
    if existing_index is not None:
        resume_list['resumes'][existing_index] = resume_item
    else:
        resume_list['resumes'].append(resume_item)
    
    cache.set_resume_list(resume_list)


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
