"""
完整测试套件 - 覆盖所有核心模块
使用 unittest + mock 隔离 LLM 依赖，确保离线可测
"""
import sys
import os
import json
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.shared_db import SharedDatabase
from utils.llm_client import LLMClient
from utils.document_generator import DocumentGenerator
from agents.base_agent import BaseAgent
from agents.sponsor import SponsorAgent
from agents.manager import ManagerAgent
from agents.team_member import TeamMemberAgent
from config import PHASES, MAX_EXECUTION_CYCLES, ROLES, LLM_CONFIG, AGENT_PROMPTS

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# 1. SharedDatabase 测试
# ============================================================
class TestSharedDatabase(unittest.TestCase):
    """共享数据库完整测试"""

    def setUp(self):
        self.db = SharedDatabase("TEST_DB")

    def test_init_default_state(self):
        self.assertEqual(self.db.project_code, "TEST_DB")
        self.assertEqual(self.db.data['project_charter'], '')
        self.assertEqual(self.db.data['constraints'], {})
        self.assertEqual(self.db.data['meeting_records'], [])
        self.assertEqual(self.db.data['evm_records'], [])

    def test_save_project_charter(self):
        self.db.save_project_charter("测试章程")
        self.assertEqual(self.db.data['project_charter'], "测试章程")

    def test_save_constraints(self):
        constraints = {"cost": "10万", "scope": "Web应用", "schedule": "3个月"}
        self.db.save_constraints(constraints)
        self.assertEqual(self.db.data['constraints']['cost'], "10万")
        self.assertEqual(len(self.db.data['constraints']), 3)

    def test_save_wbs(self):
        self.db.save_wbs("1. 需求\n2. 设计")
        self.assertIn("需求", self.db.data['wbs'])

    def test_save_management_plans(self):
        plans = {"cost": "成本计划", "scope": "范围计划", "schedule": "进度计划"}
        self.db.save_management_plans(plans)
        self.assertEqual(self.db.data['management_plans']['cost'], "成本计划")

    def test_save_meeting_record(self):
        self.db.save_meeting_record("启动", "讨论需求")
        self.assertEqual(len(self.db.data['meeting_records']), 1)
        self.assertEqual(self.db.data['meeting_records'][0]['type'], "启动")
        self.assertIn('timestamp', self.db.data['meeting_records'][0])

    def test_save_discussion(self):
        self.db.save_discussion(["经理", "成员"], "技术选型", "用Python")
        self.assertEqual(len(self.db.data['discussions']), 1)
        self.assertEqual(self.db.data['discussions'][0]['topic'], "技术选型")

    def test_save_code_file(self):
        self.db.save_code_file("main.py", "print('hello')")
        self.assertEqual(self.db.data['code_files']['main.py'], "print('hello')")

    def test_save_document(self):
        self.db.save_document("报告.md", "# 报告")
        self.assertEqual(self.db.data['documents']['报告.md'], "# 报告")

    def test_save_evm_record(self):
        evm = {"pv": 100, "ev": 90, "ac": 95}
        self.db.save_evm_record(1, evm)
        self.assertEqual(len(self.db.data['evm_records']), 1)
        self.assertEqual(self.db.data['evm_records'][0]['cycle'], 1)

    def test_save_execution_cycle(self):
        self.db.start_execution_cycle(1)
        self.db.save_execution_cycle(1, "execution", {"status": "done"})
        self.assertEqual(len(self.db.data['execution_cycles']), 1)

    def test_update_cycle_feedback(self):
        self.db.update_cycle_feedback(1, "需要改进", False)
        self.assertEqual(len(self.db.data['cycle_feedbacks']), 1)
        self.assertFalse(self.db.data['cycle_feedbacks'][0]['accepted'])

    def test_save_critical_path_analysis(self):
        cpm = {"critical_path": "A->B->C", "total_duration": 30}
        self.db.save_critical_path_analysis(cpm)
        self.assertEqual(self.db.data['critical_path_analysis']['critical_path'], "A->B->C")

    def test_save_critical_chain_record(self):
        ccpm = {"critical_chain": "X->Y", "buffers": {"project_buffer": 5}}
        self.db.save_critical_chain_record(1, ccpm)
        self.assertEqual(len(self.db.data['critical_chain_records']), 1)

    def test_save_npv_record(self):
        npv = {"npv_value": 50.5, "discount_rate": 0.1}
        self.db.save_npv_record(1, npv)
        self.assertEqual(len(self.db.data['npv_records']), 1)

    def test_get_latest_plans(self):
        self.db.save_wbs("WBS内容")
        self.db.save_management_plans({"cost": "成本", "scope": "范围", "schedule": "进度"})
        plans = self.db.get_latest_plans()
        self.assertEqual(plans['wbs'], "WBS内容")
        self.assertEqual(plans['cost_plan'], "成本")

    def test_get_latest_evm_empty(self):
        self.assertEqual(self.db.get_latest_evm(), {})

    def test_get_latest_evm(self):
        self.db.save_evm_record(1, {"pv": 100})
        self.db.save_evm_record(2, {"pv": 200})
        self.assertEqual(self.db.get_latest_evm()['pv'], 200)

    def test_get_critical_path_analysis(self):
        self.assertEqual(self.db.get_critical_path_analysis(), {})
        self.db.save_critical_path_analysis({"path": "A->B"})
        self.assertEqual(self.db.get_critical_path_analysis()['path'], "A->B")

    def test_get_latest_critical_chain(self):
        self.assertEqual(self.db.get_latest_critical_chain(), {})
        self.db.save_critical_chain_record(1, {"chain": "X"})
        self.assertEqual(self.db.get_latest_critical_chain()['chain'], "X")

    def test_get_latest_npv(self):
        self.assertEqual(self.db.get_latest_npv(), {})
        self.db.save_npv_record(1, {"npv": 100})
        self.assertEqual(self.db.get_latest_npv()['npv'], 100)

    def test_export_and_load(self):
        tmp = tempfile.mktemp(suffix=".json")
        try:
            self.db.save_project_charter("导出测试")
            self.db.save_constraints({"cost": "5万"})
            self.db.export_to_file(tmp)

            db2 = SharedDatabase("TEST_LOAD")
            db2.load_from_file(tmp)
            self.assertEqual(db2.data['project_charter'], "导出测试")
            self.assertEqual(db2.data['constraints']['cost'], "5万")
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    def test_get_summary(self):
        self.db.save_project_charter("章程")
        self.db.save_constraints({"cost": "1", "scope": "2"})
        self.db.save_code_file("a.py", "code")
        summary = self.db.get_summary()
        self.assertEqual(summary['project_charter_length'], 2)
        self.assertEqual(summary['constraints_count'], 2)
        self.assertEqual(summary['code_files_count'], 1)
        self.assertIn('evm_records_count', summary)
        self.assertIn('has_critical_path_analysis', summary)
        self.assertIn('npv_records_count', summary)


