<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 5: Multi-Agent Applications</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/AIE9/tree/main/00_AIE_Quicklinks)

| Session Sheet | Recording     | Slides        | Repo         | Homework      | Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
|[Multi-Agent Applications](https://github.com/AI-Maker-Space/AIE9/blob/main/00_Docs/Session_Sheets/05_Multi-Agent_Applications.md) | Coming soon! | Coming soon! | You are here! | Coming soon! | Coming soon! |


### Outline:

**BREAKOUT ROOM #1:**
- Task 1: Dependencies & Environment Setup
- Task 2: Understanding Multi-Agent Systems
- Task 3: Building a Supervisor Agent Pattern
- Task 4: Adding Tavily Search for Web Research
     - **Activity #1**: Add a Custom Specialist Agent

**BREAKOUT ROOM #2:**
- Task 5: Agent Handoffs Pattern
- Task 6: Building a Wellness Agent Team
- Task 7: Context Engineering & Optimization
- Task 8: Visualizing and Debugging with LangSmith
     - **Activity #2**: Multi-Agent Consultation Pattern

### Prerequisites:

#### 1. API Keys Required

You'll need API keys for:
- **OpenAI** - For GPT-5.2 (supervisor) and GPT-4o-mini (specialist agents)
- **Tavily** - For web search capabilities (free tier available at [tavily.com](https://www.tavily.com/))
- **LangSmith** (optional) - For tracing and debugging

### Steps to Run:

1. Install UV, which you can do through [this resource](https://docs.astral.sh/uv/#getting-started)
2. Run the command `uv sync`
3. Open your Jupyter notebook and select `.venv` for your kernel.

# Build

Run the notebook!

# Ship

- Customize your multi-agent system with one of the following enhancements:
     - Add a new specialist agent to the team (e.g., a Fitness Coach, Nutrition Expert)
     - Implement a different multi-agent pattern (Network/Swarm, Debate)
     - Add human-in-the-loop approval for certain agent decisions
     - Implement context summarization to manage long conversations
- Create a diagram showing your multi-agent architecture
- Record a Loom video walking through the notebook, the questions, and your enhancements!

# Share

- Show your multi-agent architecture diagram in a Loom video and explain the agent interactions
- Make a social media post about your multi-agent wellness system and tag @AIMakerspace
- Share 3 lessons learned
- Share 3 lessons not learned

Here's a template to get your post started!

```
Built my first Multi-Agent AI System using LangGraph!

What I learned about multi-agent patterns:
1. Supervisor pattern = orchestrator that routes to specialist agents
2. Handoffs = agents can transfer control to each other based on expertise
3. Context engineering is critical - garbage in, garbage out

Key insight: Don't build multi-agents unless you really need them!
Start simple, add complexity only when necessary.

A huge shoutout to @AI Makerspace for making this possible.

#AI #Agents #LangGraph #MultiAgent #BuildInPublic
```

<details>
<summary><h3>Advanced Build (Optional): Personal Wellness Planner with File I/O</h3></summary>

> **Note**: Completing an Advanced Build earns full credit **in place of** doing the base assignment notebook questions/activities.

Build a **Personal Wellness Planner** - a multi-agent system that can create, save, and manage personalized wellness plans using file system tools.

### Requirements

**1. Multi-Agent Architecture:**
- A **Planner Supervisor** (GPT-5.2) that coordinates the planning process
- Specialist agents for each wellness domain (Exercise, Nutrition, Sleep, Stress)
- A **File Manager Agent** that handles reading/writing wellness plans

**2. File System Tools:**
Create tools that allow agents to:
- `save_wellness_plan(filename, content)` - Save a plan to a markdown file
- `load_wellness_plan(filename)` - Load an existing plan
- `list_saved_plans()` - List all saved wellness plans
- `append_to_plan(filename, section, content)` - Add a section to an existing plan

**3. Workflow:**
```
User: "Create a wellness plan for someone who wants to lose weight and reduce stress"
                           │
                           ▼
                 ┌─────────────────┐
                 │ Planner Super-  │
                 │ visor (GPT-5.2) │
                 └────────┬────────┘
                          │ coordinates
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Exercise │    │ Nutrition│    │  Stress  │
   │  Agent   │    │  Agent   │    │  Agent   │
   └────┬─────┘    └────┬─────┘    └────┬─────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
               ┌─────────────────┐
               │  File Manager   │
               │     Agent       │
               └────────┬────────┘
                        │
                        ▼
              📄 wellness_plan_2024.md
```

**4. Example Output File (`plans/wellness_plan_weight_loss.md`):**
```markdown
# Personal Wellness Plan: Weight Loss & Stress Reduction
Generated: 2024-01-26

## Goals
- Lose 15 pounds over 3 months
- Reduce daily stress levels

## Exercise Plan
- Monday/Wednesday/Friday: 30-min cardio
- Tuesday/Thursday: Strength training
- Weekend: Active recovery (walking, yoga)

## Nutrition Plan
- Daily calorie target: 1,800 cal
- Meal prep on Sundays
- Increase protein intake to 100g/day

## Stress Management Plan
- Morning: 10-min meditation
- Evening: Digital detox after 8pm
- Weekly: One relaxing activity (bath, nature walk)

## Weekly Check-in Template
- [ ] Completed workouts: _/5
- [ ] Stayed within calorie target: _/7 days
- [ ] Meditation sessions: _/7
```

### Bonus Features (optional)
- Add a **Progress Tracker Agent** that can update plans with completed items
- Implement **plan versioning** (save revisions with timestamps)
- Add **web search** to include latest wellness research in plans

### Resources
- [LangGraph Hierarchical Teams](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/)
- [LangChain File System Tools](https://python.langchain.com/docs/integrations/tools/filesystem/)

### Submitting the Advanced Build
1. Complete all steps of the Main Assignment above
2. Include your multi-agent implementation with file I/O tools
3. Include at least 2 example generated wellness plans in a `plans/` folder
4. Document your architecture with a diagram
5. Add, commit and push your modifications to your repository

When submitting, provide:
- Your Loom video link demonstrating the planner creating and saving a wellness plan
- The GitHub URL to your completed notebook with the Advanced Build
- Screenshots of generated plan files

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
2. **IMPORTANT:** Start Cursor from the `05_Multi_Agent_with_LangGraph` folder (you can also use the _File -> Open Folder_ menu option of an existing Cursor window)
3. Answer Questions 1 - 4 using the `##### Answer:` markdown cell below them.
4. Complete Activity #1 and Activity #2 in the notebook.
5. Add, commit and push your modified `Multi_Agent_Applications_Assignment.ipynb` to your GitHub repository.

When submitting your homework, provide:
- Your Loom video link
- The GitHub URL to your completed notebook
