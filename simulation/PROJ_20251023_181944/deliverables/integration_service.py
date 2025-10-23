"""
集成服务模块
负责模块间数据流转和流程整合
版本：3.0
"""
from user_auth import user_manager
from visualization import visualizer
from budget_manager import budget_manager
from database import DatabaseManager
import json

class IntegrationService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_user_dashboard_data(self, user_id):
        """获取用户仪表板完整数据"""
        try:
            # 验证用户会话
            if not user_manager.validate_session(user_id):
                return {'error': '用户会话无效'}
            
            # 并行获取各种数据
            dashboard_data = {
                'user_info': self._get_user_info(user_id),
                'monthly_summary': self._get_monthly_summary(user_id),
                'budget_progress': visualizer.get_budget_progress(user_id),
                'recent_transactions': visualizer.get_recent_transactions(user_id, 5),
                'budget_alerts': budget_manager.check_budget_alerts(user_id),
                'visualization_data': visualizer.get_monthly_summary_chart(user_id),
                'budget_recommendations': budget_manager.get_budget_recommendation(user_id)
            }
            
            return {'success': True, 'data': dashboard_data}
            
        except Exception as e:
            return {'error': f'获取仪表板数据失败: {str(e)}'}
    
    def complete_user_workflow(self, user_id, transaction_data=None):
        """完整的用户工作流程"""
        workflow_result = {
            'steps_completed': [],
            'errors': [],
            'data': {}
        }
        
        try:
            # 步骤1: 验证用户
            if not user_manager.validate_session(user_id):
                workflow_result['errors'].append('用户验证失败')
                return workflow_result
            
            workflow_result['steps_completed'].append('用户验证')
            
            # 步骤2: 如果有新交易，记录交易
            if transaction_data:
                success, message = self.db.add_transaction(
                    user_id, 
                    transaction_data['amount'],
                    transaction_data['category'],
                    transaction_data['description'],
                    transaction_data['type']
                )
                if success:
                    workflow_result['steps_completed'].append('记录交易')
                    workflow_result['data']['transaction_id'] = message
                else:
                    workflow_result['errors'].append(f'记录交易失败: {message}')
            
            # 步骤3: 获取最新数据
            dashboard_data = self.get_user_dashboard_data(user_id)
            if 'error' not in dashboard_data:
                workflow_result['steps_completed'].append('数据更新')
                workflow_result['data'].update(dashboard_data['data'])
            else:
                workflow_result['errors'].append(dashboard_data['error'])
            
            # 步骤4: 检查预算提醒
            alerts = budget_manager.check_budget_alerts(user_id)
            if alerts:
                workflow_result['steps_completed'].append('预算检查')
                workflow_result['data']['alerts'] = alerts
            
            return workflow_result
            
        except Exception as e:
            workflow_result['errors'].append(f'工作流程执行失败: {str(e)}')
            return workflow_result
    
    def export_user_data(self, user_id, format_type='json'):
        """导出用户数据"""
        try:
            if not user_manager.validate_session(user_id):
                return {'error': '用户会话无效'}
            
            # 获取用户基本信息
            user_info = self._get_user_info(user_id)
            
            # 获取交易记录
            transactions = self.db.get_user_transactions(user_id, limit=1000)
            
            # 获取预算设置
            budget_settings = self._get_budget_settings(user_id)
            
            export_data = {
                'user_info': user_info,
                'transactions': [
                    {
                        'id': t[0],
                        'amount': t[1],
                        'category': t[2],
                        'description': t[3],
                        'type': t[4],
                        'created_at': t[5]
                    } for t in transactions
                ],
                'budget_settings': budget_settings,
                'export_date': datetime.now().isoformat()
            }
            
            if format_type == 'json':
                return {'success': True, 'data': json.dumps(export_data, indent=2, ensure_ascii=False)}
            else:
                return {'error': '暂不支持该导出格式'}
                
        except Exception as e:
            return {'error': f'数据导出失败: {str(e)}'}
    
    def _get_user_info(self, user_id):
        """获取用户信息"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, monthly_budget, created_at 
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'monthly_budget': user[3],
                'created_at': user[4]
            }
        return {}
    
    def _get_monthly_summary(self, user_id):
        """获取月度摘要"""
        current_month = datetime.now().strftime('%Y-%m')
        return self.db.get_monthly_summary(user_id, current_month)
    
    def _get_budget_settings(self, user_id):
        """获取预算设置"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, budget_amount 
            FROM category_budgets 
            WHERE user_id = ?
        ''', (user_id,))
        
        budgets = cursor.fetchall()
        conn.close()
        
        return {category: amount for category, amount in budgets}

# 全局集成服务实例
integration_service = IntegrationService()