# ============================================================
# 2. LLMClient 测试
# ============================================================
class TestLLMClient(unittest.TestCase):
    """LLM客户端测试"""

    def test_init(self):
        client = LLMClient("http://test.com", "key123", "gpt-4")
        self.assertEqual(client.model, "gpt-4")

    @patch('utils.llm_client.OpenAI')
    def test_chat_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "测试响应"
        mock_client.chat.completions.create.return_value = mock_response

        client = LLMClient("http://test.com", "key", "model")
        result = client.chat([{"role": "user", "content": "hello"}])
        self.assertEqual(result, "测试响应")

    @patch('utils.llm_client.OpenAI')
    def test_chat_failure_returns_fallback(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Connection error")

        client = LLMClient("http://test.com", "key", "model")
        result = client.chat([{"role": "user", "content": "hello"}])
        self.assertIn("模拟响应", result)
        self.assertIn("Connection error", result)

    @patch('utils.llm_client.OpenAI')
    def test_chat_with_retry_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "成功"
        mock_client.chat.completions.create.return_value = mock_response

        client = LLMClient("http://test.com", "key", "model")
        result = client.chat_with_retry([{"role": "user", "content": "hi"}], max_retries=3)
        self.assertEqual(result, "成功")

    @patch('utils.llm_client.OpenAI')
    def test_chat_with_retry_all_retries_return_fallback(self, mock_openai):
        """chat() 内部捕获异常返回 fallback，chat_with_retry 正常拿到 fallback"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Fail")

        client = LLMClient("http://test.com", "key", "model")
        result = client.chat_with_retry([{"role": "user", "content": "hi"}], max_retries=2)
        self.assertIn("模拟响应", result)


# ============================================================
# 3. DocumentGenerator 测试
# ============================================================
class TestDocumentGenerator(unittest.TestCase):
    """文档生成器完整测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.gen = DocumentGenerator(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_init_creates_directory(self):
        new_dir = os.path.join(self.temp_dir, "sub", "dir")
        DocumentGenerator(new_dir)
        self.assertTrue(os.path.exists(new_dir))

    def test_save_document(self):
        self.gen.save_document("test.md", "# 测试")
        with open(os.path.join(self.temp_dir, "test.md"), 'r') as f:
            self.assertEqual(f.read(), "# 测试")

    def test_generate_project_charter(self):
        doc = self.gen.generate_project_charter("章程内容")
        self.assertIn("项目章程", doc)
        self.assertIn("章程内容", doc)
        self.assertIn("批准签字", doc)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "项目章程.md")))

    def test_generate_meeting_minutes(self):
        doc = self.gen.generate_meeting_minutes("启动", ["A", "B"], "会议内容")
        self.assertIn("启动", doc)
        self.assertIn("A, B", doc)
        files = [f for f in os.listdir(self.temp_dir) if f.startswith("会议记录")]
        self.assertEqual(len(files), 1)

    def test_generate_wbs(self):
        doc = self.gen.generate_wbs("1. 需求\n2. 设计")
        self.assertIn("WBS", doc)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "WBS.md")))

    def test_generate_management_plan_all_types(self):
        for plan_type, expected_name in [("cost", "成本管理计划"), ("scope", "范围管理计划"), ("schedule", "进度管理计划")]:
            doc = self.gen.generate_management_plan(plan_type, f"{expected_name}内容")
            self.assertIn(expected_name, doc)
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, f"{expected_name}.md")))

    def test_generate_evm_report(self):
        evm = {"pv": 100, "ev": 90, "ac": 95, "cv": -5, "sv": -10, "cpi": 0.95, "spi": 0.90, "analysis": "进度滞后"}
        doc = self.gen.generate_evm_report(1, evm)
        self.assertIn("挣值分析", doc)
        self.assertIn("100.00", doc)
        self.assertIn("进度滞后", doc)

    def test_generate_critical_path_report(self):
        cpm = {"critical_path": "A->B->D", "total_duration": 30, "activities": [{"name": "A", "duration": 10}], "analysis": "关键路径明确", "recommendations": "关注B"}
        doc = self.gen.generate_critical_path_report(cpm)
        self.assertIn("关键路径", doc)
        self.assertIn("30", doc)
        self.assertIn("关注B", doc)

    def test_generate_critical_chain_report(self):
        ccpm = {
            "critical_chain": "X->Y->Z",
            "buffers": {"project_buffer": 5, "feeding_buffer": 3},
            "resource_constraints": "开发人员有限",
            "buffer_status": [{"type": "项目缓冲", "total": 5, "consumed": 1, "remaining": 4, "consumption_rate": 20.0, "status": "正常"}],
            "analysis": "缓冲区充足",
            "action_recommendations": "继续监控"
        }
        doc = self.gen.generate_critical_chain_report(1, ccpm)
        self.assertIn("关键链", doc)
        self.assertIn("缓冲区充足", doc)

    def test_generate_npv_report(self):
        npv = {"npv_value": 50.5, "discount_rate": 0.1, "payback_period": 2.5, "investment_recommendation": "建议投资", "risk_assessment": "风险可控"}
        doc = self.gen.generate_npv_report(1, npv)
        self.assertIn("净现值", doc)
        self.assertIn("50.50", doc)
        self.assertIn("建议投资", doc)
        self.assertIn("风险可控", doc)

    def test_generate_final_summary(self):
        db_data = {
            'constraints': {'cost': '10万', 'scope': 'Web应用', 'schedule': '3个月'},
            'execution_cycles': [{'cycle': 1}],
            'code_files': {'app.py': 'code'},
            'documents': {'报告.md': '内容'},
            'meeting_records': [{'type': '启动'}],
            'discussions': [{'topic': '需求'}],
            'evm_records': [{'cycle': 1, 'cpi': 0.95, 'spi': 0.90, 'cv': -5, 'sv': -10}]
        }
        doc = self.gen.generate_final_summary(db_data, "TEST_001")
        self.assertIn("项目总结报告", doc)
        self.assertIn("TEST_001", doc)
        self.assertIn("10万", doc)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "项目总结报告.md")))

    def test_save_code_file(self):
        self.gen.save_code_file("app.py", "print('hello')")
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "app.py")))


