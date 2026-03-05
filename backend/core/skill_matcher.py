from typing import Dict, List, Set

from ..utils.helpers import calculate_experience_match, calculate_education_match


class SkillMatcher:
    def __init__(self):
        pass
    
    def match(self, resume_data: Dict, job_data: Dict) -> Dict:
        """
        规则匹配
        """
        resume_skill_summary = resume_data.get('skill_summary', {}) or {}
        job_skill_summary = job_data.get('skill_summary', {}) or {}
        
        resume_skills = set(resume_skill_summary.get('expanded', []))
        job_skills = set(job_skill_summary.get('expanded', []))
        
        required_skills = self._get_required_skills(job_data) or []
        preferred_skills = self._get_preferred_skills(job_data) or []
        
        matched_required = [s for s in required_skills if s in resume_skills]
        matched_preferred = [s for s in preferred_skills if s in resume_skills]
        
        skill_match_rate = len(matched_required) / len(required_skills) if required_skills else 1.0
        
        resume_years = resume_data.get('background_info', {}).get('work_years', 0)
        job_experience = job_data.get('experience_years', {})
        experience_result = calculate_experience_match(
            resume_years,
            job_experience.get('min', 0),
            job_experience.get('max')
        )
        
        resume_education = self._get_highest_education(resume_data)
        required_education = job_data.get('education_level', {}).get('required', '')
        education_result = calculate_education_match(resume_education, required_education)
        
        base_score = (
            skill_match_rate * 50 +
            experience_result['score'] * 20 +
            education_result['score'] * 20 +
            (len(matched_preferred) / len(preferred_skills) if preferred_skills else 0) * 10
        )
        
        return {
            'match_score': round(base_score, 2),
            'skill_match_rate': round(skill_match_rate, 2),
            'experience_match': experience_result['match'],
            'education_match': education_result['match'],
            'matched_required_skills': matched_required,
            'matched_preferred_skills': matched_preferred,
            'missing_required_skills': [s for s in required_skills if s not in resume_skills],
            'details': {
                'experience': experience_result,
                'education': education_result
            }
        }
    
    def _get_required_skills(self, job_data: Dict) -> List[str]:
        """
        获取必须技能列表
        """
        required_skills = job_data.get('required_skills', []) or []
        return [
            skill.get('name')
            for skill in required_skills
            if skill.get('importance') == '必须' and skill.get('name')
        ]
    
    def _get_preferred_skills(self, job_data: Dict) -> List[str]:
        """
        获取加分技能列表
        """
        required_skills = job_data.get('required_skills', []) or []
        return [
            skill.get('name')
            for skill in required_skills
            if skill.get('importance') == '加分' and skill.get('name')
        ]
    
    def _get_highest_education(self, resume_data: Dict) -> str:
        """
        获取最高学历
        """
        education_list = resume_data.get('background_info', {}).get('education', [])
        if not education_list:
            return ''
        
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
        
        highest_level = 0
        highest_education = ''
        
        for edu in education_list:
            degree = edu.get('degree', '') or ''
            if not degree:
                continue
            for key, level in education_levels.items():
                if key in degree and level > highest_level:
                    highest_level = level
                    highest_education = degree
        
        return highest_education


skill_matcher = SkillMatcher()

def get_skill_matcher() -> SkillMatcher:
    return skill_matcher
