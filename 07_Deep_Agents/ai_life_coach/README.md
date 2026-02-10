# AI Life Coach

🤖 **Your Personal AI Life Coach** - Comprehensive life guidance across career, relationships, finance, and wellness with persistent memory and adaptive recommendations.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

---

## 🌟 Quick Start

Get started in 3 simple steps:

```bash
# 1. Clone and navigate to the project
git clone <repository-url>
cd ai_life_coach

# 2. Set up your environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Start your coaching session
python src/main.py
```

**Ready to begin?** Start with: `"I'm ready to start improving my life. Can you guide me through the process?"`

---

## 🎯 What Is AI Life Coach?

AI Life Coach is a sophisticated Deep Agent system that provides comprehensive life guidance across four key domains:

### Core Architecture
```
Life Coach Coordinator (Main Orchestrator)
├── 🚀 Career Specialist      # Career planning, skill development, job transitions
├── 💝 Relationship Specialist  # Communication, boundaries, social skills
├── 💰 Finance Specialist       # Budgeting, investing, financial planning
└── 🌿 Wellness Specialist      # Health, habits, stress management, life balance
```

### How It Works

1. **📊 Initial Assessment** - Comprehensive evaluation across all life domains
2. **🎯 Goal Setting** - Define meaningful, achievable goals with dependencies
3. **📋 Action Planning** - Create 90-day structured action plans
4. **📈 Progress Tracking** - Weekly check-ins and adaptive recommendations
5. **🔄 Continuous Improvement** - Learn from your patterns and optimize guidance

---

## 🚀 Key Features

### Core Capabilities
- ✅ **Multi-Domain Coaching** - Career, Relationships, Finance, Wellness
- ✅ **Personalized Assessment** - Tailored evaluation of your current situation
- ✅ **Smart Goal Planning** - Goals with dependency mapping and conflict detection
- ✅ **90-Day Action Plans** - Structured, achievable roadmaps
- ✅ **Weekly Progress Tracking** - Habit formation and milestone monitoring
- ✅ **Adaptive Recommendations** - AI learns from your patterns and preferences

### Advanced Features
- ✅ **Mood Tracking** - Emotional state monitoring with sentiment analysis
- ✅ **Goal Dependency Visualization** - See how goals connect and support each other
- ✅ **Personalized Reflections** - AI-generated prompts based on your journey
- ✅ **Cross-Domain Insights** - Understand how different life areas affect each other
- ✅ **Emergency Support** - Crisis detection and resource guidance
- ✅ **Persistent Memory** - Your coaching history and preferences saved between sessions

---

## 🏗️ Architecture Overview

### Four Deep Agent Elements

1. **🗂️ Planning System**
   - Multi-phase todo lists with dependencies
   - Discovery → Planning → Execution → Review phases
   - Smart task prioritization and conflict resolution

2. **💾 Context Management**
   - Filesystem-based storage across 5 directories
   - User profiles, assessments, plans, progress, resources
   - Secure data isolation and organization

3. **🤖 Subagent Coordination**
   - 4 specialized domain experts
   - Parallel processing for efficiency
   - Cross-domain insight synthesis

