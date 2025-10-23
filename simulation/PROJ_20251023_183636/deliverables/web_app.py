"""
Web应用主入口 - 优化版
集成所有模块，提供完整的用户流程
"""
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
from assessment_engine import AssessmentEngine
from user_manager import UserManager
from resume_analyzer import ResumeAnalyzer

app = Flask(__name__)
app.secret_key = 'career_platform_secret_key'

# 初始化核心组件
assessment_engine = AssessmentEngine()
user_manager = UserManager()
resume_analyzer = ResumeAnalyzer()

@app.route('/')
def index():
    """首页"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if user_manager.register_user(email, password, full_name):
            return jsonify({'success': True, 'message': '注册成功'})
        else:
            return jsonify({'success': False, 'message': '邮箱已存在'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user_id = user_manager.authenticate_user(email, password)
        if user_id:
            session['user_id'] = user_id
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '邮箱或密码错误'})
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """用户仪表板"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    profile = user_manager.get_user_profile(user_id)
    assessment_history = user_manager.get_assessment_history(user_id)
    
    return render_template('dashboard.html', 
                         profile=profile, 
                         history=assessment_history)

@app.route('/assessment/start')
def start_assessment():
    """开始测评"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    assessment = assessment_engine.generate_assessment(user_id)
    session['current_assessment'] = assessment
    
    return render_template('assessment.html', assessment=assessment)

@app.route('/assessment/submit', methods=['POST'])
def submit_assessment():
    """提交测评答案"""
    if 'user_id' not in session or 'current_assessment' not in session:
        return jsonify({'success': False, 'message': '会话已过期'})
    
    user_id = session['user_id']
    answers = request.get_json().get('answers', {})
    
    # 计算得分
    results = assessment_engine.calculate_score(answers)
    
    # 验证结果准确性
    validation_result = assessment_engine.validate_results(results)
    
    # 保存结果
    questions = session['current_assessment']['questions']
    user_manager.save_assessment_result(
        user_id, 'career_assessment', questions, answers, results
    )
    
    # 清理会话
    session.pop('current_assessment', None)
    
    return jsonify({
        'success': True,
        'results': results,
        'validation': validation_result
    })

@app.route('/assessment/results/<int:assessment_id>')
def view_results(assessment_id):
    """查看测评结果"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    result = user_manager.get_assessment_result(user_id, assessment_id)
    
    if not result:
        return redirect(url_for('dashboard'))
    
    return render_template('results.html', result=result)

@app.route('/resume/analyze', methods=['POST'])
def analyze_resume():
    """分析简历"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    if 'resume_file' not in request.files:
        return jsonify({'success': False, 'message': '未上传文件'})
    
    resume_file = request.files['resume_file']
    if resume_file.filename == '':
        return jsonify({'success': False, 'message': '未选择文件'})
    
    # 分析简历
    analysis_result = resume_analyzer.analyze_resume(resume_file)
    
    return jsonify({
        'success': True,
        'analysis': analysis_result
    })

@app.route('/profile/update', methods=['POST'])
def update_profile():
    """更新用户资料"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    user_id = session['user_id']
    profile_data = request.get_json()
    
    if user_manager.update_user_profile(user_id, profile_data):
        return jsonify({'success': True, 'message': '资料更新成功'})
    else:
        return jsonify({'success': False, 'message': '资料更新失败'})

@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)