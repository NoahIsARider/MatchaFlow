"""
预算管理模块
负责预算设置、提醒和监控
版本：3.0
"""
import sqlite3
from datetime import datetime, timedelta
from database import DatabaseManager
import smtplib
from email.mime.text import MIMEText

class BudgetManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def set_user_budget(self, user_id, monthly_budget, category_budgets=None):
        """设置用户预算"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 更新用户月度预算
            cursor.execute('''
                UPDATE users 
                SET monthly_budget = ? 
                WHERE id = ?
            ''', (monthly_budget, user_id))
            
            # 设置分类预算
            if category_budgets:
                for category, budget in category_budgets.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO category_budgets 
                        (user_id, category, budget_amount, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, category, budget, datetime.now()))
            
            conn.commit()
            conn.close()
            
            return True, "预算设置成功"
            
        except Exception as e:
            return False, f"预算设置失败: {str(e)}"
    
    def check_budget_alerts(self, user_id):
        """检查预算提醒"""
        current_month = datetime.now().strftime('%Y-%m')
        summary = self.db.get_monthly_summary(user_id, current_month)
        
        alerts = []
        
        # 检查月度总预算
        monthly_budget = self._get_user_monthly_budget(user_id)
        if monthly_budget > 0:
            expense_ratio = summary['total_expense'] / monthly_budget
            
            if expense_ratio >= 0.9:
                alerts.append({
                    'type': 'danger',
                    'message': f'月度预算即将用尽！已使用{expense_ratio*100:.1f}%',
                    'remaining': monthly_budget - summary['total_expense']
                })
            elif expense_ratio >= 0.7:
                alerts.append({
                    'type': 'warning',
                    'message': f'月度预算使用率较高：{expense_ratio*100:.1f}%',
                    'remaining': monthly_budget - summary['total_expense']
                })
        
        # 检查分类预算
        category_alerts = self._check_category_budgets(user_id, summary['category_expenses'])
        alerts.extend(category_alerts)
        
        return alerts
    
    def get_budget_recommendation(self, user_id):
        """生成预算建议"""
        # 分析过去3个月的消费模式
        recommendations = []
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 获取过去3个月的消费数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM transactions 
                WHERE user_id = ? AND type = 'expense' 
                AND created_at BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total DESC
            ''', (user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            category_totals = cursor.fetchall()
            conn.close()
            
            if category_totals:
                total_expense = sum([item[1] for item in category_totals])
                
                for category, amount in category_totals[:3]:  # 前3大支出类别
                    percentage = (amount / total_expense) * 100
                    recommendations.append({
                        'category': category,
                        'suggestion': f"'{category}'占总支出的{percentage:.1f}%，建议关注"
                    })
            
            if not recommendations:
                recommendations.append({
                    'category': 'general',
                    'suggestion': '基于您的消费习惯，建议设置月度预算以更好管理财务'
                })
                
        except Exception as e:
            recommendations.append({
                'category': 'error',
                'suggestion': '暂时无法生成建议'
            })
        
        return recommendations
    
    def _get_user_monthly_budget(self, user_id):
        """获取用户月度预算"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT monthly_budget FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def _check_category_budgets(self, user_id, category_expenses):
        """检查分类预算"""
        alerts = []
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, budget_amount 
                FROM category_budgets 
                WHERE user_id = ?
            ''', (user_id,))
            
            category_budgets = cursor.fetchall()
            conn.close()
            
            for category, budget in category_budgets:
                actual_expense = category_expenses.get(category, 0)
                if budget > 0 and actual_expense >= budget * 0.8:
                    usage_ratio = actual_expense / budget
                    alert_type = 'danger' if usage_ratio >= 1 else 'warning'
                    
                    alerts.append({
                        'type': alert_type,
                        'message': f"'{category}'分类预算{'已超支' if usage_ratio >= 1 else '即将用尽'}",
                        'category': category,
                        'budget': budget,
                        'actual': actual_expense
                    })
                    
        except Exception as e:
            print(f"检查分类预算时出错: {e}")
        
        return alerts
    
    def send_budget_alert_email(self, user_email, alert_data):
        """发送预算提醒邮件（模拟实现）"""
        # 实际项目中需要配置SMTP服务器
        print(f"发送预算提醒邮件到: {user_email}")
        print(f"提醒内容: {alert_data}")
        return True

# 全局预算管理器实例
budget_manager = BudgetManager()