# ============================================================
# 4. BaseAgent 测试
# ============================================================
class TestBaseAgent(unittest.TestCase):
    """Agent基类测试"""

    def setUp(self):
        self.mock_llm = MagicMock(spec=LLMClient)
        self.mock_llm.chat.return_value = "LLM响应"
        self.mock_db = MagicMock(spec=SharedDatabase)
        self.agent = BaseAgent("测试角色", "你是测试助手", self.mock_llm, self.mock_db)

    def test_init(self):
        self.assertEqual(self.agent.role_name, "测试角色")
        self.assertEqual(self.agent.conversation_history, [])
        self.assertEqual(self.agent.working_memory, {})

    def test_think(self):
        result = self.agent.think("你好")
        self.assertEqual(result, "LLM响应")
        self.mock_llm.chat.assert_called_once()

    def test_think_updates_history(self):
        self.agent.think("问题1")
        self.assertEqual(len(self.agent.conversation_history), 2)
        self.assertEqual(self.agent.conversation_history[0]['role'], 'user')
        self.assertEqual(self.agent.conversation_history[1]['role'], 'assistant')

    def test_think_with_context(self):
        self.agent.think("问题", context="额外上下文")
        call_args = self.mock_llm.chat.call_args[0][0]
        context_msgs = [m for m in call_args if "上下文信息" in m.get('content', '')]
        self.assertTrue(len(context_msgs) > 0)

    def test_think_truncates_history_for_llm(self):
        """超过10轮对话时，传给LLM的历史消息被截断"""
        for i in range(15):
            self.agent.think(f"问题{i}")
        self.assertEqual(len(self.agent.conversation_history), 30)
        call_args = self.mock_llm.chat.call_args[0][0]
        history_msgs = [m for m in call_args if m['role'] in ('user', 'assistant')]
        # [-10:] 取最近10条历史 + 当前1条用户消息 = 11
        self.assertLessEqual(len(history_msgs), 11)

    def test_working_memory(self):
        self.agent.add_to_working_memory("key1", "value1")
        self.assertEqual(self.agent.working_memory['key1'], "value1")
        self.agent.clear_working_memory()
        self.assertEqual(self.agent.working_memory, {})


