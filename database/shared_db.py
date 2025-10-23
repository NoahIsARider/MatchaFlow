"""
共享数据库
"""
from typing import Dict, List, Any
import json
import os
from datetime import datetime


class SharedDatabase:
    """
    项目共享数据库
    
    存储项目过程中的所有数据，包括：
    - 项目章程
    - 三大约束
    - WBS
    - 管理计划
    - 会议记录
    - 讨论记录
    - 代码文件
    - 文档
    - EVM记录
    - 执行循环记录
    - 关键路径分析记录（新增）
    - 关键链计划分析记录（新增）
    - 净现值分析记录（新增）
    """
    
    def __init__(self, project_code: str = None):
        self.project_code = project_code
        self.data = {
            'project_charter': '',
            'constraints': {},  # cost, scope, schedule
            'wbs': '',
            'management_plans': {},  # cost_plan, scope_plan, schedule_plan
            'meeting_records': [],
            'discussions': [],
            'code_files': {},
            'documents': {},
            'evm_records': [],
            'execution_cycles': [],
            'cycle_feedbacks': [],  # 新增：循环反馈记录
            'critical_path_analysis': {},  # 新增：关键路径分析
            'critical_chain_records': [],  # 新增：关键链分析记录
            'npv_records': []  # 新增：NPV分析记录
        }
    
    def save_project_charter(self, charter: str):
        """保存项目章程"""
        self.data['project_charter'] = charter
    
    def save_constraints(self, constraints: Dict[str, str]):
        """保存三大约束"""
        self.data['constraints'] = constraints
    
    def save_wbs(self, wbs: str):
        """保存WBS"""
        self.data['wbs'] = wbs
    
    def save_management_plans(self, plans: Dict[str, str]):
        """保存管理计划"""
        self.data['management_plans'] = plans
    
    def save_meeting_record(self, meeting_type: str, content: str):
        """保存会议记录"""
        record = {
            'type': meeting_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.data['meeting_records'].append(record)
    
    def save_discussion(self, participants: List[str], topic: str, content: str):
        """保存讨论记录"""
        discussion = {
            'participants': participants,
            'topic': topic,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.data['discussions'].append(discussion)
    
    def save_code_file(self, filename: str, content: str):
        """保存代码文件"""
        self.data['code_files'][filename] = content
    
    def save_document(self, doc_name: str, content: str):
        """保存文档"""
        self.data['documents'][doc_name] = content
    
    def save_evm_record(self, cycle: int, evm_data: Dict):
        """保存EVM分析记录"""
        record = {
            'cycle': cycle,
            'timestamp': datetime.now().isoformat(),
            **evm_data
        }
        self.data['evm_records'].append(record)
    
    def start_execution_cycle(self, cycle: int):
        """开始执行循环"""
        print(f"\n============================================================")
        print(f"阶段 4&5/6: 执行与控制 - 第{cycle}次循环")
        print(f"============================================================")
    
    def save_execution_cycle(self, cycle: int, phase: str, data: Dict):
        """保存执行循环记录"""
        record = {
            'cycle': cycle,
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.data['execution_cycles'].append(record)
    
    def update_cycle_feedback(self, cycle: int, feedback: str, accepted: bool):
        """更新循环反馈记录"""
        feedback_record = {
            'cycle': cycle,
            'feedback': feedback,
            'accepted': accepted,
            'timestamp': datetime.now().isoformat()
        }
        self.data['cycle_feedbacks'].append(feedback_record)
    
    def save_critical_path_analysis(self, cpm_data: Dict):
        """保存关键路径分析"""
        self.data['critical_path_analysis'] = {
            'timestamp': datetime.now().isoformat(),
            **cpm_data
        }
    
    def save_critical_chain_record(self, cycle: int, ccpm_data: Dict):
        """保存关键链分析记录"""
        record = {
            'cycle': cycle,
            'timestamp': datetime.now().isoformat(),
            **ccpm_data
        }
        self.data['critical_chain_records'].append(record)
    
    def save_npv_record(self, cycle: int, npv_data: Dict):
        """保存NPV分析记录"""
        record = {
            'cycle': cycle,
            'timestamp': datetime.now().isoformat(),
            **npv_data
        }
        self.data['npv_records'].append(record)
    
    def get_latest_plans(self) -> Dict:
        """获取最新的管理计划"""
        return {
            'wbs': self.data.get('wbs', ''),
            'cost_plan': self.data.get('management_plans', {}).get('cost', ''),
            'scope_plan': self.data.get('management_plans', {}).get('scope', ''),
            'schedule_plan': self.data.get('management_plans', {}).get('schedule', '')
        }
    
    def get_latest_evm(self) -> Dict:
        """获取最新的EVM记录"""
        if self.data['evm_records']:
            return self.data['evm_records'][-1]
        return {}
    
    def get_critical_path_analysis(self) -> Dict:
        """获取关键路径分析"""
        return self.data.get('critical_path_analysis', {})
    
    def get_latest_critical_chain(self) -> Dict:
        """获取最新的关键链分析记录"""
        if self.data['critical_chain_records']:
            return self.data['critical_chain_records'][-1]
        return {}
    
    def get_latest_npv(self) -> Dict:
        """获取最新的NPV分析记录"""
        if self.data['npv_records']:
            return self.data['npv_records'][-1]
        return {}
    
    def export_to_file(self, filepath: str):
        """导出数据到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """从文件加载数据"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
    
    def get_summary(self) -> Dict:
        """获取数据库摘要"""
        return {
            'project_charter_length': len(self.data.get('project_charter', '')),
            'constraints_count': len(self.data.get('constraints', {})),
            'wbs_length': len(self.data.get('wbs', '')),
            'management_plans_count': len(self.data.get('management_plans', {})),
            'meeting_records_count': len(self.data.get('meeting_records', [])),
            'discussions_count': len(self.data.get('discussions', [])),
            'code_files_count': len(self.data.get('code_files', {})),
            'documents_count': len(self.data.get('documents', {})),
            'evm_records_count': len(self.data.get('evm_records', [])),
            'execution_cycles_count': len(self.data.get('execution_cycles', [])),
            'has_critical_path_analysis': bool(self.data.get('critical_path_analysis')),
            'critical_chain_records_count': len(self.data.get('critical_chain_records', [])),
            'npv_records_count': len(self.data.get('npv_records', []))
        }
