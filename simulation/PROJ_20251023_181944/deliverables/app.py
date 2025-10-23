"""
智能个人财务管理系统 - 主应用文件
负责用户界面和主要业务逻辑
版本：1.0
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 消费分类映射
CATEGORIES = {
    'food': '餐饮',
    'transport': '交通',
    'shopping': '购物',
    'entertainment': '娱乐',
    'health': '医疗',
    'education': '教育',
    'housing': '住房',
    'utilities': '水电煤',
    'travel': '旅行',
    'other': '其他'
}

@app.route('/')
def index():
    """首页 - 显示财务概览"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    summary = get_financial_summary(user_id)
    return render_template('index.html', summary=summary, categories=CATEGORIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 简单的用户验证（实际项目应使用加密和数据库查询）
        if username and password:
            session['user_id'] = 1  # 模拟用户ID
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """添加收支记录"""
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    amount = data.get('amount')
    category = data.get('category')
    description = data.get('description', '')
    transaction_type = data.get('type', 'expense')  # expense/income
    
    if not all([amount, category]):
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 保存到数据库
    transaction_id = save_transaction(user_id, amount, category, description, transaction_type)
    
    return jsonify({'success': True, 'transaction_id': transaction_id})

@app.route('/get_summary')
def get_summary():
    """获取财务摘要数据"""
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user_id = session['user_id']
    summary = get_financial_summary(user_id)
    return jsonify(summary)

def get_financial_summary(user_id):
    """获取用户财务摘要"""
    # 模拟数据 - 实际应从数据库查询
    return {
        'total_income': 15000,
        'total_expense': 8500,
        'balance': 6500,
        'monthly_budget': 10000,
        'category_expenses': {
            'food': 2000,
            'transport': 800,
            'shopping': 2500,
            'entertainment': 1200,
            'other': 2000
        }
    }

def save_transaction(user_id, amount, category, description, transaction_type):
    """保存交易记录到数据库"""
    # 模拟数据库操作
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transactions (user_id, amount, category, description, type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, amount, category, description, transaction_type, datetime.now()))
    
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return transaction_id

if __name__ == '__main__':
    app.run(debug=True)