import json
from typing import Dict, List, Optional

from ..utils.llm_client import get_llm_client
from ..utils.helpers import truncate_text
from ..config.prompts import SEMANTIC_MATCH_PROMPT, PROJECT_RELEVANCE_PROMPT


class SemanticMatcher:
    def __init__(self):
        self.llm_client = get_llm_client()
    
    def analyze_comprehensive(self, resume_data: Dict, job_data: Dict) -> Dict:
        """
        综合语义匹配分析
        """
        name = resume_data.get('basic_info', {}).get('name', '')
        work_years = resume_data.get('background_info', {}).get('work_years', 0)
        education = self._get_highest_education(resume_data)
        skills = ', '.join(resume_data.get('skill_summary', {}).get('normalized', []))
        
        projects = resume_data.get('background_info', {}).get('projects', [])
        projects_text = self._format_projects(projects)
        
        job_title = job_data.get('job_title', '')
        responsibilities = '\n'.join([
            f'- {r}' for r in job_data.get('responsibilities', [])
        ])
        required_skills = ', '.join(job_data.get('skill_summary', {}).get('normalized', []))
        
        prompt = SEMANTIC_MATCH_PROMPT.format(
            name=name,
            work_years=work_years,
            education=education,
            skills=skills,
            projects=projects_text,
            job_title=job_title,
            responsibilities=responsibilities,
            required_skills=required_skills
        )
        
        response = self.llm_client.chat(prompt)
        
        result = self._parse_response(response)
        
        return result
    
    def analyze_detailed(self, resume_data: Dict, job_data: Dict) -> Dict:
        """
        细粒度语义匹配分析
        """
        results = {}
        
        projects = resume_data.get('background_info', {}).get('projects', [])
        if projects:
            results['project_analysis'] = self.analyze_project_relevance(
                resume_data, job_data
            )
        
        results['comprehensive_analysis'] = self.analyze_comprehensive(
            resume_data, job_data
        )
        
        scores = []
        weights = []
        
        if 'project_analysis' in results:
            scores.append(results['project_analysis']['overall_score'])
            weights.append(0.4)
        
        if 'comprehensive_analysis' in results:
            scores.append(results['comprehensive_analysis']['overall_score'])
            weights.append(0.6)
        
        if scores:
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            weighted_score = sum(s * w for s, w in zip(scores, weights) if s is not None)
            results['weighted_semantic_score'] = round(weighted_score, 2)
            results['overall_score'] = round(weighted_score, 2)
        else:
            results['overall_score'] = 0
        
        return results
    
    def analyze_project_relevance(self, resume_data: Dict, job_data: Dict) -> Dict:
        """
        分析项目经历相关性
        """
        projects = resume_data.get('background_info', {}).get('projects', [])
        projects_text = self._format_projects(projects)
        
        job_title = job_data.get('job_title', '')
        job_description = '\n'.join(job_data.get('responsibilities', []))
        
        prompt = PROJECT_RELEVANCE_PROMPT.format(
            job_title=job_title,
            job_description=job_description,
            projects_text=projects_text
        )
        
        response = self.llm_client.chat(prompt)
        
        result = self._parse_response(response)
        
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
                'overall_score': 0,
                'analysis': '解析失败',
                'strengths': [],
                'weaknesses': []
            }
    
    def _format_projects(self, projects: List[Dict]) -> str:
        """
        格式化项目经历
        """
        if not projects:
            return "无项目经历"
        
        lines = []
        for i, project in enumerate(projects, 1):
            lines.append(f"项目{i}：")
            lines.append(f"- 项目名称：{project.get('project_name', '未知')}")
            lines.append(f"- 担任角色：{project.get('role', '未知')}")
            lines.append(f"- 项目描述：{project.get('description', '无')}")
            lines.append(f"- 使用技术：{', '.join(project.get('technologies', []))}")
            lines.append(f"- 时间：{project.get('start_date', '')} - {project.get('end_date', '')}")
            lines.append("")
        
        return '\n'.join(lines)
    
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


semantic_matcher = None

def get_semantic_matcher() -> SemanticMatcher:
    global semantic_matcher
    if semantic_matcher is None:
        semantic_matcher = SemanticMatcher()
    return semantic_matcher
