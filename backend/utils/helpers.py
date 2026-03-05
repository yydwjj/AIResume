import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class PDFTypeError(Exception):
    """PDF类型错误异常"""
    pass


class ParseError(Exception):
    """解析错误异常"""
    pass


class LLMError(Exception):
    """LLM调用错误异常"""
    pass


class CacheError(Exception):
    """缓存错误异常"""
    pass


def generate_file_hash(file_content: bytes) -> str:
    """
    生成文件内容的MD5哈希值
    """
    return hashlib.md5(file_content).hexdigest()


def generate_text_hash(text: str) -> str:
    """
    生成文本的MD5哈希值
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def generate_job_hash(job_description: str) -> str:
    """
    生成岗位描述的MD5哈希值
    """
    return generate_text_hash(job_description)


def clean_phone(phone: str) -> Optional[str]:
    """
    清洗电话号码，返回标准格式
    """
    if not phone:
        return None
    
    cleaned = re.sub(r'[^\d]', '', phone)
    
    if len(cleaned) == 11 and cleaned.startswith('1'):
        return cleaned
    elif len(cleaned) > 11:
        return cleaned[-11:] if cleaned[-11:].startswith('1') else None
    
    return None


def clean_email(email: str) -> Optional[str]:
    """
    清洗邮箱地址，返回标准格式
    """
    if not email:
        return None
    
    email = email.strip().lower()
    
    pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    if re.match(pattern, email):
        return email
    
    return None


def extract_years_from_text(text: str) -> Optional[int]:
    """
    从文本中提取工作年限
    """
    if not text:
        return None
    
    patterns = [
        r'(\d+)\s*年',
        r'(\d+)\s*years?',
        r'工作年限[：:]\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None


def parse_salary_range(salary_text: str) -> Optional[Dict]:
    """
    解析薪资范围
    """
    if not salary_text:
        return None
    
    patterns = [
        r'(\d+)[kK]?\s*[-~至]\s*(\d+)[kK]?',
        r'(\d+)[kK]',
        r'(\d+)-(\d+)万',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, salary_text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                return {
                    'min': int(match.group(1)),
                    'max': int(match.group(2)),
                    'unit': 'K'
                }
            else:
                value = int(match.group(1))
                return {
                    'min': value,
                    'max': value,
                    'unit': 'K'
                }
    
    return None


def normalize_date(date_str: str) -> Optional[str]:
    """
    标准化日期格式
    """
    if not date_str:
        return None
    
    patterns = [
        (r'(\d{4})[年/-](\d{1,2})[月/-]?', r'\1-\2'),
        (r'(\d{4})\.(\d{1,2})\.?', r'\1-\2'),
        (r'(\d{1,2})/(\d{4})', r'\2-\1'),
    ]
    
    for pattern, replacement in patterns:
        match = re.search(pattern, date_str)
        if match:
            result = re.sub(pattern, replacement, date_str)
            parts = result.split('-')
            if len(parts) == 2:
                year, month = parts
                return f"{year}-{month.zfill(2)}"
    
    return None


def calculate_experience_match(resume_years: int, job_min_years: int, job_max_years: Optional[int] = None) -> Dict:
    """
    计算工作经验匹配度
    """
    if resume_years is None:
        resume_years = 0
    
    if job_min_years is None:
        job_min_years = 0
    
    if job_min_years == 0:
        return {
            'match': True,
            'score': 1.0,
            'reason': '无工作年限要求'
        }
    
    if resume_years >= job_min_years:
        if job_max_years and resume_years > job_max_years:
            return {
                'match': True,
                'score': 0.8,
                'reason': f'工作年限{resume_years}年超过要求{job_min_years}-{job_max_years}年'
            }
        else:
            return {
                'match': True,
                'score': 1.0,
                'reason': f'工作年限{resume_years}年符合要求{job_min_years}年及以上'
            }
    else:
        gap = job_min_years - resume_years
        score = max(0, 1 - gap * 0.2)
        return {
            'match': False,
            'score': score,
            'reason': f'工作年限{resume_years}年不足要求{job_min_years}年，差{gap}年'
        }


def calculate_education_match(resume_education: str, required_education: str) -> Dict:
    """
    计算学历匹配度
    """
    education_levels = {
        '博士': 5,
        '硕士': 4,
        '研究生': 4,
        '本科': 3,
        '大专': 2,
        '专科': 2,
        '高中': 1,
        '中专': 1,
    }
    
    if not required_education:
        return {
            'match': True,
            'score': 1.0,
            'reason': '无学历要求'
        }
    
    resume_level = 0
    for key, level in education_levels.items():
        if key in resume_education:
            resume_level = max(resume_level, level)
    
    required_level = 0
    for key, level in education_levels.items():
        if key in required_education:
            required_level = max(required_level, level)
    
    if resume_level >= required_level:
        return {
            'match': True,
            'score': 1.0,
            'reason': f'学历{resume_education}符合要求{required_education}'
        }
    else:
        return {
            'match': False,
            'score': 0.0,
            'reason': f'学历{resume_education}不足要求{required_education}'
        }


def get_current_timestamp() -> str:
    """
    获取当前时间戳
    """
    return datetime.now().isoformat()


def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    安全的JSON解析
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 4000) -> str:
    """
    截断文本到指定长度
    """
    if not text:
        return ""
    return text[:max_length] if len(text) > max_length else text
