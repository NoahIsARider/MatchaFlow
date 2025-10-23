"""
用户认证模块
负责用户注册、登录、会话管理
版本：2.0
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime
from database import DatabaseManager

class UserManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def register_user(self, username, email, password, monthly_budget=0):
        """用户注册"""
        # 输入验证
        if not all([username, email, password]):
            return False, "请填写所有必填字段"
        
        if len(password) < 6:
            return False, "密码长度至少6位"
        
        # 检查用户是否已存在
        if self._user_exists(username, email):
            return False, "用户名或邮箱已存在"
        
        # 密码加密
        password_hash = self._hash_password(password)
        
        # 保存用户信息
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, monthly_budget)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, monthly_budget))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return True, f"用户注册成功，ID: {user_id}"
            
        except Exception as e:
            return False, f"注册失败: {str(e)}"
    
    def login_user(self, username, password):
        """用户登录"""
        if not username or not password:
            return False, "请输入用户名和密码"
        
        password_hash = self._hash_password(password)
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, monthly_budget 
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return True, {
                    'user_id': user[0],
                    'username': user[1],
                    'monthly_budget': user[2]
                }
            else:
                return False, "用户名或密码错误"
                
        except Exception as e:
            return False, f"登录失败: {str(e)}"
    
    def update_user_budget(self, user_id, monthly_budget):
        """更新用户月度预算"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET monthly_budget = ? 
                WHERE id = ?
            ''', (monthly_budget, user_id))
            
            conn.commit()
            conn.close()
            
            return True, "预算更新成功"
            
        except Exception as e:
            return False, f"预算更新失败: {str(e)}"
    
    def _user_exists(self, username, email):
        """检查用户是否已存在"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE username = ? OR email = ?
        ''', (username, email))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def _hash_password(self, password):
        """密码加密"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_session(self, user_id):
        """验证用户会话"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        return user is not None

# 全局用户管理器实例
user_manager = UserManager()