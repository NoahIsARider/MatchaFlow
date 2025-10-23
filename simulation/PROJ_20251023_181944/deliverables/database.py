"""
数据库管理模块
负责数据库初始化、连接和基础操作
版本：1.0
"""
import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='finance.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                monthly_budget REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,  -- 'income' or 'expense'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 创建预算设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                month_year TEXT NOT NULL,  -- Format: YYYY-MM
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 插入示例数据
        self._insert_sample_data(cursor)
        
        conn.commit()
        conn.close()
        
        print("数据库初始化完成")
    
    def _insert_sample_data(self, cursor):
        """插入示例数据用于演示"""
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # 插入示例用户
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, monthly_budget)
                VALUES (?, ?, ?, ?)
            ''', ('demo_user', 'demo@example.com', 'hashed_password', 10000))
            
            # 插入示例交易记录
            sample_transactions = [
                (1, 15000, 'income', '工资收入', 'income', '2024-01-05'),
                (1, 200, 'food', '午餐', 'expense', '2024-01-06'),
                (1, 50, 'transport', '地铁卡充值', 'expense', '2024-01-06'),
                (1, 300, 'shopping', '购买衣服', 'expense', '2024-01-07'),
                (1, 150, 'entertainment', '看电影', 'expense', '2024-01-08')
            ]
            
            for transaction in sample_transactions:
                cursor.execute('''
                    INSERT INTO transactions (user_id, amount, category, description, type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', transaction)
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def get_user_transactions(self, user_id, limit=50):
        """获取用户的交易记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, amount, category, description, type, created_at
            FROM transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        transactions = cursor.fetchall()
        conn.close()
        
        return transactions
    
    def get_monthly_summary(self, user_id, year_month):
        """获取月度财务摘要"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取总收入
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE user_id = ? AND type = 'income' 
            AND strftime('%Y-%m', created_at) = ?
        ''', (user_id, year_month))
        
        total_income = cursor.fetchone()[0]
        
        # 获取总支出
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE user_id = ? AND type = 'expense' 
            AND strftime('%Y-%m', created_at) = ?
        ''', (user_id, year_month))
        
        total_expense = cursor.fetchone()[0]
        
        # 获取分类支出
        cursor.execute('''
            SELECT category, COALESCE(SUM(amount), 0) as amount
            FROM transactions 
            WHERE user_id = ? AND type = 'expense' 
            AND strftime('%Y-%m', created_at) = ?
            GROUP BY category
        ''', (user_id, year_month))
        
        category_expenses = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'category_expenses': category_expenses
        }
    
    def add_transaction(self, user_id, amount, category, description, transaction_type):
        """添加新的交易记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (user_id, amount, category, description, type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, amount, category, description, transaction_type, datetime.now()))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return transaction_id

# 创建全局数据库管理器实例
db = DatabaseManager()