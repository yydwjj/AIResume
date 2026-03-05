import json
import sys
import os
from datetime import datetime
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.functions.resume_upload import handler as resume_upload_handler
from backend.functions.resume_parse import handler as resume_parse_handler
from backend.functions.job_parse import handler as job_parse_handler
from backend.functions.match import handler as match_handler
from backend.functions.batch_match import handler as batch_match_handler
from backend.functions.task_status import handler as task_status_handler
from backend.config.settings import config

app = Flask(__name__)
CORS(app)

config.load()


def _update_job_list(cache, job_hash: str, result: Dict) -> None:
    """
    更新岗位列表
    """
    job_list = cache.get_job_list() or {'jobs': []}
    
    job_title = result.get('job_title', '未知')
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    job_item = {
        'hash': job_hash,
        'title': f"{job_title}_{timestamp}",
        'parse_time': ''
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


def _update_resume_list(cache, file_hash: str, result: dict) -> None:
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


def _convert_to_fc_event(request, path):
    """
    将Flask请求转换为阿里云函数计算事件格式
    """
    headers = dict(request.headers)
    body = None
    
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.is_json:
            body = request.get_json()
        else:
            body = request.get_data(as_text=True)
    
    event = {
        'httpMethod': request.method,
        'path': '/' + path,
        'headers': headers,
        'queryStringParameters': dict(request.args),
        'pathParameters': {},
        'body': json.dumps(body) if body else None
    }
    
    return event


@app.route('/api/resume/upload', methods=['POST', 'OPTIONS'])
def upload_resume():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    config.load()
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': '请上传PDF文件'
            }), 400
        
        from backend.utils.storage import get_storage
        from backend.utils.task_manager import get_task_manager
        from backend.utils.helpers import generate_file_hash
        from backend.utils.cache import get_cache
        from backend.functions.resume_parse import handler as resume_parse_handler
        
        file_content = file.read()
        file_hash = generate_file_hash(file_content)
        
        cache = get_cache()
        cached_result = cache.get_resume_parse(file_hash)
        
        if cached_result:
            _update_resume_list(cache, file_hash, cached_result)
            return jsonify({
                'success': True,
                'task_id': None,
                'file_hash': file_hash,
                'data': cached_result,
                'cached': True,
                'message': '简历解析完成（使用缓存）'
            })
        
        storage = get_storage()
        upload_result = storage.upload_resume(file_content, file.filename)
        
        task_manager = get_task_manager()
        task_id = task_manager.create_task('resume_parse', {
            'file_hash': upload_result['file_hash'],
            'object_key': upload_result['object_key']
        })
        
        task_manager.start_task(task_id, '正在解析PDF')
        
        parse_event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'task_id': task_id,
                'file_hash': upload_result['file_hash'],
                'object_key': upload_result['object_key']
            })
        }
        
        import threading
        def parse_resume_async():
            try:
                resume_parse_handler(parse_event, None)
            except Exception as e:
                task_manager.fail_task(task_id, str(e))
        
        thread = threading.Thread(target=parse_resume_async)
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'file_hash': upload_result['file_hash'],
            'message': '简历上传成功，正在解析中'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }), 500


@app.route('/api/resume/parse', methods=['POST', 'OPTIONS'])
def parse_resume():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    event = _convert_to_fc_event(request, 'api/resume/parse')
    result = resume_parse_handler(event, None)
    
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/job/parse', methods=['POST', 'OPTIONS'])
def parse_job():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    config.load()
    
    try:
        from backend.utils.llm_client import get_llm_client
        from backend.utils.cache import get_cache
        from backend.utils.helpers import generate_text_hash
        from backend.core.job_parser import get_job_parser
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        if not job_description:
            return jsonify({
                'success': False,
                'error': '缺少岗位描述'
            }), 400
        
        job_hash = generate_text_hash(job_description)
        
        cache = get_cache()
        cached_result = cache.get_job_parse(job_hash)
        
        if cached_result:
            return jsonify({
                'success': True,
                'data': cached_result
            })
        
        job_parser = get_job_parser()
        result = job_parser.parse(job_description)
        
        cache.set_job_parse(job_hash, result)
        
        _update_job_list(cache, job_hash, result)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'解析失败: {str(e)}'
        }), 500


