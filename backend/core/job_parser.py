import json
from typing import Dict, List, Optional

from ..utils.llm_client import get_llm_client
from ..utils.helpers import generate_text_hash, truncate_text
from ..data.skill_database import get_skill_db
from ..data.skill_learner import get_skill_learner
from ..config.prompts import JOB_PARSE_PROMPT


class JobParser:
    def __init__(self):
        self.llm_client = get_llm_client()
        self.skill_db = get_skill_db()
        self.skill_learner = get_skill_learner()
    
    def parse(self, job_description: str) -> Dict:
        """
        解析岗位需求描述
        """
        truncated_text = truncate_text(job_description, 3000)
        prompt = JOB_PARSE_PROMPT.format(job_description=truncated_text)
        
        response = self.llm_client.chat(prompt)
        
        result = self._parse_response(response)
        
        result = self._validate_and_clean(result)
        
        result = self._normalize_skills(result)
        
        job_hash = generate_text_hash(job_description)
        result['job_hash'] = job_hash
        result['original_description'] = job_description
        
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
                'job_title': '',
                'required_skills': [],
                'experience_years': {},
                'education_level': {},
                'responsibilities': [],
                'keywords': []
            }
    
    def _validate_and_clean(self, data: Dict) -> Dict:
        """
        验证和清洗提取的信息
        """
        if not isinstance(data.get('required_skills'), list):
            data['required_skills'] = []
        
        if not isinstance(data.get('responsibilities'), list):
            data['responsibilities'] = []
        
        if not isinstance(data.get('keywords'), list):
            data['keywords'] = []
        
        experience_years = data.get('experience_years', {})
        if not isinstance(experience_years, dict):
            data['experience_years'] = {}
        else:
            if experience_years.get('min') is not None:
                try:
                    experience_years['min'] = int(experience_years['min'])
                except (ValueError, TypeError):
                    experience_years['min'] = 0
            if experience_years.get('max') is not None:
                try:
                    experience_years['max'] = int(experience_years['max'])
                except (ValueError, TypeError):
                    experience_years['max'] = None
        
        return data
    
    def _normalize_skills(self, data: Dict) -> Dict:
        """
        标准化技能
        """
        required_skills = data.get('required_skills', [])
        
        normalized_skills = []
        skill_names = set()
        
        for skill in required_skills:
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
        
        data['required_skills'] = normalized_skills
        
        expanded = self.skill_db.expand_skills(list(skill_names))
        
        data['skill_summary'] = {
            'normalized': list(skill_names),
            'expanded': list(expanded)
        }
        
        return data
    
    def get_required_skill_names(self, job_data: Dict) -> List[str]:
        """
        获取必须技能名称列表
        """
        required_skills = job_data.get('required_skills', [])
        return [
            skill.get('name') 
            for skill in required_skills 
            if skill.get('importance') == '必须' and skill.get('name')
        ]
    
    def get_preferred_skill_names(self, job_data: Dict) -> List[str]:
        """
        获取加分技能名称列表
        """
        required_skills = job_data.get('required_skills', [])
        return [
            skill.get('name') 
            for skill in required_skills 
            if skill.get('importance') == '加分' and skill.get('name')
        ]


job_parser = None

def get_job_parser() -> JobParser:
    global job_parser
    if job_parser is None:
        job_parser = JobParser()
    return job_parser
