import json
import base64
from typing import Dict, Any

from ..config.settings import config
from ..utils.storage import get_storage
from ..utils.task_manager import get_task_manager
from ..utils.helpers import generate_file_hash, PDFTypeError


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    简历上传函数入口
    
    Args:
        event: 函数计算事件
        context: 函数计算上下文
        
    Returns:
        {
            "statusCode": 200,
            "headers": {...},
            "body": json字符串
        }
    """
    try:
        config.load()
        
        if event.get('httpMethod') == 'OPTIONS':
            return _cors_response(200, {})
        
        body = _parse_event_body(event)
        
        file_content = _extract_file_content(body)
        
        storage = get_storage()
        upload_result = storage.upload_resume(file_content, body.get('filename', 'resume.pdf'))
        
        task_manager = get_task_manager()
        task_id = task_manager.create_task('resume_parse', {
            'file_hash': upload_result['file_hash'],
            'object_key': upload_result['object_key']
        })
        
        return _cors_response(200, {
            'success': True,
            'task_id': task_id,
            'file_hash': upload_result['file_hash'],
            'message': '简历上传成功，正在解析中'
        })
        
    except PDFTypeError as e:
        return _cors_response(400, {
            'success': False,
            'error': str(e)
        })
    except Exception as e:
        return _cors_response(500, {
            'success': False,
            'error': f'上传失败: {str(e)}'
        })


def _parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析事件体
    """
    body = event.get('body', '')
    
    if event.get('isBase64Encoded'):
        body = base64.b64decode(body).decode('utf-8')
    
    if event.get('headers', {}).get('content-type', '').startswith('multipart/form-data'):
        return _parse_multipart(body, event.get('headers', {}))
    
    try:
        return json.loads(body) if body else {}
    except json.JSONDecodeError:
        return {}


def _parse_multipart(body: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    解析multipart/form-data
    """
    content_type = headers.get('content-type', '')
    boundary = None
    
    for part in content_type.split(';'):
        if 'boundary=' in part:
            boundary = part.split('=')[1].strip()
            break
    
    if not boundary:
        return {}
    
    result = {}
    parts = body.split(f'--{boundary}')
    
    for part in parts:
        if 'Content-Disposition' in part:
            lines = part.strip().split('\r\n')
            for line in lines:
                if 'filename=' in line:
                    filename_start = line.find('filename="') + 10
                    filename_end = line.find('"', filename_start)
                    result['filename'] = line[filename_start:filename_end]
                elif 'name="file"' in line:
                    content_start = part.find('\r\n\r\n')
                    if content_start != -1:
                        result['file_content'] = part[content_start + 4:].strip()
    
    return result


def _extract_file_content(body: Dict[str, Any]) -> bytes:
    """
    提取文件内容
    """
    if 'file_content' in body:
        return base64.b64decode(body['file_content'])
    
    if 'file' in body:
        return base64.b64decode(body['file'])
    
    raise PDFTypeError("未找到文件内容")


def _cors_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成CORS响应
    """
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