# ============================================================
# 5. SponsorAgent 测试
# ============================================================
class TestSponsorAgent(unittest.TestCase):
    """项目发起人Agent测试"""

    def setUp(self):
        self.mock_llm = MagicMock(spec=LLMClient)
        self.mock_llm.chat.return_value = "发起人响应"
        self.mock_db = MagicMock(spec=SharedDatabase)
        self.mock_db.data = {
            'project_charter': '测试章程',
            'constraints': {'cost': '10万', 'scope': 'Web', 'schedule': '3月'}
        }
        self.sponsor = SponsorAgent(self.mock_llm, self.mock_db, AGENT_PROMPTS['SPONSOR'])

    def test_init(self):
        self.assertEqual(self.sponsor.role_name, "项目发起人")

    def test_state_requirements_with_idea(self):
        result = self.sponsor.state_requirements("开发图书管理系统")
        self.assertEqual(result, "发起人响应")
        call_args = self.mock_llm.chat.call_args[0][0]
        user_msg = [m for m in call_args if m['role'] == 'user'][0]
        self.assertIn("图书管理系统", user_msg['content'])

    def test_state_requirements_without_idea(self):
        result = self.sponsor.state_requirements()
        self.assertEqual(result, "发起人响应")

    def test_participate_in_kickoff(self):
        result = self.sponsor.participate_in_kickoff("会议上下文")
        self.assertEqual(result, "发起人响应")

    def test_review_product_review_only(self):
        """评审模式 - 只提意见不验收"""
        feedback, accepted = self.sponsor.review_product(1, "产品描述", "代码", review_only=True)
        self.assertEqual(feedback, "发起人响应")
        self.assertFalse(accepted)

    def test_review_product_accept(self):
        """验收模式 - 接受"""
        self.mock_llm.chat.return_value = "我决定接受这个版本"
        feedback, accepted = self.sponsor.review_product(3, "产品", "代码", review_only=False)
        self.assertTrue(accepted)

    def test_review_product_reject(self):
        """验收模式 - 拒绝"""
        self.mock_llm.chat.return_value = "【拒绝】产品尚未达到预期标准，需要继续改进功能模块"
        feedback, accepted = self.sponsor.review_product(3, "产品", "代码", review_only=False)
        self.assertFalse(accepted)

    def test_final_acceptance(self):
        """最终验收"""
        self.mock_llm.chat.return_value = "同意最终验收"
        result = self.sponsor.final_acceptance("交付物摘要")
        self.assertEqual(result, "同意最终验收")


