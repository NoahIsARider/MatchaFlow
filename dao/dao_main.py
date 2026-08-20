"""
DAO 治理模拟系统 - 主程序

用法示例：
    export LLM_BASE_URL=https://api-inference.modelscope.cn/v1
    export LLM_API_KEY=sk-xxx
    export LLM_MODEL=Qwen/Qwen3.8-27B

    # 基础运行（不接 OnChainGov 校准）
    python3 dao/dao_main.py --proposal-idea "调整社区投票门槛"

    # 接入 OnChainGov 实证指标校准
    python3 dao/dao_main.py --proposal-idea "引入委托投票机制" \
        --calibration-path ../onchaingov/data/indicators/snapshot_space_a_participation.parquet
"""
import sys
import os
from datetime import datetime
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dao.dao_config import LLM_CONFIG, DAO_AGENT_PROMPTS
from dao.dao_engine import DAOEngine
from dao.dao_calibration import load_calibration


def generate_project_code():
    """生成提案代号"""
    return f"DAO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def main():
    parser = argparse.ArgumentParser(description='DAO 治理模拟系统')
    parser.add_argument('--proposal-idea', type=str, default=None,
                        help='治理提案构想（可选，不提供则由 AI 自动生成）')
    parser.add_argument('--project-code', type=str, default=None,
                        help='提案代号（可选，默认自动生成）')
    parser.add_argument('--calibration-path', type=str, default=None,
                        help='OnChainGov 指标 parquet 路径（可选，用于校准模拟参数）')
    parser.add_argument('--no-calibration', action='store_true',
                        help='强制跳过 OnChainGov 校准（使用默认参数）')
    args = parser.parse_args()

    project_code = args.project_code if args.project_code else generate_project_code()

    print("\n" + "=" * 70)
    print(" " * 18 + "DAO 治理模拟系统")
    print("=" * 70)
    print(f"\n提案代号：{project_code}")
    if args.proposal_idea:
        print(f"提案构想：{args.proposal_idea[:100]}...")
    else:
        print("提案构想：由 AI 自动生成")
    print("\n" + "=" * 70 + "\n")

    # 加载校准（--no-calibration 或未提供路径 -> 默认）
    calibration = None
    if not args.no_calibration:
        calibration = load_calibration(args.calibration_path)

    engine = DAOEngine(
        project_code=project_code,
        llm_config=LLM_CONFIG,
        agent_prompts=DAO_AGENT_PROMPTS,
        calibration=calibration,
        proposal_idea=args.proposal_idea
    )

    engine.run()

    print("\n" + "=" * 70)
    print(" " * 22 + "模拟完成！")
    print("=" * 70)
    print(f"\n所有交付物已保存到：")
    print(f"  {engine.deliverables_path}")
    print("  - 治理提案书.md")
    print("  - 会议记录_社区讨论.md")
    print("  - 治理参数.md")
    print("  - 治理设计书.md")
    print("  - 执行行动_第X轮.md")
    print("  - 监控报告_第X轮.md")
    print("  - 治理复盘报告.md")
    print("  - 最终验收意见.md")
    print("  - dao_data.json（完整治理数据）")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
