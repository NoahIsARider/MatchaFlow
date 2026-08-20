<div align="center">

# 多智能体项目管理模拟系统

### 让 AI 智能体自主运行一个完整的软件项目 — 从立项到交付。

[English](README.md) · [测试报告](TEST_REPORT.md)

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/LLM-兼容任意%20OpenAI%20API-10A37F?logo=openai&logoColor=white" alt="LLM">
<img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
<img src="https://img.shields.io/badge/Tests-86%20passing-brightgreen" alt="Tests">

</div>

---

## 这是什么

**让 AI 智能体组成项目团队，自主完成一个软件项目的全生命周期。**

三个 LLM 驱动的智能体分别扮演**项目发起人**（定义需求、审批交付物）、**项目经理**（规划、协调、跟踪进度）和**项目组成员**（开发代码、汇报进展）。它们按照 PMI/PMBOK 方法论经历六个阶段 — 预启动、启动、计划、执行、监控、收尾 — 产出真实的项目交付物：项目章程、WBS、管理计划、代码、挣值分析报告、NPV 分析、关键路径/链分析、验收意见。

不是 PPT 演示，不是模拟数据。智能体真正地推理、协商、产出交付物、互相评审、根据反馈迭代，直到发起人验收通过。

## 工作原理

```
┌─────────────────────────────────────────────────────────────────┐
│                         工作流引擎                                │
│                                                                  │
│   阶段 1         阶段 2         阶段 3         阶段 4 & 5        │
│   ┌──────┐      ┌──────┐      ┌──────┐      ┌──────────┐      │
│   │预    │      │启    │      │计    │      │执行与     │      │
│   │启动  │─────>│动    │─────>│划    │─────>│控制      │──┐   │
│   └──────┘      └──────┘      └──────┘      └──────────┘  │   │
│        │                                      │  评审       │   │
│        │              阶段 6                    │  循环       │   │
│        │            ┌──────┐                   └───┘         │   │
│        └───────────>│收尾  │<────────────────────────────────┘   │
│                     └──────┘                                     │
└─────────────────────────────────────────────────────────────────┘

         ┌────────────┬──────────────┬────────────────┐
         │            │              │                 │
    ┌────▼───┐  ┌─────▼────┐  ┌─────▼──────┐
    │ 发起人  │  │ 项目经理  │  │  项目组成员  │
    │  Agent │  │  Agent   │  │   Agent    │
    └────────┘  └──────────┘  └────────────┘
    需求定义     规划与         代码开发
    与验收       协调           与进度汇报
```

每个阶段有明确的进入条件、角色交互定义和具体交付物。执行阶段以循环方式运行 — 成员开发、经理评审、发起人决策。如果被拒绝，循环带着反馈重新开始。

## 核心特性

- **三角色智能体系统** — 发起人、项目经理、组成员各有独立的职责定义、提示词模板和决策逻辑
- **六阶段项目生命周期** — 忠实遵循 PMI/PMBOK 方法论，从预启动到收尾
- **迭代执行循环** — 代码-评审-拒绝循环，基于反馈驱动改进，直到验收通过
- **九类交付物** — 项目章程、WBS、进度/成本/范围管理计划、会议记录、挣值报告、NPV 分析、关键路径/链分析、项目总结
- **兼容任意 OpenAI API** — 支持 OpenAI、DeepSeek、Ollama、vLLM 等任意兼容端点
- **共享知识库** — SQLite 共享数据库确保所有智能体基于一致的项目状态工作
- **完整审计追踪** — 每次会议、讨论、决策和交付物都有时间戳记录
- **优雅降级** — LLM 调用失败时生成兜底响应，模拟不中断

## 快速开始

### 环境要求

- Python 3.10+
- 任意 OpenAI 兼容 API（或本地 LLM 端点）

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/multi-agent-pm.git
cd multi-agent-pm

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置 LLM

编辑 `config.py`，设置你的 LLM 端点：

```python
LLM_CONFIG = {
    "base_url": "https://api.openai.com/v1",  # 或任意兼容端点
    "api_key": "sk-your-api-key",
    "model": "gpt-4o",
}
```

### 运行