# ============================================================
# 6. ManagerAgent 测试
# ============================================================
class TestManagerAgent(unittest.TestCase):
    """项目经理Agent测试"""

    def setUp(self):
        self.mock_llm = MagicMock(spec=LLMClient)
        self.mock_db = MagicMock(spec=SharedDatabase)
        self.mock_db.data = {
            'project_charter': '测试章程',
            'constraints': {'cost': '10万', 'scope': 'Web应用', 'schedule': '3个月'},
            'wbs': 'WBS内容',
            'management_plans': {},
            'meeting_records': [],
            'discussions': [],
            'code_files': {},
            'documents': {},
            'evm_records': [],
            'execution_cycles': [],
            'cycle_feedbacks': [],
            'critical_path_analysis': {},
            'critical_chain_records': [],
            'npv_records': []
        }
        self.manager = ManagerAgent(self.mock_llm, self.mock_db, AGENT_PROMPTS['MANAGER'])

    def test_init(self):
        self.assertEqual(self.manager.role_name, "项目经理")

    def test_draft_project_charter(self):
        self.mock_llm.chat.return_value = "项目章程内容"
        result = self.manager.draft_project_charter("需求描述")
        self.assertEqual(result, "项目章程内容")

    def test_facilitate_kickoff_meeting(self):
        self.mock_llm.chat.return_value = "【成本约束】\n10万\n\n【范围约束】\nWeb应用\n\n【进度约束】\n3个月"
        result = self.manager.facilitate_kickoff_meeting("发起人发言", "成员发言")
        self.assertIsInstance(result, dict)

    def test_create_wbs(self):
        self.mock_llm.chat.return_value = "WBS内容"
        result = self.manager.create_wbs()
        self.assertEqual(result, "WBS内容")

    def test_create_management_plans(self):
        self.mock_llm.chat.return_value = "管理计划内容"
        result = self.manager.create_management_plans()
        self.assertIsInstance(result, dict)
        self.assertIn('cost', result)
        self.assertIn('scope', result)
        self.assertIn('schedule', result)

    def test_perform_evm_analysis(self):
        self.mock_llm.chat.return_value = "EVM分析结果"
        result = self.manager.perform_evm_analysis(1)
        self.assertIsInstance(result, dict)
        self.assertIn('pv', result)
        self.assertIn('ev', result)
        self.assertIn('cpi', result)

    def test_perform_critical_path_analysis(self):
        self.mock_llm.chat.return_value = '{"critical_path": "A->B", "total_duration": 20, "activities": [], "analysis": "分析", "recommendations": "建议"}'
        result = self.manager.perform_critical_path_analysis()
        self.assertIsInstance(result, dict)
        self.assertIn('critical_path', result)

    def test_perform_critical_chain_analysis(self):
        self.mock_llm.chat.return_value = '{"critical_chain": "X->Y", "buffers": {}, "resource_constraints": "无", "buffer_status": [], "analysis": "分析", "action_recommendations": "建议"}'
        result = self.manager.perform_critical_chain_analysis(1)
        self.assertIsInstance(result, dict)

    def test_perform_npv_analysis(self):
        self.mock_llm.chat.return_value = '{"npv_value": 50, "discount_rate": 0.1, "payback_period": 2, "analysis": "可行", "recommendations": "投资"}'
        result = self.manager.perform_npv_analysis(1)
        self.assertIsInstance(result, dict)


