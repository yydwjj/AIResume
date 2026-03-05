from typing import Dict, Optional

from .skill_matcher import get_skill_matcher
from .semantic_matcher import get_semantic_matcher
from ..config.settings import config


class DualMatcher:
    def __init__(self):
        self.skill_matcher = get_skill_matcher()
        self.semantic_matcher = get_semantic_matcher()
        
        match_config = config.get_match_config()
        self.rule_weight = match_config.get('rule_weight', 0.5)
        self.semantic_weight = match_config.get('semantic_weight', 0.5)
        self.default_mode = match_config.get('default_mode', 'standard')
    
    def match(
        self,
        resume_data: Dict,
        job_data: Dict,
        mode: Optional[str] = None
    ) -> Dict:
        """
        双轨匹配
        
        Args:
            resume_data: 简历数据
            job_data: 岗位数据
            mode: 匹配模式
                - quick: 仅规则匹配
                - standard: 规则匹配 + 综合语义分析
                - deep: 规则匹配 + 细粒度语义分析
        """
        if mode is None:
            mode = self.default_mode
        
        rule_result = self.skill_matcher.match(resume_data, job_data)
        
        if mode == "quick":
            return {
                'final_score': rule_result['match_score'],
                'mode': 'quick',
                'rule_based': rule_result,
                'semantic': None,
                'recommendation': self._get_recommendation(rule_result['match_score'])
            }
        
        if mode == "standard":
            semantic_result = self.semantic_matcher.analyze_comprehensive(
                resume_data, job_data
            )
        else:
            semantic_result = self.semantic_matcher.analyze_detailed(
                resume_data, job_data
            )
        
        semantic_score = semantic_result.get('overall_score', 0)
        
        final_score = (
            rule_result['match_score'] * self.rule_weight +
            semantic_score * self.semantic_weight
        )
        
        return {
            'final_score': round(final_score, 2),
            'mode': mode,
            'rule_based': rule_result,
            'semantic': semantic_result,
            'recommendation': self._get_recommendation(final_score)
        }
    
    def batch_match(
        self,
        resume_data_list: list,
        job_data_list: list,
        mode: Optional[str] = None
    ) -> list:
        """
        批量匹配
        """
        results = []
        
        for resume_data in resume_data_list:
            for job_data in job_data_list:
                result = self.match(resume_data, job_data, mode)
                result['resume_hash'] = resume_data.get('resume_hash')
                result['job_hash'] = job_data.get('job_hash')
                results.append(result)
        
        return results
    
    def _get_recommendation(self, score: float) -> str:
        """
        根据分数给出推荐
        """
        if score is None:
            score = 0
        
        if score >= 90:
            return "强烈推荐"
        elif score >= 80:
            return "推荐录用"
        elif score >= 70:
            return "可以考虑"
        elif score >= 60:
            return "需要进一步评估"
        else:
            return "不建议录用"


dual_matcher = None

def get_dual_matcher() -> DualMatcher:
    global dual_matcher
    if dual_matcher is None:
        dual_matcher = DualMatcher()
    return dual_matcher