```bash
# 指定项目需求
python main.py --project-idea "构建一个企业级智能知识库平台，支持 RAG 和向量检索"

# 交互模式 — 发起人智能体会向你提问
python main.py
```

模拟将自主运行全部六个阶段。输出保存在 `simulation/<项目代号>/` 目录下。

## 项目结构

```
.
├── agents/
│   ├── base_agent.py          # 基础智能体：LLM 集成 & 对话记忆
│   ├── sponsor.py             # 发起人：需求定义、启动会、评审与验收
│   ├── manager.py             # 项目经理：章程、WBS、计划、挣值、关键路径
│   └── team_member.py         # 组成员：代码开发与进度汇报
├── database/
│   └── shared_db.py           # 共享 SQLite 数据库
├── workflow/
│   └── engine.py              # 工作流引擎，驱动六阶段生命周期
├── utils/
│   ├── llm_client.py          # LLM API 客户端（重试 & 降级）
│   └── document_generator.py  # 结构化文档生成器
├── dao/                         # 🆕 DAO 治理模式（提案人/协调员/成员）
│   ├── dao_config.py             # DAO 阶段、角色、提示词、LLM 配置
│   ├── dao_agents.py             # ProposerAgent / GovernorAgent / MemberAgent
│   ├── dao_calibration.py        # OnChainGov 实证指标校准
│   ├── dao_engine.py             # DAO 工作流引擎（六阶段治理）
│   ├── dao_main.py               # DAO 模式 CLI 入口
│   └── simulation/               # DAO 输出目录（每次运行自动创建）
├── simulation/                # 输出目录（每次运行自动创建）
├── tests/
│   └── test_all.py            # 86 个单元 & 集成测试
├── config.py                  # LLM 配置、阶段定义、智能体提示词模板
├── main.py                    # CLI 入口
├── test_simple.py             # 快速冒烟测试
└── requirements.txt           # 依赖声明
```

## DAO 治理模式

MatchaFlow 同时支持 **DAO 去中心化治理模拟**——三个 LLM 智能体将治理提案完整跑过社区讨论、机制设计、执行与复盘。复用同一套引擎模式（六阶段、review-only 循环、验收机制），但换成治理语境。

**角色映射：**

| 项目管理模式 | DAO 模式 | 职责 |
|------------|----------|------|
| 发起人 | **提案人 Proposer** | 陈述提案、参与讨论、评审并验收执行结果 |
| 项目经理 | **协调员 Governor** | 起草提案书、主持讨论、设计治理机制、监控指标、编制复盘 |
| 项目组成员 | **社区成员 Member** | 参与讨论、执行治理行动（投票/委托/链上操作） |

**阶段映射：** 预启动→提案发起 · 启动→社区讨论 · 计划→治理设计 · 执行→提案执行（成员行动）· 控制→治理监控（参与度/集中度分析）· 结束→治理复盘（复盘报告+最终验收）。

**OnChainGov 校准：** 可通过 parquet 文件把 OnChainGov 实证指标（如 `snapshot_space_a_participation.parquet`）注入模拟——参与度低会降低成员参与意愿，集中度高会触发反集中设计（委托上限、二次方投票、防女巫）。用 `--no-calibration` 可跳过。

```bash
# 配置 LLM（环境变量，避免密钥入库）
export LLM_BASE_URL=https://api-inference.modelscope.cn/v1
export LLM_API_KEY=你的密钥
export LLM_MODEL=Qwen/Qwen3.8-27B

# 基础运行
python3 dao/dao_main.py --proposal-idea "引入委托投票机制，提升社区参与度"

# 接入 OnChainGov 实证指标校准
python3 dao/dao_main.py --proposal-idea "引入委托投票机制" \
    --calibration-path ../onchaingov/data/indicators/snapshot_space_a_participation.parquet
```

交付物（位于 `dao/simulation/DAO_<时间戳>/deliverables/`）：

