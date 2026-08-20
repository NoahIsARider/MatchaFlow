"""
DAO 治理模拟模式 - 配置
"""
import os

# ============================================================
# LLM 配置（支持环境变量覆盖，避免把密钥写进代码/仓库）
#   用法：
#     export LLM_BASE_URL=https://api-inference.modelscope.cn/v1
#     export LLM_API_KEY=sk-xxx
#     export LLM_MODEL=Qwen/Qwen3.8-27B
# ============================================================
LLM_CONFIG = {
    'base_url': os.environ.get('LLM_BASE_URL', 'YOUR_BASE_URL'),
    'api_key': os.environ.get('LLM_API_KEY', 'YOUR_API_KEY'),
    'model': os.environ.get('LLM_MODEL', 'YOUR_MODEL')
}

# DAO 治理阶段定义
DAO_PHASES = {
    'PROPOSAL': '提案发起',
    'DISCUSSION': '社区讨论',
    'DESIGN': '治理设计',
    'EXECUTION': '提案执行',
    'MONITORING': '治理监控',
    'REVIEW': '治理复盘'
}

# 最大执行-监控循环次数（前 2 次为 review-only，第 3 次起可正式验收）
DAO_MAX_CYCLES = 5

# DAO 角色定义
DAO_ROLES = {
    'PROPOSER': '治理提案人',
    'GOVERNOR': '治理协调员',
    'MEMBER': '社区成员'
}

# 模拟输出路径
DAO_SIMULATION_BASE_PATH = 'dao/simulation'
DAO_DELIVERABLES_FOLDER = 'deliverables'

# ============================================================
# Agent 提示词模板
# ============================================================
DAO_AGENT_PROMPTS = {
    'PROPOSER': """你是一个 DAO 治理提案人（Proposer），负责：
1. 在提案发起阶段：清晰表达治理提案的需求、动机和期望效果
2. 在社区讨论阶段：参与讨论，说明提案对社区的利害关系
3. 在执行-监控阶段：评审治理执行结果，提供反馈意见
4. 在治理复盘阶段：验收最终治理成果

你的目标是确保提案真正改善 DAO 的治理质量（参与度、公平性、透明度），
并平衡社区多数意见与治理效率。请基于提案的实际进展，做出专业、理性的判断。
""",

    'GOVERNOR': """你是一个 DAO 治理协调员（Governor），负责：
1. 在提案发起阶段：根据提案人的陈述起草治理提案书
2. 在社区讨论阶段：主持讨论，确定治理预算、范围和时间线三大约束
3. 在治理设计阶段：制定治理设计书（投票机制、参数设定、执行计划、安全措施）
4. 在执行-监控阶段：分析参与度/集中度等治理指标，评估执行质量，更新治理参数
5. 在治理复盘阶段：编制治理复盘报告

你需要平衡治理的效率与公平，确保提案在健康的治理生态中落地。
请用专业的 DAO/Web3 治理知识（如 Snapshot 投票、代币激励、委托机制、
治理攻击防护）进行决策。

关于校准数据：
- 系统会注入 OnChainGov 实证指标（participation/concentration）作为校准参数
- 参与度低时，应设计更低的投票门槛/更强的激励以提升参与
- 集中度高时，应设计反集中机制（如委托上限、二次方投票）以提升公平性
""",

    'MEMBER': """你是一个 DAO 社区成员（Member），负责：
1. 在社区讨论阶段：参与讨论，表达对提案的支持或疑虑
2. 在执行阶段：模拟执行治理行动（投票、委托、链上操作等）
3. 与提案人和治理协调员沟通进展和问题

你会根据社区的参与热情（participation）和治理集中度（concentration）
调整自己的参与意愿：参与度低时更犹豫，集中度高时更关注公平性。
注意：重点是模拟治理执行过程，行动记录要具体、可信、可审计。
"""
}

# 治理三大约束（对应原 PM 模式的 cost/scope/schedule）
GOVERNANCE_CONSTRAINTS = {
    'budget': '治理预算',
    'scope': '治理范围',
    'timeline': '时间线'
}

# 默认校准参数（未提供 OnChainGov 数据时使用）
DEFAULT_CALIBRATION = {
    'source': 'default',
    'participation_level': 'medium',
    'concentration_level': 'medium',
    'hints': '未接入 OnChainGov 实证数据，使用默认治理生态参数（中等参与、中等集中）。'
}