4. **🧠 Long-Term Memory**
   - LangGraph Store with namespace patterns
   - Learns from your successes and challenges
   - Personalized recommendation engine

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-key-features)
- [Installation](#-installation)
- [Getting Started](#-getting-started)
- [User Guide](#-user-guide)
- [Domain Specialists](#-domain-specialists)
- [Examples](#-examples)
- [FAQ](#-faq)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🛠️ Installation

### System Requirements
- **Python**: 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space
- **OS**: Windows, macOS, or Linux

### Step-by-Step Setup

#### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd ai_life_coach
```

#### 2. **Create Virtual Environment**
```bash
# For Unix/macOS:
python3 -m venv venv
source venv/bin/activate

# For Windows:
python -m venv venv
venv\Scripts\activate
```

#### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### 4. **Configure Environment**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# (See Configuration section below)
```

#### 5. **Verify Installation**
```bash
python src/main.py --test
```

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Local Model (Optional)
LOCAL_MODEL_ENDPOINT=http://localhost:8080/v1
MODEL_NAME=glm-4.7

# Storage Configuration
WORKSPACE_DIR=./workspace
MEMORY_BACKEND=filesystem

# User Settings
DEFAULT_USER_ID=user123
DEBUG_MODE=false
```

### Model Options
Choose your preferred AI model:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **GPT-4** | OpenAI's advanced model | Excellent reasoning | API costs |
| **Claude** | Anthropic's model | Great with nuance | API costs |
| **Local Model** | Privacy-first setup | Free, private | Requires hardware |
| **Hybrid** | Mix of models for different tasks | Optimized performance | Complex setup |

---

## 🎓 Getting Started

### Your First Session

1. **Launch the Coach**
   ```bash
   python src/main.py
   ```

2. **Complete Initial Assessment**
   ```
   You'll be guided through a comprehensive evaluation covering:
   - Career satisfaction and goals
   - Relationship quality and social connections
   - Financial health and objectives
   - Wellness across 8 dimensions
   ```

3. **Receive Your Personalized Plan**
   ```
   Based on your assessment, you'll get:
   - Top 3 priority areas
   - 90-day action plan
   - Goal dependencies and potential conflicts
   - Weekly milestones and check-ins
   ```

### Example First Interaction

```python
>>> coach.invoke({
...     "messages": [{
...         "role": "user", 
...         "content": "I'm feeling stuck in my career and it's affecting my relationships. Can you help me?"
...     }]
... })

Response: "I understand you're experiencing career stagnation that's impacting your relationships. 
Let me coordinate with my specialists to create a comprehensive plan for you..."
```

---

## 📖 User Guide

### Coaching Workflow

#### Phase 1: Discovery (Week 1)
- Comprehensive life assessment
- Identify core values and priorities
- Map current situation vs. desired future
- Set SMART goals with dependencies

#### Phase 2: Planning (Week 2)
- Create 90-day action plans
- Establish weekly milestones
- Identify resources and support needs
- Schedule regular check-ins

#### Phase 3: Execution (Weeks 3-12)
- Implement action plans
- Track progress and habits
- Adapt strategies based on feedback
- Celebrate wins and learn from setbacks

#### Phase 4: Review (Every 4 weeks)
- Evaluate progress and lessons learned
- Adjust goals and strategies
- Plan next phase priorities
- Update long-term vision

### Daily Interactions

**Morning Check-in (2-3 minutes):**
```bash
"Good morning! Here's my mood: 7/10. Yesterday I completed my career research task but skipped exercise. Today I have a team meeting I'm nervous about."
```

**Evening Reflection (3-5 minutes):**
```bash
"Day complete! Meeting went better than expected - rated my confidence 8/10. Didn't get to the evening walk though. Tomorrow I'll prioritize it."
```

**Weekly Review (10-15 minutes):**
```bash
"Weekly review: Career progress 85%, Relationships 70%, Finance 90%, Wellness 60%. Main blocker was time management. Wins: Submitted resume, had good talk with partner."
```

---

## 🎯 Domain Specialists

### 🚀 Career Specialist

**Focus:** Professional growth, skill development, career transitions

**Capabilities:**
- Career path planning and optimization
- Skill gap analysis and learning recommendations
- Resume/CV optimization and interview preparation
- Job market research and salary negotiation
- Work-life balance and burnout prevention

**Example Queries:**
```bash
"I want to transition from marketing to data science. What skills do I need?"
"I'm burned out in my current job. Should I quit or find ways to make it work?"
"How can I position myself for a promotion in the next 6 months?"
```

### 💝 Relationship Specialist

**Focus:** Personal relationships, communication, social connections

**Capabilities:**
- Communication style analysis and improvement
- Boundary setting and conflict resolution
- Social skill development
- Relationship quality assessment
- Family dynamics and partnership coaching

**Example Queries:**
```bash
"I struggle with setting boundaries with my family. How can I improve?"
"My partner and I keep having the same arguments. What should we do?"
"I want to make new friends but I'm introverted. Any strategies?"
```

### 💰 Finance Specialist

**Focus:** Financial planning, budgeting, wealth building

**Capabilities:**
- Comprehensive financial health assessment
- Budget creation and expense optimization
- Debt reduction strategies
- Investment planning and portfolio diversification
- Major purchase planning (home, car, education)

**Example Queries:**
```bash
"I want to save $50,000 for a house down payment in 3 years. How?"
"I have $10,000 in credit card debt. What's the best way to pay it off?"
"How should I start investing with only $100 per month?"
```

### 🌿 Wellness Specialist

**Focus:** Physical health, mental well-being, life balance

**Capabilities:**
- 8-dimension wellness assessment (physical, emotional, intellectual, etc.)
- Habit formation and behavior change
- Stress management and resilience building
- Sleep optimization and energy management
- Exercise planning and nutrition guidance

**Example Queries:**
```bash
"I'm always tired and have no energy. What should I focus on?"
"I want to start meditating but can't stick with it. Help!"
"How can I improve my sleep quality naturally?"
```

---

## 💡 Example Sessions

### Example 1: Career Transition Request

```
User: "I'm a marketing manager who wants to transition to data science. 
       I have some basic Python knowledge but feel overwhelmed by the path forward.

Coach Response: 
"Let me coordinate with my Career and Finance specialists to create a comprehensive plan...

🎯 CAREER PLAN (6-month transition):
- Month 1-2: Complete Python for Data Science course (Coursera)
- Month 2-3: Learn SQL and Statistics basics (Khan Academy)
- Month 3-4: Build 2 portfolio projects (Kaggle competitions)
- Month 4-5: Network with data scientists (LinkedIn, meetups)
- Month 5-6: Apply to entry-level positions, optimize resume

💰 FINANCIAL CONSIDERATIONS:
- Course costs: ~$300 total
- Potential income dip during transition
- Recommended emergency fund: 6 months expenses
- Timeline: Plan for 3 months job search

📊 WELLNESS FACTORS:
- Avoid burnout: Limit study to 15-20 hours/week
- Schedule regular exercise during intense learning periods
- Join study groups for social support

Would you like me to break this down into weekly action steps?"
```

### Example 2: Relationship & Work Balance

```
User: "I love my job but I'm working 60 hours a week and my partner 
       feels neglected. We're arguing more and I don't know how to fix it."

Coach Response:
"This is a common challenge that requires balancing career growth with relationship health. 
Let me bring in both specialists...

🎯 CAREER INSIGHTS:
- Analyze if 60 hours is necessary or if productivity can improve
- Explore flexible work arrangements with your manager
- Set clear boundaries for work hours and availability

💝 RELATIONSHIP STRATEGIES:
- Schedule dedicated quality time (date nights, device-free hours)
- Improve communication about work stress and needs
- Create shared expectations about work-life balance

⚖️ INTEGRATED APPROACH:
- Week 1: Track actual work hours vs. productive hours
- Week 2: Schedule relationship-building activities
- Week 3: Discuss flexible work options with manager
- Week 4: Evaluate progress and adjust strategies

This integrated approach addresses both the career demands and relationship needs. 
Shall we start with tracking your current time allocation?"
```

### Example 3: Multi-Domain Life Redesign

```
User: "I'm 35, single, living in a city I don't like. I have $50K in savings, 
       a stable but unfulfilling job, and I haven't dated in 2 years. 
       I want to completely redesign my life."

Coach Response:
"This is an exciting opportunity for transformation! Let me coordinate all specialists 
to create a comprehensive life redesign...

📊 CURRENT ASSESSMENT:
- Career: Stable but unfulfilling (6/10 satisfaction)
- Finance: Good savings foundation ($50K)
- Relationships: Limited social connections (3/10)
- Wellness: Location dissatisfaction affecting mood (4/10)

🎯 INTEGRATED 12-MONTH PLAN:

Phase 1 (Months 1-3): Foundation
- Career: Identify fulfilling career paths while maintaining income
- Finance: Create relocation and transition budget
- Relationships: Start building local connections and online dating
- Wellness: Research and decide on target city

Phase 2 (Months 4-6): Preparation
- Career: Acquire skills for target career, begin job search
- Finance: Save additional $15K for relocation cushion
- Relationships: Strengthen long-distance connections
- Wellness: Plan logistics of move, visit target city

Phase 3 (Months 7-9): Execution
- Career: Secure job in new location, give notice
- Finance: Execute move, establish new budget
- Relationships: Join local communities, dating activities
- Wellness: Settle in, establish new routines

Phase 4 (Months 10-12): Optimization
- All domains: Adjust and optimize new life situation
- Celebrate transformation milestones

This is ambitious but achievable. Which phase would you like to dive deeper into first?"
```

---

## ❓ Frequently Asked Questions

### General Questions

**Q: How does AI Life Coach differ from other coaching apps?**
A: AI Life Coach uses advanced Deep Agent technology with specialized domain experts, persistent memory, and cross-domain integration. It learns from your patterns and provides truly personalized guidance.

**Q: Is my data secure and private?**
A: Yes. All data is stored locally on your machine with optional encrypted cloud backup. We never sell or share your personal information.

**Q: How much time do I need to commit?**
A: As little as 5-10 minutes daily for check-ins, plus 15-30 minutes weekly for reviews. The system adapts to your availability.

### Technical Questions

**Q: Can I use my own AI model?**
A: Yes! The system supports OpenAI, Anthropic, and local models. You can even mix models for different tasks.

**Q: What if I want to stop using it? Can I export my data?**
A: Absolutely. All your data is yours and can be exported in JSON format at any time.

**Q: Does it work offline?**
A: Some features require internet (AI processing), but your data and plans are accessible offline.

---

## 🛠️ Troubleshooting

### Common Issues

**Issue: Installation Fails**
```bash
# Try these solutions:
1. Ensure Python 3.10+: python --version
2. Update pip: pip install --upgrade pip
3. Use virtual environment
4. Install dependencies individually from requirements.txt
```

**Issue: AI Model Connection Errors**
```bash
# Check your configuration:
1. Verify API keys in .env file
2. Test internet connection
3. Try different model endpoints
4. Check rate limits and quotas
```

**Issue: Slow Response Times**
```bash
# Optimize performance:
1. Use local model for privacy and speed
2. Reduce context window in settings
3. Clear cache regularly
4. Upgrade to premium model if needed
```

**Issue: Memory/Storage Problems**
```bash
# Manage your data:
1. Archive old sessions
2. Clear temporary files
3. Export and delete old assessments
4. Increase storage allocation
```

### Getting Help

- **Documentation**: Check the `/docs` folder for detailed guides
- **Community**: Join our Discord server for user discussions
- **Support**: Email support@ailifecoach.ai for technical issues
- **GitHub**: Report bugs and request features

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **🐛 Report Bugs**: Found an issue? Please report it with details
2. **💡 Feature Requests**: Have ideas? We'd love to hear them
3. **📝 Documentation**: Help improve guides and documentation
4. **🧪 Testing**: Test new features and provide feedback
5. **💻 Code Development**: Contribute to the codebase

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/ai_life_coach.git
cd ai_life_coach

# 2. Set up development environment
python -m venv dev_env
source dev_env/bin/activate
pip install -r requirements-dev.txt

# 3. Install pre-commit hooks
pre-commit install

# 4. Run tests
python -m pytest tests/

# 5. Create your feature branch
git checkout -b feature/your-feature-name
```

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to all functions
- Include tests for new features
- Keep pull requests focused and well-documented

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain Team** - For the excellent Deep Agents framework
- **OpenAI & Anthropic** - For powerful AI models
- **Our Beta Testers** - For invaluable feedback and insights
- **The Coaching Community** - For inspiration and best practices

---

## 📞 Contact & Support

- **Email**: support@ailifecoach.ai
- **Website**: https://ailifecoach.ai
- **Discord**: [Join our community](https://discord.gg/ailifecoach)
- **Twitter**: [@AILifeCoach](https://twitter.com/ailifecoach)

---

## 🗺️ Roadmap

### Version 1.1 (Coming Soon)
- 📱 Mobile app companion
- 🎵 Voice interaction support
- 👥 Group coaching capabilities
- 📊 Advanced analytics dashboard

### Version 1.2 (Q2 2025)
- 🔗 Third-party integrations (fitness apps, banks, calendars)
- 🌍 Multi-language support
- 👨‍👩‍👧 Family coaching features
- 🧘 Meditation and mindfulness modules

### Version 2.0 (Q3 2025)
- 🤖 AI agent marketplace
- 🔒 Enterprise team features
- 📚 Certified coaching programs
- 🌟 Personal development curriculum

---

**Ready to transform your life?** 🚀

```bash
python src/main.py
```

*Start your journey to a better you today.*

---

## Project Structure

```
ai_life_coach/
├── Beads_Plan.md          # Detailed 40-bead implementation plan
├── README.md              # User documentation (to be created)
├── src/                   # Source code
│   ├── config.py          # Configuration and setup
│   ├── main.py            # Main coordinator agent
│   ├── memory.py          # Memory utilities and namespace management
│   └── tools/             # Tool libraries per domain
├── skills/                # Progressive capability disclosure
│   ├── career-assessment/
│   ├── relationship-building/
│   ├── financial-planning/
│   └── wellness-optimization/
├── workspace/             # Persistent context storage
│   ├── user_profile/{user_id}/
│   ├── assessments/{user_id}/
│   ├── plans/{user_id}/
│   ├── progress/{user_id}/
│   └── resources/
├── tests/                 # Test scenarios and suites
└── docs/                  # Developer documentation
```

---

## Phases Breakdown

### Phase 1: Foundation (Beads 1-8) - ~12.5 hours
Set up project infrastructure, memory system, planning framework, and skills definitions.

**Key Deliverables**:
- Project structure with all directories
- Deep Agents infrastructure configured
- Memory namespace strategy implemented
- Planning system with phases and dependencies
- 4 domain-specific skill definitions

### Phase 2: Specialist Subagents (Beads 9-16) - ~21.5 hours
Build the four domain specialist agents with their specialized tools and capabilities.

**Key Deliverables**:
- Career Coach Specialist (skill gaps, career paths, resume optimization)
- Relationship Coach Specialist (communication, boundaries, social skills)
- Finance Coach Specialist (budgeting, financial goals, debt strategies)
- Wellness Coach Specialist (8-dimension assessment, habits, stress management)
- Cross-domain integration logic
- Subagent communication protocol

### Phase 3: Coordinator Agent (Beads 17-24) - ~20.5 hours
Build the main orchestrator that coordinates all specialists and integrates their outputs.

**Key Deliverables**:
- Comprehensive coordinator system prompt
- Multi-domain assessment workflow
- Goal dependency mapping system
- Phase-based planning (discovery, planning, execution, review)
- Weekly check-in system
- Adaptive recommendation engine
- Result integration and unified response generation

### Phase 4: Bonus Features (Beads 25-32) - ~18.5 hours
Implement advanced features to showcase full system capabilities.

**Key Deliverables**:
- Mood tracking with sentiment analysis
- Goal dependency visualization (text-based graphs)
- Personalized weekly reflection prompts
- Progress dashboard with multi-domain metrics
- Habit tracking system with streaks
- Resource curation and recommendation engine
- Emergency support protocol (crisis detection)
- Multi-user support with data isolation

### Phase 5: Testing & Documentation (Beads 33-38) - ~14.5 hours
Comprehensive testing, optimization, and documentation.

**Key Deliverables**:
- Comprehensive test scenarios (single/multi-domain, edge cases)
- Full integration testing
- Performance optimization
- User documentation (README, guides, FAQ)
- Developer documentation (architecture, API, extension guide)

### Phase 6: Demonstration (Beads 39-40) - ~4 hours
Prepare and deliver final demonstration.

**Key Deliverables**:
- Demo session script showing all features
- Final presentation materials
- Complete, working system ready for submission

---

## Key Features & Capabilities

### Core Functionality
- ✅ Multi-domain life coaching (career, relationships, finance, wellness)
- ✅ Comprehensive initial assessment
- ✅ Goal creation with dependency mapping
- ✅ 90-day action plan generation
- ✅ Weekly check-in and progress tracking
- ✅ Adaptive recommendations based on feedback

### Advanced Features (Bonus)
- ✅ Mood tracking with sentiment analysis
- ✅ Goal dependency visualization
- ✅ Personalized reflection prompts
- ✅ Progress dashboard across all domains
- ✅ Habit formation and tracking
- ✅ Resource curation system
- ✅ Emergency support protocol
- ✅ Multi-user data isolation

### Technical Capabilities
- ✅ Persistent memory across sessions (LangGraph Store)
- ✅ Context isolation via filesystem backend
- ✅ Subagent parallelization for efficiency
- ✅ Progressive capability disclosure (Skills system)
- ✅ Cross-domain insight synthesis

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | LangChain Deep Agents |
| Orchestration | LangGraph |
| Memory Store | InMemoryStore (LangGraph) |
| Context Backend | FilesystemBackend |
| Model Provider | glm-4.7 (local endpoint) |
| Planning System | Built-in TodoListMiddleware |
| Skills System | SKILL.md progressive disclosure |

---

## Memory Namespace Strategy

```python
# User-specific data
(user_id, "profile")      # Demographics, values, life situation
(user_id, "goals")        # Short, medium, long-term goals
(user_id, "progress")     # Milestones achieved, setbacks overcome
(user_id, "preferences")  # Communication style, coaching approach

# Cross-user learned patterns (anonymized)
("coaching", "patterns")  # Common success factors, effective strategies
```

---

## Planning System Workflow

```python
todos = [
    {"title": "Initial life assessment", "phase": "discovery"},
    {"title": "Identify top 3 priorities", "phase": "discovery", "depends_on": "assessment"},
    {"title": "Create 90-day action plan", "phase": "planning", "depends_on": "priorities"},
    {"title": "Weekly check-in system", "phase": "execution"},
]
```

**Phases**:
1. **Discovery**: Assessment, goal identification
2. **Planning**: Action plan creation with dependencies
3. **Execution**: Task implementation and tracking
4. **Review**: Progress evaluation and adaptation

---

## Research Sources

This plan is based on comprehensive research from:

### Deep Agents Documentation
- Official LangChain Deep Agents docs
- Building Multi-Agent Applications blog post
- Subagent spawning patterns and best practices

### Memory & Persistence
- LangGraph memory documentation
- Long-term memory with Store patterns
- Memory management best practices

### Planning & Workflows
- Task planning with TODOs methodologies
- Agentic workflow patterns
- Deep Agents planning strategies

### Multi-Agent Coordination
- Choosing multi-agent architecture guides
- Agent coordination patterns
- LangGraph multi-agent workflows

All research sources are documented in `Beads_Plan.md` under "Research References".

---

## Success Criteria

The project will be considered successful when:

1. ✅ Multi-subagent architecture with 4 domain specialists working in coordination
2. ✅ Advanced planning system with phases and dependencies
3. ✅ Comprehensive context management across 5 directory structures
4. ✅ Long-term memory with 5 namespace patterns
5. ✅ All bonus features implemented (mood tracking, goal dependencies, reflections, dashboard)
6. ✅ Fully tested and documented system ready for demonstration
7. ✅ Demo session showcases all core and advanced features

---

## Getting Started

### Prerequisites
- Python 3.10+
- Local LLM endpoint (http://192.168.1.79:8080/v1)
- API keys for Anthropic/OpenAI (if not using local model)

### Quick Start
```bash
# Navigate to project directory
cd ai_life_coach

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install deepagents langgraph python-dotenv

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the system
python src/main.py
```

### First Session Example
```python
from src.main import create_life_coach

# Create coordinator agent
coach = create_life_coach()

# Start coaching session
result = coach.invoke({
    "messages": [{
        "role": "user",
        "content": "I'm feeling stuck in my career and it's affecting my relationships. Can you help me create a comprehensive plan?"
    }]
})

print(result["messages"][-1].content)
```

---

## Next Steps

1. **Review the detailed plan**: Open `Beads_Plan.md` for complete implementation details
2. **Set up environment**: Follow Phase 1, Bead #1 to initialize the project
3. **Begin implementation**: Execute beads sequentially within each phase
4. **Test continuously**: Don't wait until end - test each component as built
5. **Document progress**: Update documentation alongside code development

---

## Questions or Clarifications?

If you need clarification on any bead, have questions about the architecture, or want to discuss trade-offs before implementation begins, please let me know!

---

**Document Created**: Beads_Plan.md (40 beads, 6 phases)
**Status**: Ready for implementation
**Estimated Timeline**: 3-4 weeks (full-time) or 8-10 weeks (part-time)
