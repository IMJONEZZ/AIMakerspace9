<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 7: Deep Agents</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/AIE9/tree/main/00_AIE_Quicklinks)

| Session Sheet | Recording     | Slides        | Repo         | Homework      | Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Deep Agents](https://github.com/AI-Maker-Space/AIE9/blob/main/00_Docs/Session_Sheets/07_Deep_Agents.md) |[Recording!](https://us02web.zoom.us/rec/share/I__BI6_mDP_YYk0beYkS5SAaURg9VZ5k_dC5K_OLEkzHbPca9McefKJlhhwitsQN.0vXRPsAywWyFE0RJ) <br> passcode: `iBt9a&Mi`| [Session 7 Slides](https://www.canva.com/design/DAHAT1jy3nk/ZfmYrrdT2mL10GetpfRDnw/edit?utm_content=DAHAT1jy3nk&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [Session 7 Assignment: Deep Agents](https://forms.gle/95UFWAzLTYzr7cj4A) <br><br> [Project Ideation](https://forms.gle/nnCEmnZUBKtbThB78) | [Feedback 2/3](https://forms.gle/MbrAjqYFwCpJgYEB8) |


### Outline:

**BREAKOUT ROOM #1: Deep Agent Foundations**
- Task 1: Dependencies & Setup
- Task 2: Understanding Deep Agents
- Task 3: Planning with Todo Lists
- Task 4: Context Management with File Systems
- Task 5: Basic Deep Agent
     - **Activity #1**: Build a Research Agent

**BREAKOUT ROOM #2: Advanced Features & Integration**
- Task 6: Subagent Spawning
- Task 7: Long-term Memory Integration
- Task 8: Skills - On-Demand Capabilities
- Task 9: Using deepagents-cli
- Task 10: Building a Complete Deep Agent System
     - **Activity #2**: Build a Wellness Coach Agent

### Prerequisites:

#### 1. API Keys Required

You'll need API keys for:
- **Anthropic** - For Claude (default for Deep Agents)
- **OpenAI** - For GPT models (used by subagents)
- **LangSmith** (optional) - For tracing and debugging
- **Tavily** (optional) - For web search capabilities

Copy the sample environment file and fill in your API keys:
```bash
cp .env.sample .env
# Then edit .env with your actual API keys
```

### Steps to Run:

1. Install UV, which you can do through [this resource](https://docs.astral.sh/uv/#getting-started)
2. Run the command `uv sync`
3. Open your Jupyter notebook and select `.venv` for your kernel.

# Build

Run the notebook!

# Ship

- Customize your Deep Agent with one of the following enhancements:
     - Add additional specialist subagents (e.g., Fitness Tracker, Habit Coach)
     - Implement a different context management strategy (database-backed, cloud storage)
     - Create custom skills for domain-specific tasks
     - Build a multi-user system with isolated workspaces
- Create a diagram showing your Deep Agent architecture
- Record a Loom video walking through the notebook, the questions, and your enhancements!

# Share

- Show your Deep Agent architecture diagram in a Loom video and explain the four key elements
- Make a social media post about your Deep Agent wellness system and tag @AIMakerspace
- Share 3 lessons learned
- Share 3 lessons not learned

Here's a template to get your post started!

```
Built my first Deep Agent using the deepagents package!

What I learned about the 4 key elements:
1. Planning = todo lists that persist task state
2. Context Management = file systems for storing/retrieving info
3. Subagent Spawning = delegating to specialists without context bloat
4. Long-term Memory = remembering across sessions with LangGraph Store

Key insight: Deep Agents handle complexity that would overwhelm simple agent loops!
Planning is really just context engineering.

A huge shoutout to @AI Makerspace for making this possible.

#AI #Agents #DeepAgents #LangGraph #BuildInPublic
```

<details>
<summary><h3>Advanced Build (Optional): AI Life Coach with Multi-Domain Expertise</h3></summary>

> **Note**: Completing an Advanced Build earns full credit **in place of** doing the base assignment notebook questions/activities.

Build an **AI Life Coach** - a Deep Agent system that provides comprehensive life guidance across multiple domains with persistent memory and adaptive recommendations.

### Requirements

**1. Multi-Subagent Architecture:**
- **Life Coach Coordinator** (Claude) that orchestrates the coaching process
- Specialist subagents for each life domain:
  - **Career Coach**: Job search, skill development, professional growth
  - **Relationship Coach**: Communication, boundaries, social connections
  - **Finance Coach**: Budgeting, saving, financial goals
  - **Wellness Coach**: Health, fitness, mental wellbeing

**2. Advanced Planning System:**
```python
# Multi-phase planning with dependencies
todos = [
    {"title": "Initial life assessment", "phase": "discovery"},
    {"title": "Identify top 3 priorities", "phase": "discovery", "depends_on": "assessment"},
    {"title": "Create 90-day action plan", "phase": "planning", "depends_on": "priorities"},
    {"title": "Weekly check-in system", "phase": "execution"},
]
```

**3. Context Management Strategy:**
- `user_profile/` - Long-term user information
- `assessments/` - Completed assessments and reflections
- `plans/` - Active and archived action plans
- `progress/` - Weekly check-ins and milestones
- `resources/` - Curated articles, exercises, worksheets

**4. Workflow:**
```
User: "I feel stuck in my career and it's affecting my relationships"
                           │
                           ▼
                 ┌─────────────────┐
                 │  Life Coach     │
                 │  Coordinator    │
                 └────────┬────────┘
                          │ assesses & plans
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │  Career  │    │Relation- │    │ Wellness │
   │  Coach   │    │ship Coach│    │  Coach   │
   └────┬─────┘    └────┬─────┘    └────┬─────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
               ┌─────────────────┐
               │ Integrated Plan │
               │ with cross-     │
               │ domain insights │
               └─────────────────┘
```

**5. Memory Integration:**
```python
# Namespaces for comprehensive memory
(user_id, "profile")      # Demographics, values, life situation
(user_id, "goals")        # Short, medium, long-term goals
(user_id, "progress")     # Milestones achieved, setbacks overcome
(user_id, "preferences")  # Communication style, coaching approach
("coaching", "patterns")  # Learned patterns across users (anonymized)
```

### Bonus Features (optional)
- Implement **mood tracking** with sentiment analysis of check-ins
- Add **goal dependency mapping** (e.g., career growth enables financial goals)
- Create **weekly reflection prompts** personalized to current challenges
- Build a **progress dashboard** showing growth across all domains

### Resources
- [Deep Agents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangGraph Memory Documentation](https://langchain-ai.github.io/langgraph/concepts/memory/)
- [Context Management Best Practices](https://www.blog.langchain.com/context-management-for-deepagents/)

### Submitting the Advanced Build
1. Complete all steps of the Main Assignment above
2. Include your multi-subagent implementation with all 4 Deep Agent elements
3. Include an architecture diagram showing subagent relationships
4. Document your context management and memory namespace strategy
5. Add, commit and push your modifications to your repository

When submitting, provide:
- Your Loom video link demonstrating the Life Coach handling a multi-domain request
- The GitHub URL to your completed notebook with the Advanced Build
- Screenshots of generated plans and progress tracking

</details>

# Submitting Your Homework

## Main Assignment

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your AIE9 repo:
    - _(You should have completed this process already.)_ For your initial repo setup, see [Initial_Setup](https://github.com/AI-Maker-Space/AIE9/tree/main/00_Docs/Prerequisites/Initial_Setup)
    - To get the latest updates from AI Makerspace into your own AIE9 repo, run the following commands:
    ```
    git checkout main
    git pull upstream main
    git push origin main
    ```
2. **IMPORTANT:** Start Cursor from the `07_Deep_Agents` folder (you can also use the _File -> Open Folder_ menu option of an existing Cursor window)
3. Answer Questions 1 - 4 using the `##### Answer:` markdown cell below them.
4. Complete Activity #1 and Activity #2 in the notebook.
5. Add, commit and push your modified `Deep_Agents_Assignment.ipynb` to your GitHub repository.

When submitting your homework, provide:
- Your Loom video link
- The GitHub URL to your completed notebook