```
├── 治理提案书.md              # 治理提案书
├── 会议记录_社区讨论.md        # 社区讨论会议记录
├── 治理参数.md                # 治理三大约束（预算/范围/时间线）
├── 治理设计书.md              # 治理设计（投票机制/参数/安全措施）
├── 执行行动_第N轮.md           # 成员治理行动（每轮）
├── 监控报告_第N轮.md           # 治理监控报告（每轮）
├── 治理复盘报告.md            # 治理复盘报告
├── 最终验收意见.md            # 最终验收意见
└── dao_data.json             # 完整结构化数据导出
```

## 模拟输出

每次运行产出一套完整的项目交付物：

```
simulation/PROJ_20251023_181944/
├── deliverables/
│   ├── 项目章程.md                    # 项目章程
│   ├── WBS.md                        # 工作分解结构
│   ├── 进度管理计划.md                 # 进度管理计划
│   ├── 成本管理计划.md                 # 成本管理计划
│   ├── 范围管理计划.md                 # 范围管理计划
│   ├── 会议记录_启动_*.md             # 启动会会议记录
│   ├── 关键路径分析报告_*.md           # 关键路径分析
│   ├── EVM报告_循环*.md               # 挣值分析报告（每轮）
│   ├── NPV分析报告_循环*.md            # NPV 分析报告（每轮）
│   ├── 关键链分析报告_循环*.md          # 关键链分析报告（每轮）
│   ├── app.py                        # 生成的应用代码
│   ├── database.py                   # 生成的数据库模块
│   ├── user_auth.py                  # 生成的认证模块
│   ├── budget_manager.py             # 生成的预算管理模块
│   ├── integration_service.py        # 生成的集成服务模块
│   ├── visualization.py              # 生成的可视化模块
│   ├── 项目总结报告.md                 # 项目总结报告
│   ├── 最终验收意见.md                 # 最终验收意见
│   └── project_data.json             # 完整结构化数据导出
```

## 配置说明

| 参数 | 位置 | 说明 | 默认值 |
|------|------|------|--------|
| `base_url` | `config.py` | LLM API 基础 URL | `https://api.openai.com/v1` |
| `api_key` | `config.py` | LLM API 密钥 | — |
| `model` | `config.py` | 模型名称 | `gpt-4o` |
| `MAX_EXECUTION_CYCLES` | `config.py` | 阶段 4&5 最大评审循环数 | `5` |
| `--project-idea` | CLI | 项目需求描述 | 交互模式 |
| `--project-code` | CLI | 恢复之前的运行 | 自动生成 |

### 使用本地大模型

系统兼容任意 OpenAI API 格式的端点：

```python
# Ollama
LLM_CONFIG = {
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "model": "qwen2.5:14b",
}

# vLLM
LLM_CONFIG = {
    "base_url": "http://localhost:8000/v1",
    "api_key": "token-abc123",
    "model": "Qwen/Qwen2.5-14B-Instruct",
}
```

## 测试

```bash
# 运行全部 86 个测试
python -m unittest tests.test_all -v

# 快速冒烟测试
python test_simple.py
```

详见 [TEST_REPORT.md](TEST_REPORT.md) 获取完整测试报告。

## 架构决策

| 决策 | 理由 |
|------|------|
| **SQLite 作为共享状态** | 零配置、单文件、满足模拟场景需求。所有智能体通过统一接口读写。 |
| **同步执行** | 阶段本质上是顺序的。模拟场景不需要异步复杂度。 |
| **提示词定义角色** | 智能体行为完全通过 `config.py` 中的系统提示词定义，无需微调。 |
| **中文交付物命名** | 目标用户是中文项目管理从业者。文件名即文档标题。 |
| **兜底响应机制** | LLM 调用可能失败。兜底机制确保即使 API 不稳定，模拟也能完成。 |
| **对话截断** | 仅将最近 10 轮对话发送给 LLM。防止长模拟中上下文窗口溢出。 |

## 扩展指南

**添加新角色：** 继承 `BaseAgent`，在 `config.py` 中定义提示词，接入工作流引擎。

**添加新交付物类型：** 在 `DocumentGenerator` 中添加生成方法，在 `SharedDatabase` 中添加存储方法，在 `engine.py` 的对应阶段中调用。

**更换方法论：** 修改 `config.py` 中的阶段定义和智能体提示词。引擎与方法论无关 — 它执行你定义的任何阶段和交互。

## 许可证

MIT
