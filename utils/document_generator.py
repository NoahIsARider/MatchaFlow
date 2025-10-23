"""
文档生成器：生成各种项目文档
"""
import os
from datetime import datetime
from typing import Dict, List


class DocumentGenerator:
    """文档生成器，负责生成和保存各类项目文档"""
    
    def __init__(self, output_dir: str):
        """
        初始化文档生成器
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_document(self, filename: str, content: str):
        """
        保存文档到文件
        
        Args:
            filename: 文件名
            content: 文档内容
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[文档生成] 已保存：{filename}")
        
    def generate_project_charter(self, content: str) -> str:
        """生成项目章程文档"""
        doc = f"""# 项目章程 (Project Charter)

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}

---

**批准签字：**
- 项目发起人：____________
- 项目经理：____________

"""
        self.save_document('项目章程.md', doc)
        return doc
    
    def generate_meeting_minutes(self, phase: str, participants: List[str], 
                                content: str) -> str:
        """生成会议记录"""
        doc = f"""# 会议记录 - {phase}阶段

**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**参会人员：** {', '.join(participants)}

---

## 会议内容

{content}

---

**记录人：** 项目经理

"""
        filename = f'会议记录_{phase}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        self.save_document(filename, doc)
        return doc
    
    def generate_wbs(self, content: str) -> str:
        """生成WBS文档"""
        doc = f"""# 工作分解结构 (WBS - Work Breakdown Structure)

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}

---

"""
        self.save_document('WBS.md', doc)
        return doc
    
    def generate_management_plan(self, plan_type: str, content: str) -> str:
        """生成管理计划"""
        type_names = {
            'cost': '成本管理计划',
            'scope': '范围管理计划',
            'schedule': '进度管理计划'
        }
        
        doc = f"""# {type_names.get(plan_type, '管理计划')}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}

---

"""
        filename = f'{type_names.get(plan_type, "管理计划")}.md'
        self.save_document(filename, doc)
        return doc
    
    def generate_evm_report(self, cycle: int, evm_data: Dict) -> str:
        """生成挣值分析报告"""
        doc = f"""# 挣值分析报告 - 循环 {cycle}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 关键指标

| 指标 | 值 |
|------|-----|
| 计划值 (PV) | {evm_data.get('pv', 0):.2f} |
| 挣值 (EV) | {evm_data.get('ev', 0):.2f} |
| 实际成本 (AC) | {evm_data.get('ac', 0):.2f} |
| 成本偏差 (CV) | {evm_data.get('cv', 0):.2f} |
| 进度偏差 (SV) | {evm_data.get('sv', 0):.2f} |
| 成本绩效指数 (CPI) | {evm_data.get('cpi', 0):.2f} |
| 进度绩效指数 (SPI) | {evm_data.get('spi', 0):.2f} |

## 分析结果

{evm_data.get('analysis', '无分析结果')}

---

"""
        filename = f'EVM报告_循环{cycle}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        self.save_document(filename, doc)
        return doc
    
    def generate_critical_path_report(self, cpm_data: Dict) -> str:
        """生成关键路径分析报告"""
        doc = f"""# 关键路径分析报告 (CPM)

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 关键路径信息

**关键路径：** {cpm_data.get('critical_path', '未识别')}

**项目总工期：** {cpm_data.get('total_duration', 0)} 天

**关键活动数量：** {len(cpm_data.get('activities', []))}

---

## 关键活动详情

"""
        
        # 添加关键活动表格
        activities = cpm_data.get('activities', [])
        if activities:
            doc += """
| 活动名称 | 描述 |
|----------|------|
"""
            for activity in activities:
                if isinstance(activity, dict):
                    doc += f"| {activity.get('name', '')} | {activity.get('duration', 0)} | {activity.get('es', 0)} | {activity.get('ef', 0)} | {activity.get('ls', 0)} | {activity.get('lf', 0)} | {activity.get('total_float', 0)} |\n"
                else:
                    # 处理字符串格式的活动信息
                    doc += f"| {str(activity)} | - |\n"
        
        doc += f"""

---

## 分析结论

{cpm_data.get('analysis', '无分析结果')}

---

## 建议

{cpm_data.get('recommendations', '无建议')}

---

"""
        filename = f'关键路径分析报告_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        self.save_document(filename, doc)
        return doc
    
    def generate_critical_chain_report(self, cycle: int, ccpm_data: Dict) -> str:
        """生成关键链计划分析报告"""
        doc = f"""# 关键链计划分析报告 (CCPM) - 循环 {cycle}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 关键链信息

**关键链：** {ccpm_data.get('critical_chain', '未识别')}

**项目缓冲区：** {ccpm_data.get('buffers', {}).get('project_buffer', 0)} 天

**输入缓冲区：** {ccpm_data.get('buffers', {}).get('feeding_buffer', 0)} 天

---

## 资源约束分析

{ccpm_data.get('resource_constraints', '无资源约束分析')}

---

## 缓冲区状态

"""
        
        # 添加缓冲区状态表格
        buffers = ccpm_data.get('buffer_status', [])
        if buffers:
            doc += """
| 缓冲区类型 | 总时间 | 已消耗 | 剩余时间 | 消耗率 | 状态 |
|------------|--------|--------|----------|--------|------|
"""
            for buffer in buffers:
                doc += f"| {buffer.get('type', '')} | {buffer.get('total', 0)} | {buffer.get('consumed', 0)} | {buffer.get('remaining', 0)} | {buffer.get('consumption_rate', 0):.1f}% | {buffer.get('status', '')} |\n"
        
        doc += f"""

---

## 分析结论

{ccpm_data.get('analysis', '无分析结果')}

---

## 行动建议

{ccpm_data.get('action_recommendations', '无行动建议')}

---

"""
        filename = f'关键链分析报告_循环{cycle}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        self.save_document(filename, doc)
        return doc
    
    def generate_npv_report(self, cycle: int, npv_data: Dict) -> str:
        """生成净现值分析报告"""
        doc = f"""# 净现值分析报告 (NPV) - 循环 {cycle}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 财务指标

**净现值 (NPV)：** {npv_data.get('npv_value', 0):.2f} 万元

**贴现率：** {npv_data.get('discount_rate', 0.1)*100:.1f}%

**投资回收期：** {npv_data.get('payback_period', 0):.1f} 年

**内部收益率 (IRR)：** {npv_data.get('irr', 0)*100:.1f}%

---

## 现金流分析

"""
        
        # 添加现金流表格
        cash_flows = npv_data.get('cash_flows', [])
        if cash_flows:
            doc += """
| 年份 | 现金流入 | 现金流出 | 净现金流 | 折现因子 | 现值 |
|------|----------|----------|----------|----------|------|
"""
            for i, cf in enumerate(cash_flows):
                doc += f"| {i} | {cf.get('inflow', 0):.2f} | {cf.get('outflow', 0):.2f} | {cf.get('net_flow', 0):.2f} | {cf.get('discount_factor', 0):.4f} | {cf.get('present_value', 0):.2f} |\n"
        
        doc += f"""

---

## 敏感性分析

{npv_data.get('sensitivity_analysis', '无敏感性分析')}

---

## 投资建议

{npv_data.get('investment_recommendation', '无投资建议')}

---

## 风险评估

{npv_data.get('risk_assessment', '无风险评估')}

---

"""
        filename = f'NPV分析报告_循环{cycle}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        self.save_document(filename, doc)
        return doc
    
    def generate_final_summary(self, db_data: Dict, project_code: str = None) -> str:
        """生成项目总结文档"""
        doc = f"""# 项目总结报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 项目概况

**项目代号：** {project_code or '未知'}

**创建时间：** {datetime.now().strftime('%Y-%m-%d')}

---

## 项目约束

- **成本约束：** {db_data['constraints']['cost']}
- **范围约束：** {db_data['constraints']['scope']}
- **进度约束：** {db_data['constraints']['schedule']}

---

## 项目执行情况

**执行循环次数：** {len(db_data['execution_cycles'])}

**代码文件数：** {len(db_data['code_files'])}

**生成文档数：** {len(db_data['documents'])}

**会议记录数：** {len(db_data['meeting_records'])}

**讨论记录数：** {len(db_data['discussions'])}

---

## 挣值分析总结

"""
        # 添加所有EVM记录
        if db_data['evm_records']:
            for evm in db_data['evm_records']:
                doc += f"""
### 循环 {evm['cycle']}

- CPI: {evm['cpi']:.2f} (成本绩效{'良好' if evm['cpi'] >= 1 else '需改进'})
- SPI: {evm['spi']:.2f} (进度绩效{'良好' if evm['spi'] >= 1 else '需改进'})
- 成本偏差: {evm['cv']:.2f}
- 进度偏差: {evm['sv']:.2f}

"""
        
        doc += f"""
---

## 项目成果

本项目完成了以下交付物：

"""
        
        # 列出代码文件
        if db_data['code_files']:
            doc += "\n### 代码文件\n\n"
            for filename in db_data['code_files'].keys():
                doc += f"- {filename}\n"
        
        # 列出文档
        if db_data['documents']:
            doc += "\n### 项目文档\n\n"
            for docname in db_data['documents'].keys():
                doc += f"- {docname}\n"
        
        doc += """
---

## 经验教训

本项目成功模拟了软件项目管理的完整生命周期，包括预启动、启动、计划、执行、控制和结束六个阶段。
通过多智能体协作，完成了项目章程制定、WBS分解、三大管理计划制定、挣值分析等关键项目管理活动。

---

**项目经理签字：** ____________

**项目发起人签字：** ____________

**日期：** {datetime.now().strftime('%Y-%m-%d')}

"""
        
        self.save_document('项目总结报告.md', doc)
        return doc
    
    def save_code_file(self, filename: str, code_content: str):
        """保存代码文件"""
        try:
            # 将路径分隔符替换为下划线，确保所有文件都保存在同一文件夹中
            safe_filename = filename.replace('/', '_').replace('\\', '_')
            filepath = os.path.join(self.output_dir, safe_filename)
            
            # 确保输出目录存在
            os.makedirs(self.output_dir, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code_content)
            print(f"[代码生成] 已保存：{safe_filename}")
        except Exception as e:
            print(f"[错误] 保存代码文件失败 {filename}: {str(e)}")
            # 尝试使用更安全的文件名
            try:
                safe_filename = f"generated_file_{datetime.now().strftime('%H%M%S')}.txt"
                filepath = os.path.join(self.output_dir, safe_filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# 原文件名: {filename}\n\n{code_content}")
                print(f"[代码生成] 已使用备用文件名保存：{safe_filename}")
            except Exception as backup_e:
                print(f"[错误] 备用保存方式也失败: {str(backup_e)}")
