"""
多智能体项目管理模拟系统 - 主程序

这个系统模拟了一个完整的软件项目组工作流程，包括：
- 项目发起人（Project Sponsor）
- 项目经理（Project Manager）
- 项目组成员（Team Member）

通过六个阶段模拟项目管理过程：
1. 预启动：项目发起人陈述需求，项目经理形成项目章程
2. 启动：三方开会，确定cost/scope/schedule三大约束
3. 计划：项目经理形成WBS和管理计划
4. 执行：项目组成员开发代码
5. 控制：项目经理进行挣值分析，更新计划
6. 结束：交付所有文档和代码
"""
import sys
import os
from datetime import datetime
import argparse

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow.engine import WorkflowEngine
from config import LLM_CONFIG, AGENT_PROMPTS


def generate_project_code():
    """生成项目代号"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"PROJ_{timestamp}"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='多智能体项目管理模拟系统'
    )
    parser.add_argument(
        '--project-idea',
        type=str,
        default=None,
        help='项目创意描述（可选，如果不提供则由AI自动生成）'
    )
    parser.add_argument(
        '--project-code',
        type=str,
        default=None,
        help='项目代号（可选，默认自动生成）'
    )
    
    args = parser.parse_args()
    
    # 生成或使用指定的项目代号
    project_code = args.project_code if args.project_code else generate_project_code()
    
    print("\n" + "="*70)
    print(" " * 15 + "多智能体项目管理模拟系统")
    print("="*70)
    print(f"\n项目代号：{project_code}")
    if args.project_idea:
        print(f"项目创意：{args.project_idea[:100]}...")
    else:
        print("项目创意：由AI自动生成")
    print("\n" + "="*70 + "\n")
    
    try:
        # 创建工作流引擎
        engine = WorkflowEngine(
            project_code=project_code,
            llm_config=LLM_CONFIG,
            agent_prompts=AGENT_PROMPTS,
            project_idea=args.project_idea
        )
        
        # 运行完整的项目生命周期
        engine.run()
        
        print("\n" + "="*70)
        print(" " * 20 + "模拟完成！")
        print("="*70)
        print(f"\n所有交付物已保存到：")
        print(f"  {engine.deliverables_path}")
        print("\n包含以下文件：")
        print("  - 项目章程.md")
        print("  - 会议记录_*.md")
        print("  - WBS.md")
        print("  - 成本管理计划.md")
        print("  - 范围管理计划.md")
        print("  - 进度管理计划.md")
        print("  - EVM报告_*.md")
        print("  - 项目总结报告.md")
        print("  - 最终验收意见.md")
        print("  - 代码文件（*.py等）")
        print("  - project_data.json（完整项目数据）")
        print("\n" + "="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n[中断] 用户终止了程序执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[错误] 程序执行出错：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
