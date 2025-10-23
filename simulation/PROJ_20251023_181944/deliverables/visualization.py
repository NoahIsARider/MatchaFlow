"""
数据可视化模块
负责生成图表和报表数据
版本：2.0
"""
import json
from datetime import datetime, timedelta
from database import DatabaseManager
from collections import defaultdict

class DataVisualizer:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_monthly_summary_chart(self, user_id, year_month=None):
        """生成月度财务摘要图表数据"""
        if year_month is None:
            year_month = datetime.now().strftime('%Y-%m')
        
        summary = self.db.get_monthly_summary(user_id, year_month)
        
        # 生成饼图数据
        pie_chart_data = {
            'labels': [],
            'data': [],
            'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', 
                      '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384']
        }
        
        for category, amount in summary['category_expenses'].items():
            if amount > 0:
                pie_chart_data['labels'].append(category)
                pie_chart_data['data'].append(amount)
        
        # 生成趋势图数据（最近6个月）
        trend_data = self._get_trend_data(user_id, 6)
        
        return {
            'pie_chart': pie_chart_data,
            'trend_data': trend_data,
            'summary': summary
        }
    
    def get_budget_progress(self, user_id):
        """获取预算进度数据"""
        current_month = datetime.now().strftime('%Y-%m')
        summary = self.db.get_monthly_summary(user_id, current_month)
        
        # 获取用户预算设置
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT monthly_budget FROM users WHERE id = ?', (user_id,))
        user_budget = cursor.fetchone()
        monthly_budget = user_budget[0] if user_budget else 0
        
        conn.close()
        
        if monthly_budget == 0:
            return {
                'current_spending': summary['total_expense'],
                'monthly_budget': 0,
                'progress_percentage': 0,
                'remaining_budget': 0,
                'status': 'no_budget'
            }
        
        progress_percentage = (summary['total_expense'] / monthly_budget) * 100
        remaining_budget = monthly_budget - summary['total_expense']
        
        status = 'normal'
        if progress_percentage >= 90:
            status = 'danger'
        elif progress_percentage >= 70:
            status = 'warning'
        
        return {
            'current_spending': summary['total_expense'],
            'monthly_budget': monthly_budget,
            'progress_percentage': round(progress_percentage, 1),
            'remaining_budget': remaining_budget,
            'status': status
        }
    
    def get_recent_transactions(self, user_id, limit=10):
        """获取最近的交易记录"""
        transactions = self.db.get_user_transactions(user_id, limit)
        
        formatted_transactions = []
        for transaction in transactions:
            trans_id, amount, category, description, trans_type, created_at = transaction
            
            formatted_transactions.append({
                'id': trans_id,
                'amount': amount,
                'category': category,
                'description': description,
                'type': trans_type,
                'created_at': created_at,
                'formatted_amount': f"¥{amount:.2f}",
                'is_income': trans_type == 'income'
            })
        
        return formatted_transactions
    
    def _get_trend_data(self, user_id, months_count):
        """获取趋势数据"""
        trend_data = {
            'labels': [],
            'income': [],
            'expense': []
        }
        
        current_date = datetime.now()
        
        for i in range(months_count - 1, -1, -1):
            target_date = current_date - timedelta(days=30 * i)
            year_month = target_date.strftime('%Y-%m')
            
            summary = self.db.get_monthly_summary(user_id, year_month)
            
            trend_data['labels'].append(year_month)
            trend_data['income'].append(summary['total_income'])
            trend_data['expense'].append(summary['total_expense'])
        
        return trend_data
    
    def generate_monthly_report(self, user_id, year_month):
        """生成月度报告"""
        summary = self.db.get_monthly_summary(user_id, year_month)
        budget_progress = self.get_budget_progress(user_id)
        
        report = {
            'period': year_month,
            'total_income': summary['total_income'],
            'total_expense': summary['total_expense'],
            'net_savings': summary['total_income'] - summary['total_expense'],
            'category_breakdown': summary['category_expenses'],
            'budget_status': budget_progress['status'],
            'budget_utilization': budget_progress['progress_percentage']
        }
        
        # 生成建议
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report):
        """根据报告生成建议"""
        recommendations = []
        
        if report['net_savings'] < 0:
            recommendations.append("本月支出超过收入，建议控制消费")
        
        if report['budget_utilization'] > 90:
            recommendations.append("预算使用率过高，建议调整预算或减少支出")
        
        # 找出支出最高的类别
        if report['category_breakdown']:
            max_category = max(report['category_breakdown'].items(), key=lambda x: x[1])
            recommendations.append(f"'{max_category[0]}'类别支出最高，建议关注")
        
        if not recommendations:
            recommendations.append("财务状况良好，继续保持！")
        
        return recommendations

# 全局可视化实例
visualizer = DataVisualizer()