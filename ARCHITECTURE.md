# 系统架构文档

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      工作流引擎（Workflow Engine）              │
│                   控制项目生命周期的六个阶段                      │
└───────────────┬─────────────────────────────┬─────────────────┘
                │                             │
    ┌───────────▼──────────┐      ┌──────────▼─────────────┐
    │   智能体系统（Agents）  │      │  共享数据库（SharedDB）  │
    │  - 项目发起人          │◄────►│  - 项目信息              │
    │  - 项目经理            │      │  - 文档记录              │
    │  - 项目组成员          │      │  - 讨论历史              │
    └───────────┬──────────┘      └──────────┬─────────────┘
                │                             │
    ┌───────────▼──────────┐      ┌──────────▼─────────────┐
    │  LLM客户端             │      │  文档生成器               │
    │  - API调用            │      │  - Markdown文档          │
    │  - 重试机制            │      │  - 代码文件              │
    └───────────────────────┘      └────────────────────────┘
```

## 核心模块

### 1. 智能体模块（agents/）

#### BaseAgent（基类）

所有智能体的基础类，提供：

- **记忆管理**
  - 短期记忆：conversation_history（对话历史）
  - 工作记忆：working_memory（任务相关临时信息）
  - 长期记忆：通过shared_db访问

- **思考机制**
  - think()：核心方法，调用LLM生成响应
  - 自动管理对话上下文
  - 支持额外上下文注入

- **通信机制**
  - communicate_with()：与其他智能体通信
  - 自动记录到共享数据库

#### SponsorAgent（项目发起人）

职责：
- `state_requirements()` - 陈述项目需求
- `participate_in_kickoff()` - 参与启动会议
- `review_product()` - 评审产品，决定是否接受
- `final_acceptance()` - 最终验收

#### ManagerAgent（项目经理）

职责：
- `draft_project_charter()` - 起草项目章程
- `facilitate_kickoff_meeting()` - 主持启动会议，确定三大约束
- `create_wbs()` - 创建工作分解结构
- `create_management_plans()` - 创建三大管理计划
- `perform_evm_analysis()` - 执行挣值分析
- `update_plans()` - 根据反馈更新计划

#### TeamMemberAgent（项目组成员）

职责：
- `participate_in_kickoff()` - 参与启动会议，提供技术意见
- `develop_code()` - 开发代码
- `report_progress()` - 报告进展
- `discuss_with_sponsor()` - 与发起人讨论改进

### 2. 数据库模块（database/）

#### SharedDatabase

集中式数据存储，包含：

**数据结构**：
```python
{
    'project_info': {...},           # 项目基本信息
    'project_charter': str,          # 项目章程
    'constraints': {                 # 三大约束
        'cost': str,
        'scope': str,
        'schedule': str
    },
    'wbs': str,                      # 工作分解结构
    'management_plans': {            # 管理计划
        'cost_plan': str,
        'scope_plan': str,
        'schedule_plan': str
    },
    'meeting_records': [...],        # 会议记录
    'discussions': [...],            # 讨论记录
    'code_files': {...},             # 代码文件
    'documents': {...},              # 文档
    'evm_records': [...],            # 挣值分析记录
    'execution_cycles': [...]        # 执行控制循环记录
}
```

**核心方法**：
- 保存类：save_*(), add_*()
- 查询类：get_*()
- 导出类：export_to_json()

### 3. 工作流引擎（workflow/）

#### WorkflowEngine

控制项目的六个阶段：

```python
def run():
    phase_pre_initiation()      # 阶段1：预启动
    phase_initiation()          # 阶段2：启动
    phase_planning()            # 阶段3：计划
    
    # 阶段4&5：执行与控制（循环）
    for cycle in range(1, MAX_CYCLES + 1):
        phase_execution(cycle)
        phase_control(cycle)
        if get_sponsor_feedback(cycle):
            break
    
    phase_closure()             # 阶段6：结束
```

**阶段详情**：

| 阶段 | 主要活动 | 参与者 | 交付物 |
|-----|---------|-------|--------|
| 预启动 | 需求陈述、起草章程 | 发起人、经理 | 项目章程 |
| 启动 | 启动会议、确定约束 | 全体 | 会议记录、三大约束 |
| 计划 | 创建WBS、管理计划 | 经理 | WBS、管理计划 |
| 执行 | 开发代码、报告进展 | 成员、经理 | 代码、进展报告 |
| 控制 | EVM分析、更新计划 | 经理 | EVM报告、更新计划 |
| 结束 | 整理交付物、验收 | 全体 | 总结报告、全部交付物 |

### 4. 工具模块（utils/）

#### LLMClient

封装对外部大模型的调用：

```python
class LLMClient:
    def chat(messages, temperature, max_tokens) -> str
    def chat_with_retry(messages, max_retries) -> str
```

特性：
- 使用OpenAI兼容接口
- 支持重试机制
- 错误处理

#### DocumentGenerator

生成标准化项目文档：

```python
class DocumentGenerator:
    def generate_project_charter(content) -> str
    def generate_meeting_minutes(...) -> str
    def generate_wbs(content) -> str
    def generate_management_plan(...) -> str
    def generate_evm_report(...) -> str
    def generate_final_summary(...) -> str
    def save_code_file(...) -> None
```

## 数据流

### 1. 预启动阶段数据流

```
项目创意 → SponsorAgent.state_requirements()
         → 需求描述
         → ManagerAgent.draft_project_charter()
         → 项目章程
         → SharedDB.save_project_charter()
         → DocumentGenerator.generate_project_charter()
