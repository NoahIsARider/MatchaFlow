# 🚀 开始使用 - 多智能体项目管理模拟系统

## 欢迎！

恭喜你获得了这个完整的多智能体项目管理模拟系统！

本系统可以模拟一个完整的软件项目管理流程，包括：
- ✅ 6个项目阶段（预启动→启动→计划→执行→控制→结束）
- ✅ 3个智能体角色（项目发起人、项目经理、项目组成员）
- ✅ 完整的项目文档（章程、WBS、管理计划、EVM报告等）
- ✅ 自动生成的代码文件
- ✅ 智能决策和协作

---

## ⚡ 3步快速开始

### 第1步：安装依赖

```bash
pip install -r requirements.txt
```

### 第2步：运行测试

```bash
python test_simple.py
```

如果看到所有测试通过 `[PASS]`，说明系统可以运行了！

### 第3步：运行你的第一个项目模拟

```bash
python main.py
```

系统会自动：
1. 生成一个项目需求
2. 模拟完整的项目管理流程（6个阶段）
3. 生成所有项目文档和代码

**运行时间**：约3-10分钟（取决于API响应速度）

---

## 📖 阅读文档

| 文档 | 适合人群 | 阅读时间 |
|-----|---------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | 所有人 | 5分钟 |
| [README.md](README.md) | 想了解系统详情 | 10分钟 |
| [USAGE.md](USAGE.md) | 想深入使用 | 15分钟 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 开发者 | 20分钟 |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | 项目管理者 | 10分钟 |

**建议阅读顺序**：
1. 先看 QUICKSTART.md（快速入门）
2. 然后看 README.md（了解系统）
3. 需要时查阅 USAGE.md（高级用法）

---

## 🎯 常用命令

### 基本使用

```bash
# 默认运行（AI自动生成项目需求）
python main.py

# 指定项目需求
python main.py --project-idea "开发一个在线图书管理系统"

# 指定项目代号
python main.py --project-code "MY_PROJECT_001"
```

### 查看结果

```bash
# Windows
explorer simulation

# 或手动打开
# simulation/{项目代号}/deliverables/
```

### 示例项目

查看 `example_ideas.txt` 获取10+个项目创意示例。

---

## 📁 生成的文件

每次模拟会生成：

**📄 项目管理文档**（8+ 个Markdown文件）
- 项目章程
- 会议记录
- WBS（工作分解结构）
- 三大管理计划（成本、范围、进度）
- EVM报告（挣值分析）
- 项目总结报告
- 最终验收意见

**💻 代码文件**（2-5个Python文件）
- 根据项目需求自动生成

**📊 项目数据**
- project_data.json（完整项目数据，可用于分析）

---

## 🎓 学习路径

### 初学者

1. ✅ 运行 `python test_simple.py` 测试系统
2. ✅ 运行 `python main.py` 查看默认模拟
3. ✅ 查看生成的文档，了解项目管理流程
4. ✅ 阅读 README.md 了解系统设计

### 进阶用户

1. ✅ 使用 `--project-idea` 指定自己的项目需求
2. ✅ 修改 `config.py` 中的 `AGENT_PROMPTS` 调整智能体行为
3. ✅ 阅读 USAGE.md 了解高级功能
4. ✅ 分析 project_data.json 研究项目数据

### 开发者

1. ✅ 阅读 ARCHITECTURE.md 了解系统架构
2. ✅ 研究各个模块的源代码
3. ✅ 尝试添加新的智能体角色
4. ✅ 自定义新的项目阶段或文档模板

---

## ⚙️ 系统配置

### LLM配置

系统默认使用 ModelScope 的 Qwen 模型。

如需使用其他模型，编辑 `config.py`：

```python
LLM_CONFIG = {
    'base_url': 'your_api_url',
    'api_key': 'your_api_key',
    'model': 'your_model_name'
}
```

### 智能体行为调整

编辑 `config.py` 中的 `AGENT_PROMPTS` 可以调整三个智能体的行为。

### 循环次数

默认最多执行3次执行-控制循环。修改 `config.py`：

```python
MAX_EXECUTION_CYCLES = 3  # 改为你想要的次数
```

---

## ❓ 常见问题

**Q: 系统需要联网吗？**
A: 是的，需要调用外部LLM API。

**Q: 运行失败怎么办？**
A: 
1. 先运行 `python test_simple.py` 检查组件
2. 检查网络连接
3. 查看错误信息

**Q: 生成的代码质量如何？**
A: 系统重点是**模拟项目管理流程**，代码只是展示工作量，质量次要。

**Q: 可以修改吗？**
A: 完全可以！系统采用模块化设计，易于扩展和修改。

**Q: 如何添加新角色？**
A: 参考 ARCHITECTURE.md 的"扩展点"章节。

---

## 🎉 开始你的第一个模拟

准备好了吗？运行这个命令：

```bash
python main.py --project-idea "开发一个学生选课管理系统，支持课程管理、选课、成绩录入等功能"
```

然后坐下来，观看三个智能体如何协作完成整个项目！ ☕

---

## 📞 需要帮助？

1. 📖 查看文档（README.md, USAGE.md等）
2. 🧪 运行测试（test_simple.py）
3. 🐛 提交Issue描述问题

---

## 📊 系统统计

- 📁 **27个文件**（Python代码 + 文档）
- 💻 **2000+行代码**
- 📝 **40000+字文档**
- ⚙️ **15+个可配置组件**
- 🤖 **3个智能体角色**
- 📋 **6个项目阶段**
- 📄 **8+种文档模板**

---

**祝你使用愉快！开始探索项目管理的魅力吧！** 🚀✨

---

_如果这个系统对你有帮助，别忘了给项目加星 ⭐_
