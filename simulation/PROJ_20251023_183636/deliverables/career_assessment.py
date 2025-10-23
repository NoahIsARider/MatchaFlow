"""
职业倾向测评模块
负责分析用户技能和兴趣，提供职业建议
"""
import numpy as np
from typing import List, Dict, Any

class CareerAssessment:
    def __init__(self):
        # 预定义的职业数据库
        self.career_database = {
            'software_engineer': {
                'required_skills': ['programming', 'algorithms', 'problem_solving'],
                'interest_fit': ['technology', 'innovation', 'coding'],
                'experience_level': 2
            },
            'data_scientist': {
                'required_skills': ['statistics', 'machine_learning', 'python'],
                'interest_fit': ['data', 'analysis', 'research'],
                'experience_level': 2
            },
            'product_manager': {
                'required_skills': ['communication', 'strategy', 'market_analysis'],
                'interest_fit': ['business', 'leadership', 'innovation'],
                'experience_level': 3
            },
            'ux_designer': {
                'required_skills': ['design_thinking', 'user_research', 'prototyping'],
                'interest_fit': ['creativity', 'user_experience', 'design'],
                'experience_level': 2
            }
        }
        
        # 技能权重配置
        self.skill_weights = {
            'programming': 0.3,
            'algorithms': 0.2,
            'problem_solving': 0.25,
            'statistics': 0.3,
            'machine_learning': 0.35,
            'python': 0.2,
            'communication': 0.4,
            'strategy': 0.3,
            'market_analysis': 0.3,
            'design_thinking': 0.35,
            'user_research': 0.3,
            'prototyping': 0.35
        }

    def analyze_career_fit(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析用户与不同职业的匹配度
        """
        user_skills = user_data.get('skills', [])
        user_interests = user_data.get('interests', [])
        user_experience = user_data.get('experience', 0)
        
        career_suggestions = []
        
        for career, requirements in self.career_database.items():
            # 计算技能匹配度
            skill_match = self._calculate_skill_match(user_skills, requirements['required_skills'])
            
            # 计算兴趣匹配度
            interest_match = self._calculate_interest_match(user_interests, requirements['interest_fit'])
            
            # 计算经验匹配度
            experience_match = self._calculate_experience_match(user_experience, requirements['experience_level'])
            
            # 综合评分
            overall_score = (skill_match * 0.5 + interest_match * 0.3 + experience_match * 0.2)
            
            # 识别技能差距
            skill_gaps = self._identify_skill_gaps(user_skills, requirements['required_skills'])
            
            career_suggestions.append({
                'career': career,
                'match_score': round(overall_score, 2),
                'skill_gaps': skill_gaps,
                'confidence_score': self._calculate_confidence(overall_score, len(user_skills))
            })
        
        # 按匹配度排序
        career_suggestions.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            'suggestions': career_suggestions[:3],  # 返回前3个建议
            'skill_gaps': self._consolidate_skill_gaps(career_suggestions),
            'confidence_score': self._calculate_overall_confidence(career_suggestions)
        }

    def _calculate_skill_match(self, user_skills: List[str], required_skills: List[str]) -> float:
        """计算技能匹配度"""
        if not required_skills:
            return 0.0
            
        matched_skills = set(user_skills) & set(required_skills)
        total_weight = sum(self.skill_weights.get(skill, 0.1) for skill in required_skills)
        matched_weight = sum(self.skill_weights.get(skill, 0.1) for skill in matched_skills)
        
        return matched_weight / total_weight if total_weight > 0 else 0.0

    def _calculate_interest_match(self, user_interests: List[str], career_interests: List[str]) -> float:
        """计算兴趣匹配度"""
        if not career_interests:
            return 0.0
            
        matched_interests = set(user_interests) & set(career_interests)
        return len(matched_interests) / len(career_interests)

    def _calculate_experience_match(self, user_exp: int, required_exp: int) -> float:
        """计算经验匹配度"""
        if user_exp >= required_exp:
            return 1.0
        return user_exp / required_exp

    def _identify_skill_gaps(self, user_skills: List[str], required_skills: List[str]) -> List[str]:
        """识别技能差距"""
        return list(set(required_skills) - set(user_skills))

    def _calculate_confidence(self, match_score: float, skill_count: int) -> float:
        """计算置信度"""
        base_confidence = match_score
        skill_bonus = min(skill_count * 0.05, 0.3)  # 最多30%加成
        return min(base_confidence + skill_bonus, 1.0)

    def _consolidate_skill_gaps(self, suggestions: List[Dict]) -> List[str]:
        """整合所有建议中的技能差距"""
        all_gaps = set()
        for suggestion in suggestions:
            all_gaps.update(suggestion['skill_gaps'])
        return list(all_gaps)

    def _calculate_overall_confidence(self, suggestions: List[Dict]) -> float:
        """计算总体置信度"""
        if not suggestions:
            return 0.0
        return sum(s['confidence_score'] for s in suggestions) / len(suggestions)