import json
import os
from typing import Dict, List, Optional

from .skill_database import get_skill_db
from ..utils.llm_client import get_llm_client


class SkillLearner:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.unlearned_skills_file = os.path.join(current_dir, "unlearned_skills.json")
        self.unlearned_skills = self._load_unlearned_skills()
        self.skill_db = get_skill_db()
        self.llm_client = None
        self.auto_learn_threshold = 3
    
    def _load_unlearned_skills(self) -> Dict:
        if os.path.exists(self.unlearned_skills_file):
            with open(self.unlearned_skills_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _get_llm_client(self):
        if self.llm_client is None:
            self.llm_client = get_llm_client()
        return self.llm_client
    
    def learn_skill(self, original_skill: str) -> str:
        normalized = self.skill_db.normalize(original_skill)
        
        if normalized and normalized != original_skill.strip().title():
            return normalized
        
        llm = self._get_llm_client()
        
        prompt = f"""请将以下技能名称标准化为最通用的名称。

原始技能名称: {original_skill}

要求:
1. 返回最通用、最标准的技能名称
2. 如果是缩写，返回全称（如"ML" -> "机器学习"）
3. 如果有多个名称，选择最常用的
4. 只返回标准化后的名称，不要解释

示例:
- "Python编程" -> "Python"
- "深度学习" -> "深度学习"
- "ML" -> "机器学习"
- "React.js" -> "React"
"""
        
        response = llm.chat(prompt)
        learned_skill = response.strip()
        
        if original_skill in self.unlearned_skills:
            self.unlearned_skills[original_skill]['count'] += 1
        else:
            self.unlearned_skills[original_skill] = {
                'normalized': learned_skill,
                'count': 1
            }
        
        self._save_unlearned_skills()
        
        if self.unlearned_skills[original_skill]['count'] >= self.auto_learn_threshold:
            self.skill_db.add_skill_mapping(original_skill, learned_skill)
            del self.unlearned_skills[original_skill]
            self._save_unlearned_skills()
        
        return learned_skill
    
    def _save_unlearned_skills(self) -> None:
        os.makedirs(os.path.dirname(self.unlearned_skills_file), exist_ok=True)
        with open(self.unlearned_skills_file, 'w', encoding='utf-8') as f:
            json.dump(self.unlearned_skills, f, ensure_ascii=False, indent=2)
    
    def get_unlearned_skills_report(self) -> List[Dict]:
        return [
            {'original': k, 'normalized': v['normalized'], 'count': v['count']}
            for k, v in sorted(
                self.unlearned_skills.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
        ]
    
    def approve_skill(self, original_skill: str, normalized_skill: Optional[str] = None) -> bool:
        if original_skill not in self.unlearned_skills:
            return False
        
        if normalized_skill is None:
            normalized_skill = self.unlearned_skills[original_skill]['normalized']
        
        self.skill_db.add_skill_mapping(original_skill, normalized_skill)
        del self.unlearned_skills[original_skill]
        self._save_unlearned_skills()
        
        return True
    
    def reject_skill(self, original_skill: str) -> bool:
        if original_skill not in self.unlearned_skills:
            return False
        
        del self.unlearned_skills[original_skill]
        self._save_unlearned_skills()
        
        return True
    
    def clear_unlearned_skills(self) -> None:
        self.unlearned_skills = {}
        self._save_unlearned_skills()


skill_learner = None

def get_skill_learner() -> SkillLearner:
    global skill_learner
    if skill_learner is None:
        skill_learner = SkillLearner()
    return skill_learner
