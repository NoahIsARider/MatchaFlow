"""
职业测评引擎 - 完善版
集成题库管理和评分逻辑
"""
import json
import random
from typing import Dict, List, Any
from datetime import datetime

class AssessmentEngine:
    def __init__(self):
        self.question_bank = self._load_question_bank()
        self.scoring_rules = self._load_scoring_rules()
        
    def _load_question_bank(self) -> Dict[str, List[Dict]]:
        """加载测评题库"""
        return {
            "personality": [
                {
                    "id": 1,
                    "question": "在团队项目中，你更倾向于：",
                    "options": [
                        {"text": "领导团队，制定计划", "score": {"leadership": 2}},
                        {"text": "分析数据，提供建议", "score": {"analytical": 2}},
                        {"text": "协调沟通，解决冲突", "score": {"communication": 2}},
                        {"text": "执行任务，关注细节", "score": {"execution": 2}}
                    ]
                },
                {
                    "id": 2,
                    "question": "面对新挑战时，你首先会：",
                    "options": [
                        {"text": "制定详细计划", "score": {"planning": 2}},
                        {"text": "立即开始尝试", "score": {"action": 2}},
                        {"text": "寻求他人意见", "score": {"collaboration": 2}},
                        {"text": "研究相关资料", "score": {"research": 2}}
                    ]
                }
            ],
            "skills": [
                {
                    "id": 3,
                    "question": "你的编程经验水平：",
                    "options": [
                        {"text": "无经验", "score": {"programming": 0}},
                        {"text": "初学者", "score": {"programming": 1}},
                        {"text": "熟练使用1-2种语言", "score": {"programming": 2}},
                        {"text": "精通多种语言", "score": {"programming": 3}}
                    ]
                },
                {
                    "id": 4,
                    "question": "数据分析能力：",
                    "options": [
                        {"text": "不了解", "score": {"data_analysis": 0}},
                        {"text": "基础Excel操作", "score": {"data_analysis": 1}},
                        {"text": "使用Python/R分析", "score": {"data_analysis": 2}},
                        {"text": "精通机器学习", "score": {"data_analysis": 3}}
                    ]
                }
            ]
        }
    
    def _load_scoring_rules(self) -> Dict[str, Dict]:
        """加载评分规则"""
        return {
            "career_mapping": {
                "software_engineer": {
                    "required_traits": ["programming", "problem_solving", "technical"],
                    "weight": {"programming": 0.4, "problem_solving": 0.3, "technical": 0.3}
                },
                "data_scientist": {
                    "required_traits": ["data_analysis", "statistics", "research"],
                    "weight": {"data_analysis": 0.4, "statistics": 0.3, "research": 0.3}
                },
                "product_manager": {
                    "required_traits": ["leadership", "communication", "planning"],
                    "weight": {"leadership": 0.3, "communication": 0.4, "planning": 0.3}
                }
            }
        }
    
    def generate_assessment(self, user_id: str, categories: List[str] = None) -> Dict[str, Any]:
        """生成个性化测评"""
        if categories is None:
            categories = ["personality", "skills"]
            
        assessment = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "questions": []
        }
        
        for category in categories:
            if category in self.question_bank:
                # 随机选择每个类别的题目
                selected_questions = random.sample(
                    self.question_bank[category], 
                    min(3, len(self.question_bank[category]))
                )
                assessment["questions"].extend(selected_questions)
        
        return assessment
    
    def calculate_score(self, user_answers: Dict[str, List[int]]) -> Dict[str, Any]:
        """计算测评得分"""
        trait_scores = {}
        
        for question_id, answer_indices in user_answers.items():
            question = self._find_question_by_id(int(question_id))
            if question:
                for answer_index in answer_indices:
                    if 0 <= answer_index < len(question["options"]):
                        option = question["options"][answer_index]
                        for trait, score in option["score"].items():
                            trait_scores[trait] = trait_scores.get(trait, 0) + score
        
        # 计算职业匹配度
        career_recommendations = self._generate_career_recommendations(trait_scores)
        
        return {
            "trait_scores": trait_scores,
            "career_recommendations": career_recommendations,
            "assessment_date": datetime.now().isoformat()
        }
    
    def _find_question_by_id(self, question_id: int) -> Dict:
        """根据ID查找题目"""
        for category_questions in self.question_bank.values():
            for question in category_questions:
                if question["id"] == question_id:
                    return question
        return None
    
    def _generate_career_recommendations(self, trait_scores: Dict[str, int]) -> List[Dict]:
        """生成职业推荐"""
        recommendations = []
        
        for career, rules in self.scoring_rules["career_mapping"].items():
            match_score = 0
            total_weight = 0
            
            for trait, weight in rules["weight"].items():
                trait_value = trait_scores.get(trait, 0)
                match_score += trait_value * weight
                total_weight += weight
            
            if total_weight > 0:
                normalized_score = match_score / total_weight
                recommendations.append({
                    "career": career,
                    "match_score": round(normalized_score, 2),
                    "strengths": [trait for trait in rules["required_traits"] 
                                 if trait_scores.get(trait, 0) > 1],
                    "improvement_areas": [trait for trait in rules["required_traits"] 
                                        if trait_scores.get(trait, 0) <= 1]
                })
        
        return sorted(recommendations, key=lambda x: x["match_score"], reverse=True)[:3]