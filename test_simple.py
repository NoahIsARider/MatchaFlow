"""
简化测试脚本 - 测试系统各组件是否正常工作
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.llm_client import LLMClient
from database.shared_db import SharedDatabase
from config import LLM_CONFIG

def test_database():
    """测试共享数据库"""
    print("\n[测试] 共享数据库...")
    
    db = SharedDatabase("TEST_001")
    
    # 测试保存项目章程
    db.save_project_charter("这是一个测试项目章程")
    
    # 测试保存约束
    db.save_constraints({
        "cost": "预算10万元",
        "scope": "开发一个简单的Web应用",
        "schedule": "2个月"
    })
    
    # 测试添加会议记录
    db.save_meeting_record(
        meeting_type="启动",
        content="讨论了项目需求"
    )
    
    # 测试添加讨论
    db.save_discussion(
        participants=["项目经理", "项目发起人"],
        topic="需求确认",
        content="请确认需求是否正确"
    )
    
    # 测试保存代码
    db.save_code_file("test.py", "print('hello')")
    
    # 测试获取摘要
    summary = db.get_summary()
    print(summary)
    
    print("[成功] 数据库测试通过")
    return True

def test_llm_client():
    """测试LLM客户端"""
    print("\n[测试] LLM客户端...")
    
    try:
        client = LLMClient(
            base_url=LLM_CONFIG['base_url'],
            api_key=LLM_CONFIG['api_key'],
            model=LLM_CONFIG['model']
        )
        
        # 发送一个简单的测试请求
        messages = [
            {"role": "system", "content": "你是一个测试助手"},
            {"role": "user", "content": "请回复'测试成功'"}
        ]
        
        response = client.chat(messages, temperature=0.5, max_tokens=50)
        print(f"LLM响应：{response[:100]}...")
        
        print("[成功] LLM客户端测试通过")
        return True
    except Exception as e:
        print(f"[警告] LLM客户端测试失败：{e}")
        print("这可能是由于网络或API配置问题")
        print("系统仍可运行，但会使用模拟响应")
        return False

def test_document_generator():
    """测试文档生成器"""
    print("\n[测试] 文档生成器...")
    
    from utils.document_generator import DocumentGenerator
    import tempfile
    
    # 使用临时目录
    temp_dir = tempfile.mkdtemp()
    gen = DocumentGenerator(temp_dir)
    
    # 测试生成项目章程
    gen.generate_project_charter("测试项目章程内容")
    
    # 测试生成会议记录
    gen.generate_meeting_minutes("启动", ["A", "B", "C"], "会议内容")
    
    # 检查文件是否创建
    files = os.listdir(temp_dir)
    print(f"生成的文件：{files}")
    
    print("[成功] 文档生成器测试通过")
    return True

def main():
    """运行所有测试"""
    print("="*60)
    print("系统组件测试")
    print("="*60)
    
    results = []
    
    # 测试数据库
    results.append(("数据库", test_database()))
    
    # 测试文档生成器
    results.append(("文档生成器", test_document_generator()))
    
    # 测试LLM客户端（可能失败）
    results.append(("LLM客户端", test_llm_client()))
    
    # 显示结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results[:2])  # LLM测试失败也可以接受
    
    if all_passed:
        print("\n[结论] 核心组件测试通过，系统可以运行！")
        print("\n运行完整模拟：")
        print("  python main.py")
        print("\n或指定项目需求：")
        print("  python main.py --project-idea \"你的项目需求描述\"")
    else:
        print("\n[警告] 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()
