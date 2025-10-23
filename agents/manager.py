"""
项目经理智能体
"""
from agents.base_agent import BaseAgent
from utils.llm_client import LLMClient
from database.shared_db import SharedDatabase
from typing import Dict, Tuple, List
import re
import json


class ManagerAgent(BaseAgent):
    """
    项目经理（Project Manager）
    
    职责：
    1. 与项目发起人沟通，制定项目章程
    2. 组织和参加会议
    3. 制定WBS和管理计划
    4. 跟踪项目进展
    5. 进行挣值分析
    6. 进行关键路径分析（新增）
    7. 进行关键链计划分析（新增）
    8. 进行净现值分析（新增）
    """
    
    def __init__(self, llm_client: LLMClient, shared_db: SharedDatabase,
                 system_prompt: str):
        super().__init__(
            role_name="项目经理",
            system_prompt=system_prompt,
            llm_client=llm_client,
            shared_db=shared_db
        )
    
    def draft_project_charter(self, requirements: str) -> str:
        """
        起草项目章程
        
        Args:
            requirements: 项目发起人的需求描述
            
        Returns:
            项目章程内容
        """
        prompt = f"""项目发起人提出了以下需求：

{requirements}

请作为项目经理，起草项目章程。项目章程应包括：

1. **项目名称和背景**
2. **项目目标**
3. **项目范围概述**
4. **主要可交付成果**
5. **项目里程碑**
6. **初步预算估算**
7. **项目约束和假设**
8. **项目发起人和项目经理信息**

请按照专业的项目管理标准编写，内容详实（500-800字）。
"""
        
        response = self.think(prompt, temperature=0.7)
        return response
    
    def facilitate_kickoff_meeting(self, sponsor_input: str, 
                                   team_input: str) -> Dict[str, str]:
        """
        主持启动会议，形成三大约束
        
        Args:
            sponsor_input: 项目发起人的发言
            team_input: 团队成员的发言
            
        Returns:
            包含cost, scope, schedule的字典
        """
        charter = self.shared_db.data.get('project_charter', '')
        
        context = f"""
项目章程（部分）：
{charter[:300] if charter else '无'}...
"""
        
        prompt = f"""项目启动会议正在进行。

项目发起人发言：
{sponsor_input}

团队成员发言：
{team_input}

作为项目经理，请综合各方意见，明确定义项目的三大约束：

1. **成本约束 (Cost)**：预算是多少？包含哪些成本项？
2. **范围约束 (Scope)**：项目要做什么？不做什么？具体功能有哪些？
3. **进度约束 (Schedule)**：总工期多长？关键里程碑是什么？

请分别用100-150字详细描述每个约束。

格式要求：
【成本约束】
...

【范围约束】
...

【进度约束】
...
"""
        
        response = self.think(prompt, context=context, temperature=0.7)
        
        # 解析三大约束
        constraints = self._parse_constraints(response)
        return constraints
    
    def create_wbs(self) -> str:
        """
        创建工作分解结构（WBS）
        
        Returns:
            WBS内容
        """
        charter = self.shared_db.data.get('project_charter', '')
        constraints = self.shared_db.data.get('constraints', {})
        
        context = f"""
项目章程（部分）：
{charter[:300] if charter else '无'}...

项目约束：
- 成本：{constraints.get('cost', '未定义')}
- 范围：{constraints.get('scope', '未定义')}
- 时间：{constraints.get('schedule', '未定义')}
"""
        
        prompt = """请创建工作分解结构（WBS）。

WBS应该：
1. 按照项目生命周期划分（需求分析、设计、开发、测试、部署）
2. 每个阶段进一步分解为具体工作包
3. 标注每个工作包的负责人和预计工期
4. 使用树形结构清晰展示

请创建详细的WBS（400-600字），使用Markdown格式，层次分明。
"""
        
        response = self.think(prompt, context=context, temperature=0.7)
        return response
    
    def create_management_plans(self) -> Dict[str, str]:
        """
        创建三大管理计划
        
        Returns:
            包含cost_plan, scope_plan, schedule_plan的字典
        """
        wbs = self.shared_db.data.get('wbs', '')
        constraints = self.shared_db.data.get('constraints', {})
        
        plans = {}
        
        # 成本管理计划
        plans['cost'] = self._create_cost_plan(constraints.get('cost', ''), wbs)
        
        # 范围管理计划
        plans['scope'] = self._create_scope_plan(constraints.get('scope', ''), wbs)
        
        # 进度管理计划
        plans['schedule'] = self._create_schedule_plan(constraints.get('schedule', ''), wbs)
        
        return plans
    
    def perform_evm_analysis(self, cycle: int) -> Dict:
        """
        执行挣值分析
        
        Args:
            cycle: 当前循环次数
            
        Returns:
            EVM分析数据
        """
        # 获取项目约束
        constraints = self.shared_db.data.get('constraints', {})
        
        # 简化的EVM计算（实际项目中需要详细的工作包完成情况）
        # 这里使用模拟数据
        total_budget = 100000  # 假设总预算
        planned_completion = (cycle / 3.0) * 100  # 计划完成百分比
        
        context = f"""
当前是第{cycle}次执行控制循环。
项目约束：
- 成本：{constraints.get('cost', '未定义')}
- 范围：{constraints.get('scope', '未定义')}
- 时间：{constraints.get('schedule', '未定义')}

代码文件数：{len(self.shared_db.data.get('code_files', {}))}
"""
        
        prompt = f"""请进行挣值分析（EVM）。

假设：
- 总预算（BAC）：{total_budget}元
- 计划完成进度：{planned_completion:.1f}%
- 当前循环：{cycle}/3

请估算：
1. 计划值（PV）：按计划应该完成的工作价值
2. 挣值（EV）：实际已完成的工作价值
3. 实际成本（AC）：实际花费的成本

并计算：
- 成本偏差（CV = EV - AC）
- 进度偏差（SV = EV - PV）
- 成本绩效指数（CPI = EV / AC）
- 进度绩效指数（SPI = EV / PV）

然后给出分析结论和建议。

请按以下格式回答：
【PV】数值
【EV】数值
【AC】数值
【分析】分析内容...
"""
        
        response = self.think(prompt, context=context, temperature=0.7)
        
        # 解析EVM数据
        evm_data = self._parse_evm(response, total_budget, planned_completion)
        
        return evm_data
    
    def update_plans(self, cycle: int, feedback: str) -> Dict[str, str]:
        """
        根据反馈更新管理计划
        
        Args:
            cycle: 当前循环次数
            feedback: 项目发起人的反馈
            
        Returns:
            更新后的计划
        """
        current_plans = self.shared_db.get_latest_plans()
        
        context = f"""
当前循环：{cycle}/3

项目发起人反馈：
{feedback}

当前计划（部分）：
WBS: {str(current_plans['wbs'])[:200] if current_plans['wbs'] else '无'}...
"""
        
        prompt = """根据项目发起人的反馈，请更新管理计划。

重点考虑：
1. 哪些地方需要调整？
2. 如何应对反馈中提出的问题？
3. 资源和时间如何重新分配？

请简要说明更新内容（200-300字）。
"""
        
        response = self.think(prompt, context=context, temperature=0.7)
        
        return {
            'update_summary': response,
            'cycle': cycle
        }
    
    def _parse_constraints(self, response: str) -> Dict[str, str]:
        """解析三大约束"""
        constraints = {}
        
        # 简单的文本解析
        parts = response.split('【')
        for part in parts:
            if '成本约束】' in part:
                constraints['cost'] = part.split('】')[1].split('【')[0].strip()
            elif '范围约束】' in part:
                constraints['scope'] = part.split('】')[1].split('【')[0].strip()
            elif '进度约束】' in part:
                constraints['schedule'] = part.split('】')[1].strip()
        
        return constraints
    
    def _create_cost_plan(self, cost_constraint: str, wbs: str) -> str:
        """创建成本管理计划"""
        prompt = f"""请创建成本管理计划。

成本约束：
{cost_constraint}

WBS（部分）：
{wbs[:300] if wbs else '无'}...

成本管理计划应包括：
1. 成本估算方法
2. 预算分配
3. 成本基准
4. 成本控制方法
5. EVM应用说明

请详细编写（300-400字）。
"""
        
        response = self.think(prompt, temperature=0.7, max_tokens=1500)
        return response
    
    def _create_scope_plan(self, scope_constraint: str, wbs: str) -> str:
        """创建范围管理计划"""
        prompt = f"""请创建范围管理计划。

范围约束：
{scope_constraint}

WBS（部分）：
{wbs[:300] if wbs else '无'}...

范围管理计划应包括：
1. 范围定义方法
2. 需求管理流程
3. 范围变更控制流程
4. 范围验证方法
5. 可交付成果验收标准

请详细编写（300-400字）。
"""
        
        response = self.think(prompt, temperature=0.7, max_tokens=1500)
        return response
    
    def _create_schedule_plan(self, schedule_constraint: str, wbs: str) -> str:
        """创建进度管理计划"""
        prompt = f"""请创建进度管理计划。

进度约束：
{schedule_constraint}

WBS（部分）：
{wbs[:300] if wbs else '无'}...

进度管理计划应包括：
1. 活动排序方法
2. 资源估算
3. 进度计划制定
4. 进度控制方法
5. 关键路径管理

请详细编写（300-400字）。
"""
        
        response = self.think(prompt, temperature=0.7, max_tokens=1500)
        return response
    
    def _parse_evm(self, response: str, total_budget: float, 
                   planned_pct: float) -> Dict:
        """解析EVM数据"""
        import re
        
        evm_data = {
            'pv': total_budget * (planned_pct / 100),
            'ev': 0,
            'ac': 0,
            'analysis': response
        }
        
        # 尝试从响应中提取数值
        pv_match = re.search(r'【PV】\s*([\d.]+)', response)
        ev_match = re.search(r'【EV】\s*([\d.]+)', response)
        ac_match = re.search(r'【AC】\s*([\d.]+)', response)
        
        if pv_match:
            evm_data['pv'] = float(pv_match.group(1))
        if ev_match:
            evm_data['ev'] = float(ev_match.group(1))
        if ac_match:
            evm_data['ac'] = float(ac_match.group(1))
        
        # 计算派生指标
        evm_data['cv'] = evm_data['ev'] - evm_data['ac']
        evm_data['sv'] = evm_data['ev'] - evm_data['pv']
        evm_data['cpi'] = evm_data['ev'] / evm_data['ac'] if evm_data['ac'] > 0 else 0
        evm_data['spi'] = evm_data['ev'] / evm_data['pv'] if evm_data['pv'] > 0 else 0
        
        return evm_data

    def perform_critical_path_analysis(self) -> Dict:
        """
        执行关键路径分析（CPM）
        
        Returns:
            关键路径分析数据
        """
        wbs = self.shared_db.data.get('wbs', '')
        constraints = self.shared_db.data.get('constraints', {})
        
        context = f"""
WBS内容：
{wbs[:500] if wbs else '无'}...

项目约束：
- 成本：{constraints.get('cost', '未定义')}
- 范围：{constraints.get('scope', '未定义')}
- 时间：{constraints.get('schedule', '未定义')}
"""
        
        prompt = """请进行关键路径分析（Critical Path Method, CPM）。

基于WBS，请：
1. 识别项目中的主要活动和任务
2. 确定活动之间的依赖关系
3. 估算每个活动的持续时间
4. 计算最早开始时间（ES）和最早完成时间（EF）
5. 计算最晚开始时间（LS）和最晚完成时间（LF）
6. 计算总浮动时间（TF）
7. 识别关键路径（浮动时间为0的活动序列）

请按以下格式输出：

【活动列表】
活动A: 需求分析 (持续时间: 5天)
活动B: 系统设计 (持续时间: 8天, 前置活动: A)
...

【关键路径】
A → B → D → F → H (总工期: 35天)

【关键活动分析】
- 活动A: ES=0, EF=5, LS=0, LF=5, TF=0 (关键活动)
- 活动B: ES=5, EF=13, LS=5, LF=13, TF=0 (关键活动)
...

【风险分析】
关键路径上的风险点和建议...
"""
        
        response = self.think(prompt, context=context, temperature=0.7)
        
        # 解析关键路径数据
        cpm_data = self._parse_critical_path(response)
        
        return cpm_data
    
    def perform_critical_chain_analysis(self, cycle: int) -> Dict:
        """
        执行关键链计划分析（CCPM）
        
        Args:
            cycle: 当前循环次数
            
        Returns:
            关键链分析数据
        """
        # 获取关键路径分析结果
        cpm_data = self.shared_db.data.get('critical_path_analysis', {})
        constraints = self.shared_db.data.get('constraints', {})
        
        context = f"""
当前循环：{cycle}/3

关键路径分析结果：
{str(cpm_data)[:300] if cpm_data else '无'}...

项目约束：
- 成本：{constraints.get('cost', '未定义')}
- 范围：{constraints.get('scope', '未定义')}
- 时间：{constraints.get('schedule', '未定义')}
"""
        
        prompt = f"""请进行关键链计划分析（Critical Chain Project Management, CCPM）。

关键链方法考虑资源约束和不确定性，请分析：

1. **资源约束识别**
   - 识别项目中的关键资源（人员、设备等）
   - 分析资源冲突和瓶颈

2. **缓冲区设置**
   - 项目缓冲区：保护项目完成日期
   - 汇入缓冲区：保护关键链不受非关键链延误影响
   - 资源缓冲区：确保关键资源及时可用

3. **关键链识别**
   - 考虑资源约束后的最长路径
   - 与传统关键路径的差异分析

4. **进度监控建议**
   - 缓冲区消耗监控方法
   - 预警机制设计

请按以下格式输出：

【资源约束分析】
- 关键资源：开发人员（2人）、测试环境（1套）
- 资源冲突：...

【关键链路径】
A → B → C → D (考虑资源约束后的关键链)

【缓冲区设计】
- 项目缓冲区：5天
- 汇入缓冲区：2-3天
- 资源缓冲区：1天

【监控建议】
缓冲区消耗监控和预警机制...
"""
        
        response = self.think(prompt, context=context, temperature=0.7)
        
        # 解析关键链数据
        ccpm_data = self._parse_critical_chain(response)
        ccpm_data['cycle'] = cycle
        
        return ccpm_data
    
    def perform_npv_analysis(self, cycle: int) -> Dict:
        """
        执行净现值分析（NPV）
        
        Args:
            cycle: 当前循环次数
            
        Returns:
            NPV分析数据
        """
        constraints = self.shared_db.data.get('constraints', {})
        evm_records = self.shared_db.data.get('evm_records', [])
        
        # 获取最新的EVM数据
        latest_evm = evm_records[-1] if evm_records else {}
        
        context = f"""
当前循环：{cycle}/3

项目约束：
- 成本：{constraints.get('cost', '未定义')}
- 范围：{constraints.get('scope', '未定义')}
- 时间：{constraints.get('schedule', '未定义')}

最新EVM数据：
- PV: {latest_evm.get('pv', 0)}
- EV: {latest_evm.get('ev', 0)}
- AC: {latest_evm.get('ac', 0)}
- CPI: {latest_evm.get('cpi', 0)}
"""
        
        prompt = f"""请进行净现值分析（Net Present Value, NPV）。

基于项目的成本效益，请分析：

1. **现金流预测**
   - 项目投资成本（分期投入）
   - 预期收益（项目完成后的收益流）
   - 运营成本

2. **NPV计算**
   - 假设贴现率：8-12%
   - 计算各期现金流的现值
   - 计算净现值NPV

3. **敏感性分析**
   - 贴现率变化对NPV的影响
   - 收益延迟对NPV的影响
   - 成本超支对NPV的影响

4. **投资决策建议**
   - NPV为正/负的含义
   - 项目财务可行性评估
   - 风险控制建议

请按以下格式输出：

【现金流预测】
年份0: -50万（初始投资）
年份1: -30万（开发成本）
年份2: +20万（收益开始）
年份3: +40万
年份4: +40万
年份5: +30万

【NPV计算】（贴现率10%）
NPV = -50 + (-30/1.1) + (20/1.1²) + (40/1.1³) + (40/1.1⁴) + (30/1.1⁵)
NPV = XX万元

【敏感性分析】
- 贴现率8%: NPV = XX万
- 贴现率12%: NPV = XX万
- 收益延迟1年: NPV = XX万

【投资建议】
基于NPV分析的项目可行性评估...
"""
        
        response = self.think(prompt, context=context, temperature=0.7)
        
        # 解析NPV数据
        npv_data = self._parse_npv_analysis(response)
        npv_data['cycle'] = cycle
        
        return npv_data

    def _parse_critical_path(self, response: str) -> Dict:
        """解析关键路径分析结果"""
        cpm_data = {
            'activities': [],
            'critical_path': '',
            'total_duration': 0,
            'critical_activities': [],
            'analysis': response
        }
        
        # 尝试提取关键路径
        critical_path_match = re.search(r'【关键路径】\s*([^【]*)', response)
        if critical_path_match:
            path_text = critical_path_match.group(1).strip()
            # 提取路径和总工期
            duration_match = re.search(r'总工期[：:]\s*(\d+)', path_text)
            if duration_match:
                cpm_data['total_duration'] = int(duration_match.group(1))
            
            # 提取路径序列
            path_match = re.search(r'([A-Z](?:\s*→\s*[A-Z])*)', path_text)
            if path_match:
                cpm_data['critical_path'] = path_match.group(1)
        
        # 提取活动列表
        activities_match = re.search(r'【活动列表】\s*([^【]*)', response)
        if activities_match:
            activities_text = activities_match.group(1)
            # 简单解析活动信息
            for line in activities_text.split('\n'):
                if '活动' in line and ':' in line:
                    cpm_data['activities'].append(line.strip())
        
        return cpm_data
    
    def _parse_critical_chain(self, response: str) -> Dict:
        """解析关键链分析结果"""
        ccpm_data = {
            'resource_constraints': '',
            'critical_chain': '',
            'buffers': {},
            'monitoring_plan': '',
            'analysis': response
        }
        
        # 提取资源约束
        resource_match = re.search(r'【资源约束分析】\s*([^【]*)', response)
        if resource_match:
            ccpm_data['resource_constraints'] = resource_match.group(1).strip()
        
        # 提取关键链路径
        chain_match = re.search(r'【关键链路径】\s*([^【]*)', response)
        if chain_match:
            ccpm_data['critical_chain'] = chain_match.group(1).strip()
        
        # 提取缓冲区设计
        buffer_match = re.search(r'【缓冲区设计】\s*([^【]*)', response)
        if buffer_match:
            buffer_text = buffer_match.group(1).strip()
            # 解析缓冲区信息
            for line in buffer_text.split('\n'):
                if '项目缓冲区' in line:
                    days_match = re.search(r'(\d+)天', line)
                    if days_match:
                        ccpm_data['buffers']['project_buffer'] = int(days_match.group(1))
                elif '汇入缓冲区' in line:
                    days_match = re.search(r'(\d+)', line)
                    if days_match:
                        ccpm_data['buffers']['feeding_buffer'] = int(days_match.group(1))
                elif '资源缓冲区' in line:
                    days_match = re.search(r'(\d+)天', line)
                    if days_match:
                        ccpm_data['buffers']['resource_buffer'] = int(days_match.group(1))
        
        # 提取监控建议
        monitoring_match = re.search(r'【监控建议】\s*([^【]*)', response)
        if monitoring_match:
            ccpm_data['monitoring_plan'] = monitoring_match.group(1).strip()
        
        return ccpm_data
    
    def _parse_npv_analysis(self, response: str) -> Dict:
        """解析NPV分析结果"""
        npv_data = {
            'cash_flows': [],
            'npv_value': 0,
            'discount_rate': 0.1,
            'sensitivity_analysis': {},
            'investment_recommendation': '',
            'analysis': response
        }
        
        # 提取NPV值
        npv_match = re.search(r'NPV\s*=\s*([+-]?\d+(?:\.\d+)?)', response)
        if npv_match:
            npv_data['npv_value'] = float(npv_match.group(1))
        
        # 提取现金流
        cashflow_match = re.search(r'【现金流预测】\s*([^【]*)', response)
        if cashflow_match:
            cashflow_text = cashflow_match.group(1)
            for line in cashflow_text.split('\n'):
                if '年份' in line and ':' in line:
                    # 解析现金流数据为字典格式
                    year_match = re.search(r'年份(\d+)', line)
                    amount_match = re.search(r'([+-]?\d+(?:\.\d+)?)万', line)
                    
                    if year_match and amount_match:
                        year = int(year_match.group(1))
                        amount = float(amount_match.group(1))
                        
                        cash_flow = {
                            'year': year,
                            'inflow': max(0, amount),
                            'outflow': abs(min(0, amount)),
                            'net_flow': amount,
                            'discount_factor': 1 / ((1 + npv_data['discount_rate']) ** year),
                            'present_value': amount / ((1 + npv_data['discount_rate']) ** year)
                        }
                        npv_data['cash_flows'].append(cash_flow)
        
        # 提取敏感性分析
        sensitivity_match = re.search(r'【敏感性分析】\s*([^【]*)', response)
        if sensitivity_match:
            sensitivity_text = sensitivity_match.group(1)
            # 解析不同情况下的NPV
            for line in sensitivity_text.split('\n'):
                if 'NPV' in line and '=' in line:
                    if '贴现率8%' in line:
                        value_match = re.search(r'NPV\s*=\s*([+-]?\d+(?:\.\d+)?)', line)
                        if value_match:
                            npv_data['sensitivity_analysis']['discount_8%'] = float(value_match.group(1))
                    elif '贴现率12%' in line:
                        value_match = re.search(r'NPV\s*=\s*([+-]?\d+(?:\.\d+)?)', line)
                        if value_match:
                            npv_data['sensitivity_analysis']['discount_12%'] = float(value_match.group(1))
        
        # 提取投资建议
        recommendation_match = re.search(r'【投资建议】\s*([^【]*)', response)
        if recommendation_match:
            npv_data['investment_recommendation'] = recommendation_match.group(1).strip()
        
        return npv_data