# ============================================================
# 7. TeamMemberAgent 测试
# ============================================================
class TestTeamMemberAgent(unittest.TestCase):
    """项目组成员Agent测试"""

    def setUp(self):
        self.mock_llm = MagicMock(spec=LLMClient)
        self.mock_db = MagicMock(spec=SharedDatabase)
        self.mock_db.data = {
            'project_charter': '章程',
            'constraints': {'cost': '10万', 'scope': 'Web', 'schedule': '3月'},
            'wbs': 'WBS',
            'management_plans': {'cost': '', 'scope': '', 'schedule': ''},
        }
        self.member = TeamMemberAgent(self.mock_llm, self.mock_db, AGENT_PROMPTS['TEAM_MEMBER'])

    def test_init(self):
        self.assertEqual(self.member.role_name, "项目组成员")

    def test_participate_in_kickoff(self):
        self.mock_llm.chat.return_value = "技术可行"
        result = self.member.participate_in_kickoff("会议上下文")
        self.assertEqual(result, "技术可行")

    def test_develop_code(self):
        self.mock_llm.chat.return_value = '{"main.py": "print(\'hello\')", "utils.py": "def helper(): pass"}'
        result = self.member.develop_code(1)
        self.assertIsInstance(result, dict)

    def test_report_progress(self):
        self.mock_llm.chat.return_value = "进展报告"
        result = self.member.report_progress(1, {"main.py": "code"})
        self.assertEqual(result, "进展报告")

    def test_discuss_with_sponsor(self):
        """与发起人讨论"""
        self.mock_llm.chat.return_value = "讨论回复"
        result = self.member.discuss_with_sponsor(1, "发起人反馈")
        self.assertEqual(result, "讨论回复")


# ============================================================
# 8. Config 测试
# ============================================================
class TestConfig(unittest.TestCase):
    """配置文件测试"""

    def test_phases_defined(self):
        expected = {'PRE_INITIATION', 'INITIATION', 'PLANNING', 'EXECUTION', 'CONTROL', 'CLOSURE'}
        self.assertEqual(set(PHASES.keys()), expected)

    def test_max_cycles(self):
        self.assertGreaterEqual(MAX_EXECUTION_CYCLES, 3)

    def test_roles_defined(self):
        self.assertIn('SPONSOR', ROLES)
        self.assertIn('MANAGER', ROLES)
        self.assertIn('TEAM_MEMBER', ROLES)

    def test_llm_config_structure(self):
        self.assertIn('base_url', LLM_CONFIG)
        self.assertIn('api_key', LLM_CONFIG)
        self.assertIn('model', LLM_CONFIG)

    def test_agent_prompts_defined(self):
        for role in ['SPONSOR', 'MANAGER', 'TEAM_MEMBER']:
            self.assertIn(role, AGENT_PROMPTS)
            self.assertGreater(len(AGENT_PROMPTS[role]), 50, f"{role} 提示词过短")


# ============================================================
# 9. WorkflowEngine 初始化测试
# ============================================================
class TestWorkflowEngineInit(unittest.TestCase):
    """工作流引擎初始化测试"""

    @patch('workflow.engine.LLMClient')
    def test_engine_init(self, mock_llm_class):
        from workflow.engine import WorkflowEngine
        mock_llm_class.return_value = MagicMock()

        engine = WorkflowEngine(
            project_code="TEST_ENG",
            llm_config={'base_url': 'http://test', 'api_key': 'key', 'model': 'model'},
            agent_prompts=AGENT_PROMPTS,
            project_idea="测试项目"
        )
        self.assertEqual(engine.project_code, "TEST_ENG")
        self.assertEqual(engine.project_idea, "测试项目")
        self.assertIsNotNone(engine.shared_db)
        self.assertIsNotNone(engine.sponsor)
        self.assertIsNotNone(engine.manager)
        self.assertIsNotNone(engine.team_member)
        self.assertIsNotNone(engine.doc_generator)

    @patch('workflow.engine.LLMClient')
    def test_engine_init_without_idea(self, mock_llm_class):
        from workflow.engine import WorkflowEngine
        mock_llm_class.return_value = MagicMock()

        engine = WorkflowEngine(
            project_code="TEST_ENG2",
            llm_config={'base_url': 'http://test', 'api_key': 'key', 'model': 'model'},
            agent_prompts=AGENT_PROMPTS
        )
        self.assertIsNone(engine.project_idea)