@app.route('/api/match', methods=['POST', 'OPTIONS'])
def match():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    config.load()
    
    try:
        from backend.utils.cache import get_cache
        from backend.utils.task_manager import get_task_manager
        from backend.core.dual_matcher import get_dual_matcher
        
        data = request.get_json()
        resume_hash = data.get('resume_hash')
        job_hash = data.get('job_hash')
        mode = data.get('mode', 'standard')
        
        if not resume_hash or not job_hash:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        cache = get_cache()
        
        cached_result = cache.get_match_result(resume_hash, job_hash, mode)
        if cached_result:
            return jsonify({
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
        
        import threading
        def match_async():
            try:
                task_manager.start_task(task_id, '正在加载简历数据')
                
                resume_data = cache.get_resume_parse(resume_hash)
                if not resume_data:
                    task_manager.fail_task(task_id, '简历数据不存在')
                    return
                
                task_manager.progress_task(task_id, 30, '正在加载岗位数据')
                
                job_data = cache.get_job_parse(job_hash)
                if not job_data:
                    task_manager.fail_task(task_id, '岗位数据不存在')
                    return
                
                resume_data['resume_hash'] = resume_hash
                job_data['job_hash'] = job_hash
                
                task_manager.progress_task(task_id, 50, '正在进行规则匹配')
                
                dual_matcher = get_dual_matcher()
                result = dual_matcher.match(resume_data, job_data, mode)
                
                task_manager.progress_task(task_id, 90, '正在保存结果')
                
                result['resume_hash'] = resume_hash
                result['job_hash'] = job_hash
                
                cache.set_match_result(resume_hash, job_hash, result, mode)
                
                task_manager.complete_task(task_id, result)
            except Exception as e:
                task_manager.fail_task(task_id, str(e))
        
        thread = threading.Thread(target=match_async)
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'匹配失败: {str(e)}'
        }), 500


@app.route('/api/batch-match', methods=['POST', 'OPTIONS'])
def batch_match():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    config.load()
    
    try:
        from backend.utils.cache import get_cache
        from backend.utils.task_manager import get_task_manager
        from backend.core.dual_matcher import get_dual_matcher
        
        data = request.get_json()
        resume_hashes = data.get('resume_hashes', [])
        job_hashes = data.get('job_hashes', [])
        mode = data.get('mode', 'quick')
        
        if not resume_hashes or not job_hashes:
            return jsonify({
                'success': False,
                'error': '缺少简历或岗位参数'
            }), 400
        
        task_manager = get_task_manager()
        task_id = task_manager.create_task('batch_match', {
            'resume_hashes': resume_hashes,
            'job_hashes': job_hashes,
            'mode': mode
        })
        
        import threading
        def batch_match_async():
            try:
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
                        cache.set_match_result(resume_hash, job_hash, result, mode)
                
                task_manager.complete_task(task_id, {
                    'total': len(results),
                    'results': results
                })
            except Exception as e:
                task_manager.fail_task(task_id, str(e))
        
        thread = threading.Thread(target=batch_match_async)
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量匹配失败: {str(e)}'
        }), 500


@app.route('/api/task/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    config.load()
    
    event = {
        'httpMethod': 'GET',
        'path': '/api/task/status/' + task_id,
        'headers': dict(request.headers),
        'queryStringParameters': dict(request.args),
        'pathParameters': {'task_id': task_id},
        'body': None
    }
    
    result = task_status_handler(event, None)
    
    return jsonify(json.loads(result['body'])), result['statusCode']


@app.route('/api/resume/list', methods=['GET'])
def get_resume_list():
    from backend.utils.cache import get_cache
    
    config.load()
    
    cache = get_cache()
    resume_list = cache.get_resume_list()
    
    if not resume_list:
        return jsonify({
            'success': False,
            'error': '暂无简历数据'
        }), 404
    
    return jsonify({
        'success': True,
        'data': resume_list
    })


@app.route('/api/job/list', methods=['GET'])
def get_job_list():
    from backend.utils.cache import get_cache
    
    config.load()
    
    cache = get_cache()
    job_list = cache.get_job_list()
    
    if not job_list:
        return jsonify({
            'success': False,
            'error': '暂无岗位数据'
        }), 404
    
    return jsonify({
        'success': True,
        'data': job_list
    })


@app.route('/api/resume/<hash>', methods=['GET'])
def get_resume(hash):
    from backend.utils.cache import get_cache
    
    config.load()
    
    cache = get_cache()
    resume_data = cache.get_resume_parse(hash)
    
    if not resume_data:
        return jsonify({
            'success': False,
            'error': '简历不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': resume_data
    })


@app.route('/api/job/<hash>', methods=['GET'])
def get_job(hash):
    from backend.utils.cache import get_cache
    
    config.load()
    
    cache = get_cache()
    job_data = cache.get_job_parse(hash)
    
    if not job_data:
        return jsonify({
            'success': False,
            'error': '岗位不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': job_data
    })


@app.route('/', methods=['GET'])
def health():
    from backend.utils.cache import get_cache
    
    config.load()
    
    cache = get_cache()
    
    resume_list = cache.get_resume_list() or {'resumes': []}
    job_list = cache.get_job_list() or {'jobs': []}
    
    return jsonify({
        'success': True,
        'data': {
            'resumes': resume_list.get('resumes', []),
            'jobs': job_list.get('jobs', [])
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
