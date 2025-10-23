"""
求职建议平台主应用文件
包含核心路由和功能集成
"""
from flask import Flask, request, jsonify, render_template
import json
from career_assessment import CareerAssessment
from resume_analyzer import ResumeAnalyzer

app = Flask(__name__)

# 初始化核心模块
career_assessment = CareerAssessment()
resume_analyzer = ResumeAnalyzer()

@app.route('/')
def index():
    """平台首页"""
    return render_template('index.html')

@app.route('/api/assessment', methods=['POST'])
def career_assessment_endpoint():
    """职业倾向测评API"""
    try:
        data = request.get_json()
        user_data = {
            'skills': data.get('skills', []),
            'interests': data.get('interests', []),
            'experience': data.get('experience', 0)
        }
        
        result = career_assessment.analyze_career_fit(user_data)
        return jsonify({
            'success': True,
            'career_suggestions': result['suggestions'],
            'skill_gaps': result['skill_gaps'],
            'confidence_score': result['confidence_score']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resume/analyze', methods=['POST'])
def resume_analysis_endpoint():
    """简历分析API"""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        analysis_result = resume_analyzer.analyze_resume(resume_text)
        return jsonify({
            'success': True,
            'grammar_score': analysis_result['grammar_score'],
            'structure_score': analysis_result['structure_score'],
            'improvement_suggestions': analysis_result['suggestions']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/learning-path', methods=['POST'])
def learning_path_endpoint():
    """学习路径生成API"""
    try:
        data = request.get_json()
        target_role = data.get('target_role', '')
        current_skills = data.get('current_skills', [])
        
        # 模拟学习路径生成逻辑
        learning_path = {
            'target_role': target_role,
            'steps': [
                {'step': 1, 'action': '学习基础技能', 'duration': '2周'},
                {'step': 2, 'action': '完成实践项目', 'duration': '3周'},
                {'step': 3, 'action': '准备面试技巧', 'duration': '1周'}
            ],
            'estimated_completion': '6周'
        }
        
        return jsonify({'success': True, 'learning_path': learning_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)