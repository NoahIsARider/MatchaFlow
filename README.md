# Multi-Agent Project Management Simulation System

This is a large language model (LLM) based multi-agent system that simulates a complete software project management workflow.

## System Overview

### Core Features

- **Three agent roles**: project sponsor, project manager, and team members
- **Six project phases**: pre-initiation, initiation, planning, execution, control, and closure
- **Complete project management workflow**: from requirement elicitation to final delivery
- **Earned value management (EVM)**: tracks project cost and schedule performance
- **Shared database**: centralized project information storage accessed by all agents
- **Memory management**: each agent maintains its own conversation history and working memory

### System Architecture

```
ProjectManagement/
├── agents/                 # Agent modules
│   ├── base_agent.py      # Base agent class
│   ├── sponsor.py         # Project sponsor
│   ├── manager.py         # Project manager
│   └── team_member.py     # Team member
├── database/              # Database module
│   └── shared_db.py       # Shared database
├── workflow/              # Workflow module
│   └── engine.py          # Workflow engine
├── utils/                 # Utility modules
│   ├── llm_client.py     # LLM client
│   └── document_generator.py  # Document generator
├── simulation/            # Simulation result storage
│   └── {project_code}/    # Results of each simulation
│       └── deliverables/  # Deliverables
├── config.py             # Configuration file
├── main.py               # Main program
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Project Phases

### Phase 1: Pre-initiation

- **Participants**: project sponsor, project manager
- **Activities**:
  - The project sponsor states the project requirements
  - The project manager discusses the requirements with the sponsor
  - The project manager drafts the project charter
- **Deliverable**: project charter

### Phase 2: Initiation

- **Participants**: project sponsor, project manager, team members
- **Activities**:
  - Hold the project kick-off meeting
  - All parties discuss the project constraints
  - Define the triple constraints: cost, scope, and schedule
- **Deliverables**: meeting minutes, triple constraints document

### Phase 3: Planning

- **Participants**: project manager (lead)
- **Activities**:
  - Create the WBS based on the project charter and the triple constraints
  - Develop the cost management plan
  - Develop the scope management plan
  - Develop the schedule management plan
- **Deliverables**: WBS, three management plans

### Phase 4: Execution

- **Participants**: team members, project manager, project sponsor
- **Activities**:
  - Team members develop code
  - Report progress to the project manager
  - Discuss the product with the project sponsor
- **Deliverables**: code files, progress reports

### Phase 5: Control

- **Participants**: project manager (lead)
- **Activities**:
  - Gather feedback from all parties
  - Update the WBS and management plans
  - Record work performance (cost, completed work)
  - Perform earned value analysis (EVM)
- **Deliverables**: updated management plans, EVM reports

### Loop Execution

Phases 4 and 5 run in a loop until:
1. The project sponsor accepts the current version (up to 3 loops)
2. Or the schedule time limit is reached

### Phase 6: Closure

- **Participants**: everyone
- **Activities**:
  - Organize all deliverables
  - Generate the project summary report
  - Final acceptance by the project sponsor
- **Deliverables**:
  - All project documents
  - All code files
  - Project database (JSON)
  - Project summary report
  - Final acceptance opinion

## Installation and Usage

### Environment Requirements

- Python 3.8+
- Network connection (for calling external LLM APIs)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the System

#### Basic usage (AI auto-generates project requirements)

```bash
python main.py
```

#### Specify project requirements

```bash
python main.py --project-idea "Develop an online library management system supporting book borrowing, return, query, and other features"
```

#### Specify a project code

```bash
python main.py --project-code "PROJ_LIBRARY_001"
```

### View Results

After the run completes, all deliverables are saved to:

```
simulation/{project_code}/deliverables/
```

Including:
- **项目章程.md** - Project charter document
- **会议记录_*.md** - Meeting minutes for each phase
- **WBS.md** - Work breakdown structure
- **成本管理计划.md** - Cost management plan
- **范围管理计划.md** - Scope management plan
- **进度管理计划.md** - Schedule management plan
- **EVM报告_循环*.md** - Earned value analysis reports
- **项目总结报告.md** - Project summary report
- **最终验收意见.md** - Final acceptance opinion
- **Code files (e.g., *.py)** - Project code
- **project_data.json** - Complete project data

## LLM Configuration

The system uses external LLM APIs for agent simulation. The configuration lives in `config.py`:

```python
LLM_CONFIG = {
    'base_url': '',
    'api_key': '',
    'model': ''
}
```

To use a different model, modify this configuration.

## Technical Highlights

### 1. Agent Architecture

- **BaseAgent base class**: provides a unified interface and memory management
- **Role specialization**: each agent has dedicated system prompts and behavior logic
- **Memory system**:
  - Short-term memory: conversation history
  - Working memory: task-related temporary information
  - Long-term memory: accessed through the shared database

### 2. Shared Database

- Centralized data storage
- Supports all kinds of project data: documents, code, meeting minutes, discussion records, etc.
- Provides query interfaces that agents can access on demand
- Supports export to JSON format

### 3. Workflow Engine

- Strictly follows the project management workflow
- Supports data transfer between phases
- Loop execution mechanism (execution-control loop)
- Decision logic (whether the project sponsor accepts)

### 4. Document Generation

- Automatically generates standardized project documents
- Markdown format, easy to read
- Includes timestamps and signature blocks
- Complies with project management standards

### 5. Earned Value Analysis (EVM)

- Computes key metrics: PV, EV, AC, CV, SV, CPI, SPI
- Automatically generates analysis reports
- Used to track project performance

## Notes

1. **Process simulation is the focus**: the core goal of the system is to simulate the project management process, not to generate high-quality code

2. **API calls**: the system needs to call external LLM APIs, so please make sure the network connection is working

3. **Execution time**: a full run may take from a few minutes to over ten minutes, depending on API response speed

4. **Error handling**: if an API call fails, the system continues with a simulated response

5. **Extensibility**:
   - More agent roles can be added
   - Project phases can be customized
   - Decision logic can be modified

## Sample Output

After running the system, you will see output similar to:

```
==============================================================
Starting project lifecycle execution
==============================================================

==============================================================
Phase 1/6: Pre-initiation
==============================================================

[1.1] The project sponsor states the requirements...

Requirement description:
...

[1.2] The project manager drafts the project charter...

Project charter:
...

[Done] Pre-initiation phase complete

==============================================================
Phase 2/6: Initiation
==============================================================

...
```

## Extension and Customization

### Adding a New Agent Role

1. Create a new agent class in the `agents/` directory
2. Inherit from `BaseAgent`
3. Implement the specific behavior methods
4. Add the system prompt in `config.py`
5. Integrate it into the workflow in `workflow/engine.py`

### Modifying Project Phases

1. Edit `PHASES` in `config.py`
2. Add or modify phase methods in `workflow/engine.py`
3. Update the execution logic of the `run()` method

### Customizing Document Templates

1. Edit `utils/document_generator.py`
2. Modify or add document generation methods
3. Customize the Markdown templates

## Contribution Guide

Issues and Pull Requests are welcome!

## License

MIT License

## Contact

If you have any questions, please submit an Issue or contact the developer.

---

**Development time**: October 2025

**Version**: 1.0.1