# ============================================================
# 10. main.py 入口测试
# ============================================================
class TestMainEntry(unittest.TestCase):
    """主程序入口测试"""

    def test_generate_project_code(self):
        from main import generate_project_code
        code = generate_project_code()
        self.assertTrue(code.startswith("PROJ_"))
        self.assertGreater(len(code), 10)

    def test_generate_project_code_format(self):
        from main import generate_project_code
        code = generate_project_code()
        self.assertTrue(code.startswith("PROJ_"))
        # 格式: PROJ_YYYYMMDD_HHMMSS
        parts = code.split("_")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[1]), 8)  # YYYYMMDD
        self.assertEqual(len(parts[2]), 6)  # HHMMSS

    def test_argparse_setup(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--project-idea', type=str, default=None)
        parser.add_argument('--project-code', type=str, default=None)
        args = parser.parse_args(['--project-idea', '测试项目', '--project-code', 'TEST'])
        self.assertEqual(args.project_idea, '测试项目')
        self.assertEqual(args.project_code, 'TEST')

    def test_argparse_defaults(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--project-idea', type=str, default=None)
        parser.add_argument('--project-code', type=str, default=None)
        args = parser.parse_args([])
        self.assertIsNone(args.project_idea)
        self.assertIsNone(args.project_code)


# ============================================================
# 11. 已有模拟产出验证
# ============================================================
class TestSimulationOutputs(unittest.TestCase):
    """验证已有的模拟产出文件完整性"""

    SIMULATION_DIRS = []

    @classmethod
    def setUpClass(cls):
        sim_base = os.path.join(PROJECT_ROOT, "simulation")
        if os.path.exists(sim_base):
            for d in sorted(os.listdir(sim_base)):
                if not d.startswith("PROJ_"):
                    continue
                full = os.path.join(sim_base, d, "deliverables")
                if os.path.isdir(full):
                    cls.SIMULATION_DIRS.append(full)

    @classmethod
    def tearDownClass(cls):
        # 清理 WorkflowEngine 测试产生的临时目录
        sim_base = os.path.join(PROJECT_ROOT, "simulation")
        if os.path.exists(sim_base):
            for d in os.listdir(sim_base):
                if d.startswith("TEST_"):
                    shutil.rmtree(os.path.join(sim_base, d), ignore_errors=True)

    def test_simulations_exist(self):
        self.assertGreater(len(self.SIMULATION_DIRS), 0, "未找到模拟产出目录")

    def test_deliverables_complete(self):
        required_prefixes = ["项目章程", "WBS", "成本管理计划", "范围管理计划", "进度管理计划", "项目总结报告", "最终验收意见"]
        for sim_dir in self.SIMULATION_DIRS:
            files = os.listdir(sim_dir)
            for prefix in required_prefixes:
                matched = [f for f in files if f.startswith(prefix)]
                self.assertTrue(len(matched) > 0, f"模拟 {os.path.basename(os.path.dirname(sim_dir))} 缺少 {prefix}")

    def test_evm_reports_exist(self):
        for sim_dir in self.SIMULATION_DIRS:
            evm_files = [f for f in os.listdir(sim_dir) if f.startswith("EVM")]
            self.assertGreater(len(evm_files), 0, f"模拟缺少EVM报告")

    def test_code_files_exist(self):
        for sim_dir in self.SIMULATION_DIRS:
            py_files = [f for f in os.listdir(sim_dir) if f.endswith('.py')]
            self.assertGreater(len(py_files), 0, f"模拟缺少代码文件")

    def test_project_data_json_valid(self):
        for sim_dir in self.SIMULATION_DIRS:
            json_path = os.path.join(sim_dir, "project_data.json")
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                self.assertIsInstance(data, dict)
                self.assertIn('project_charter', data)
                self.assertIn('constraints', data)
                self.assertIn('code_files', data)

    def test_critical_path_reports_exist(self):
        for sim_dir in self.SIMULATION_DIRS:
            cpm_files = [f for f in os.listdir(sim_dir) if f.startswith("关键路径")]
            self.assertGreater(len(cpm_files), 0, f"模拟缺少关键路径分析报告")

    def test_npv_reports_exist(self):
        for sim_dir in self.SIMULATION_DIRS:
            npv_files = [f for f in os.listdir(sim_dir) if f.startswith("NPV")]
            self.assertGreater(len(npv_files), 0, f"模拟缺少NPV分析报告")


if __name__ == "__main__":
    unittest.main(verbosity=2)
