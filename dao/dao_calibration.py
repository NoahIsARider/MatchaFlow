"""
OnChainGov 校准模块

读取 OnChainGov 实证工具链产出的指标 parquet（participation/concentration），
将其映射为 DAO 模拟的校准参数，注入到各 Agent 的提示词中。

指标 -> 校准映射：
- participation（参与度）：
    avg_votes_per_proposal / voting_intensity 高 -> 社区活跃 -> 成员投票意愿高
    参与度低 -> 治理设计应降低门槛/加强激励
- concentration（集中度）：
    voter_count 小 / proposal_count 少 -> 治理集中 -> 需反集中机制
"""
import os
from typing import Dict, Optional


def _level_from_value(value: Optional[float], low: float = 0.3,
                      high: float = 0.7, default: str = 'medium') -> str:
    """数值 -> 等级"""
    if value is None:
        return default
    if value < low:
        return 'low'
    if value > high:
        return 'high'
    return 'medium'


def load_calibration(parquet_path: Optional[str] = None) -> Dict:
    """
    从 OnChainGov 指标 parquet 加载校准参数。

    Args:
        parquet_path: 指标文件路径（participation/concentration 均可）。
                      为 None 或文件不存在时返回默认校准。

    Returns:
        校准字典，包含 participation_level / concentration_level / hints
    """
    if not parquet_path or not os.path.exists(parquet_path):
        from dao.dao_config import DEFAULT_CALIBRATION
        return dict(DEFAULT_CALIBRATION)

    try:
        import pandas as pd
        df = pd.read_parquet(parquet_path)
        if df.empty:
            raise ValueError('parquet 为空')
        row = df.iloc[0].to_dict()
    except Exception as e:
        from dao.dao_config import DEFAULT_CALIBRATION
        cal = dict(DEFAULT_CALIBRATION)
        cal['source'] = f'{parquet_path} (读取失败: {e})'
        cal['hints'] = f'OnChainGov 数据读取失败（{e}），使用默认校准参数。'
        return cal

    # ---- 参与度 ----
    # 优先用 avg_votes_per_proposal / voting_intensity，其次 participation_rate
    avg_votes = row.get('avg_votes_per_proposal')
    intensity = row.get('voting_intensity')
    part_rate = row.get('participation_rate')

    if avg_votes is not None and not _is_nan(avg_votes):
        # 每提案平均票数：<5 低 / 5-15 中 / >15 高
        participation_level = _level_from_value(avg_votes, low=5.0, high=15.0)
    elif intensity is not None and not _is_nan(intensity):
        participation_level = _level_from_value(intensity, low=5.0, high=15.0)
    elif part_rate is not None and not _is_nan(part_rate):
        participation_level = _level_from_value(part_rate, low=0.3, high=0.7)
    else:
        participation_level = 'medium'

    # ---- 集中度 ----
    # voter_count 小 -> 集中；proposal_count 少 -> 提案渠道集中
    voter_count = row.get('voter_count')
    proposal_count = row.get('proposal_count')
    concentration_score = None
    if voter_count is not None and not _is_nan(voter_count) and proposal_count is not None and not _is_nan(proposal_count):
        # 每提案平均投票人数：越小越集中
        concentration_score = voter_count / max(proposal_count, 1)
        concentration_level = _level_from_value(concentration_score, low=5.0, high=15.0, default='high')
        concentration_level = {'low': 'high', 'medium': 'medium', 'high': 'low'}[concentration_level]
    elif voter_count is not None and not _is_nan(voter_count):
        concentration_level = 'high' if voter_count < 20 else ('medium' if voter_count < 100 else 'low')
    else:
        concentration_level = 'medium'

    hints = (
        f"OnChainGov 实证校准（来源：{os.path.basename(parquet_path)}）：\n"
        f"- 社区参与度：{participation_level}（voter_count={_fmt(row.get('voter_count'))}, "
        f"proposal_count={_fmt(row.get('proposal_count'))}, avg_votes_per_proposal={_fmt(avg_votes)}）\n"
        f"- 治理集中度：{concentration_level}"
    )

    return {
        'source': parquet_path,
        'participation_level': participation_level,
        'concentration_level': concentration_level,
        'voter_count': row.get('voter_count'),
        'proposal_count': row.get('proposal_count'),
        'avg_votes_per_proposal': avg_votes,
        'hints': hints
    }


def calibration_prompt(calibration: Dict) -> str:
    """生成注入 Agent 提示词的校准说明"""
    level_hint = {
        'low': '参与度偏低：成员投票意愿不高，治理设计应降低门槛、加强激励。',
        'medium': '参与度中等：社区有一定活跃度，保持常规激励即可。',
        'high': '参与度较高：社区活跃，可设计更精细的治理机制。'
    }
    conc_hint = {
        'low': '集中度低：决策权分散，治理生态健康。',
        'medium': '集中度中等：存在一定集中，建议关注公平性。',
        'high': '集中度高：少数成员掌握主要话语权，必须设计反集中机制（委托上限、二次方投票等）。'
    }
    return (
        f"[OnChainGov 校准数据]\n{calibration.get('hints', '')}\n"
        f"{level_hint.get(calibration.get('participation_level', 'medium'), '')}\n"
        f"{conc_hint.get(calibration.get('concentration_level', 'medium'), '')}"
    )


def _is_nan(v) -> bool:
    try:
        return v != v  # NaN 判断
    except Exception:
        return False


def _fmt(v) -> str:
    if v is None or _is_nan(v):
        return 'N/A'
    if isinstance(v, float):
        return f'{v:.2f}'
    return str(v)
