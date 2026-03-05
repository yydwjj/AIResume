import json
from typing import Dict, List, Optional

from ..utils.llm_client import get_llm_client
from ..utils.helpers import clean_phone, clean_email, truncate_text
from ..data.skill_database import get_skill_db
from ..data.skill_learner import get_skill_learner
from ..config.prompts import RESUME_EXTRACTION_PROMPT


class InfoExtractor:
    def __init__(self):
        self.llm_client = get_llm_client()
        self.skill_db = get_skill_db()
        self.skill_learner = get_skill_learner()
    
    def extract(self, resume_text: str) -> Dict:
        """
        提取简历关键信息
        """
        truncated_text = truncate_text(resume_text, 4000)
        prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=truncated_text)
        
        response = self.llm_client.chat(prompt)
        
        result = self._parse_response(response)
        
        result = self._validate_and_clean(result)
        
        result = self._normalize_skills(result)
        
        return result
    
    def _parse_response(self, response: str) -> Dict:
        """
        解析LLM响应
        """
        try:
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0]
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {
                'basic_info': {},
                'job_info': {},
                'background_info': {},
                'skills': []
            }
    
    def _validate_and_clean(self, data: Dict) -> Dict:
        """
        验证和清洗提取的信息
        """
        basic_info = data.get('basic_info', {})
        if basic_info:
            if basic_info.get('phone'):
                basic_info['phone'] = clean_phone(basic_info['phone'])
            if basic_info.get('email'):
                basic_info['email'] = clean_email(basic_info['email'])
        
        background_info = data.get('background_info', {})
        if background_info:
            if not isinstance(background_info.get('education'), list):
                background_info['education'] = []
            if not isinstance(background_info.get('work_experience'), list):
                background_info['work_experience'] = []
            if not isinstance(background_info.get('projects'), list):
                background_info['projects'] = []
        
        if not isinstance(data.get('skills'), list):
            data['skills'] = []
        
        return data
    
    def _normalize_skills(self, data: Dict) -> Dict:
        """
        标准化技能
        """
        skills = data.get('skills', [])
        
        normalized_skills = []
        skill_names = set()
        
        for skill in skills:
            original_name = skill.get('name')
            if not original_name:
                continue
            
            normalized = self.skill_db.normalize(original_name)
            
            if normalized == original_name.strip().title():
                normalized = self.skill_learner.learn_skill(original_name)
            
            if normalized not in skill_names:
                skill_names.add(normalized)
                skill['name'] = normalized
                normalized_skills.append(skill)
        
        expanded = self.skill_db.expand_skills(list(skill_names))
        
        for expanded_skill in expanded:
            if expanded_skill not in skill_names:
                normalized_skills.append({
                    'name': expanded_skill,
                    'category': '推断',
                    'proficiency': '推断',
                    'usage_years': None,
                    'source': '技能扩展'
                })
                skill_names.add(expanded_skill)
        
        data['skills'] = normalized_skills
        data['skill_summary'] = {
            'normalized': list(skill_names),
            'expanded': list(expanded)
        }
        
        return data
    
    def extract_basic_info(self, resume_text: str) -> Dict:
        """
        仅提取基本信息
        """
        result = self.extract(resume_text)
        return result.get('basic_info', {})
    
    def extract_skills(self, resume_text: str) -> List[Dict]:
        """
        仅提取技能信息
        """
        result = self.extract(resume_text)
        return result.get('skills', [])


info_extractor = None

def get_info_extractor() -> InfoExtractor:
    global info_extractor
    if info_extractor is None:
        info_extractor = InfoExtractor()
    return info_extractor