```

### 2. 启动阶段数据流

```
项目章程 → SponsorAgent.participate_in_kickoff() → 发言1
         → TeamMemberAgent.participate_in_kickoff() → 发言2
         → ManagerAgent.facilitate_kickoff_meeting() → 三大约束
         → SharedDB.save_constraints()
         → DocumentGenerator.generate_meeting_minutes()
```

### 3. 执行-控制循环数据流

```
循环开始 → TeamMemberAgent.develop_code()
         → 代码文件
         → SharedDB.save_code_file()
         → ManagerAgent.perform_evm_analysis()
         → EVM数据
         → SharedDB.add_evm_record()
         → SponsorAgent.review_product()
         → (接受/拒绝)
         → 如果拒绝 → 下一循环
         → 如果接受 → 结束阶段
```

## 记忆系统

### 三层记忆架构

```
┌──────────────────────────────────────┐
│          短期记忆（Short-term）         │
│     conversation_history (最近10轮)    │
│     - 对话上下文                        │
│     - 自动管理                          │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│          工作记忆（Working）            │
│     working_memory (字典)              │
│     - 当前任务相关信息                   │
│     - 临时数据                          │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│          长期记忆（Long-term）          │
│     shared_db (共享数据库)              │
│     - 项目历史数据                       │
│     - 持久化存储                        │
└──────────────────────────────────────┘
```

### 记忆管理策略

1. **短期记忆**
   - 只保留最近10轮对话
   - 每次think()自动更新
   - 提供对话上下文

2. **工作记忆**
   - 存储当前任务的临时数据
   - 可手动添加/查询/清空
   - 跨方法调用共享

3. **长期记忆**
   - 通过shared_db访问
   - 查询相关讨论：get_discussions_for_agent()
   - 查询项目数据：get_project_summary()等

## 通信机制

### 智能体间通信

```python
# 发送消息
agent1.communicate_with(
    other_agent_name="项目经理",
    topic="进展报告",
    message="第1次循环已完成..."
)
↓
记录到SharedDB.discussions
↓
# 接收方可查询
agent2.get_relevant_discussions()
```

### 通信记录格式

```python
{
    'timestamp': '2025-01-14T18:10:00',
    'from': '项目组成员',
    'to': '项目经理',
    'topic': '进展报告',
    'content': '...'
}
```

## 配置系统

### config.py

```python
# LLM配置
LLM_CONFIG = {
    'base_url': str,
    'api_key': str,
    'model': str
}

# 阶段定义
PHASES = {
    'PRE_INITIATION': '预启动',
    'INITIATION': '启动',
    ...
}

# 最大循环次数
MAX_EXECUTION_CYCLES = 3

# Agent提示词
AGENT_PROMPTS = {
    'SPONSOR': str,
    'MANAGER': str,
    'TEAM_MEMBER': str
}
```

## 扩展点

### 1. 添加新角色

```python
# 1. 创建新的Agent类
class NewAgent(BaseAgent):
    def __init__(self, ...):
        super().__init__(...)
    
    def custom_method(self):
        ...

# 2. 在config.py添加提示词
AGENT_PROMPTS['NEW_ROLE'] = "..."

# 3. 在WorkflowEngine中初始化
self.new_agent = NewAgent(...)

# 4. 在相应阶段调用
def phase_xxx(self):
    result = self.new_agent.custom_method()
```

### 2. 添加新阶段

```python
# 在WorkflowEngine中添加方法
def phase_custom(self):
    print(f"阶段X: 自定义阶段")
    # 实现阶段逻辑
    ...

# 在run()中调用
def run(self):
    ...
    self.phase_custom()
    ...
```

### 3. 自定义文档格式

```python
# 在DocumentGenerator中添加方法
def generate_custom_doc(self, ...):
    doc = f"""
    # 自定义文档
    ...
    """
    self.save_document('custom_doc.md', doc)
    return doc
```

## 性能优化

### 1. LLM调用优化

- 批量请求（如果API支持）
- 缓存常见响应
- 调整max_tokens减少等待时间

### 2. 记忆管理优化

- 限制对话历史长度
- 定期清理工作记忆
- 按需加载长期记忆

### 3. 并发优化

- 独立任务可并行执行
- 使用异步API调用
- 多项目模拟可并行

## 错误处理

### 1. API调用失败

```python
try:
    response = llm_client.chat(messages)
except Exception as e:
    # 使用模拟响应
    response = f"[模拟响应] ..."
```

### 2. 数据解析失败

```python
try:
    data = parse_response(response)
except:
    # 使用默认数据
    data = generate_default_data()
```

### 3. 文件操作失败

```python
try:
    save_file(path, content)
except:
    # 记录错误，继续执行
    log_error(...)
```

## 测试策略

### 1. 单元测试

- 测试各个Agent的方法
- 测试SharedDB的数据操作
- 测试DocumentGenerator的文档生成

### 2. 集成测试

- 测试WorkflowEngine的完整流程
- 测试智能体间的通信
- 测试数据流的完整性

### 3. 系统测试

- test_simple.py：组件测试
- main.py：完整流程测试
- 多次运行验证稳定性

---

## 设计原则

1. **模块化**：每个模块职责单一，便于维护
2. **可扩展**：易于添加新角色、新阶段
3. **容错性**：API失败不影响整体流程
4. **可追溯**：所有操作记录到数据库
5. **标准化**：遵循项目管理规范

## 技术栈

- **语言**：Python 3.8+
- **LLM接口**：OpenAI兼容API
- **数据格式**：JSON、Markdown
- **依赖库**：openai, requests, python-dateutil
