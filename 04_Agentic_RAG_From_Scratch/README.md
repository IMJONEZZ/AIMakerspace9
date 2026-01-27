<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 4: Agentic RAG From Scratch</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/AIE9/tree/main/00_AIE_Quicklinks)

| Session Sheet | Recording     | Slides        | Repo         | Homework      | Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Vibe Check!](../00_Docs/Session_Sheets/04_Agentic_RAG_From_Scratch.md) |[Recording!](https://us02web.zoom.us/rec/share/HY0f8Ovri36rF9lRYPs-I1qckTkEftcuxg0zUXmLSI9_tCxJQxXYgPXejzMxYbuC.nJypOGHZUaPBaVZd) <br> passcode: `02y.=1pO`| [Session 4 Slides](https://www.canva.com/design/DAG-EIVcUxE/WH_2fNB39mBUmOb-zeB8WA/edit?utm_content=DAG-EIVcUxE&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [Session 4 Assignment: Agentic RAG](https://forms.gle/wJWWTyQXhveVLaKx8) | [Feedback 1/22](https://forms.gle/dTuPZjRVnUMQy5x76) |


### Outline:

**BREAKOUT ROOM #1:**
- Task 1: Dependencies & Ollama Setup
- Task 2: LangGraph Core Concepts (StateGraph, Nodes, Edges)
- Task 3: Building a ReAct Agent from Scratch
- Task 4: Adding Tools to Your Agent
     - **Activity #1**: Implement a Custom Routing Function

**BREAKOUT ROOM #2:**
- Task 5: Loading & Chunking with LangChain
- Task 6: Setting up Qdrant with Local Embeddings
- Task 7: Creating a RAG Tool
- Task 8: Building Agentic RAG from Scratch
     - **Activity #2**: Extend the Agent with Memory

### Prerequisites:

#### 1. Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com/):

- **macOS**: `brew install ollama` or download the app
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`
- **Windows**: Download the installer from the website

#### 2. Start Ollama Server

```bash
ollama serve
```

#### 3. Pull Required Models

```bash
# Pull the chat model (~12GB download)
ollama pull gpt-oss:20b

# Pull the embedding model (~622MB download)
ollama pull embeddinggemma
```

> **Note**: If you don't have enough RAM/VRAM for `gpt-oss:20b`, you can use `llama3.2:3b` as an alternative. Update the model name in the notebook accordingly.

### Steps to Run:

1. Install UV, which you can do through [this resource](https://docs.astral.sh/uv/#getting-started)
2. Run the command `uv sync`
3. Make sure Ollama is running: `ollama serve`
4. Open your Jupyter notebook and select `.venv` for your kernel.

# Build

Run the notebook!

# Ship

- Customize your from-scratch agent with one of the following enhancements:
     - Add a new node to the graph (e.g., a "thinking" node that reasons before responding)
     - Implement memory/conversation history that persists across invocations
     - Add parallel tool execution when multiple tools are called
     - Create a custom routing strategy (e.g., route based on query type)
- Make a diagram of your custom agent architecture showing the graph structure
- Record a Loom video walking through the notebook, the questions, and your enhancements!

# Share

- Show your Agent architecture diagram in a Loom video and explain the graph flow
- Make a social media post about your local AI agent and tag @AIMakerspace
- Share 3 lessons learned
- Share 3 lessons not learned

Here's a template to get your post started!

```
Built my first AI Agent FROM SCRATCH using LangGraph + local open-source models!

What I learned building with StateGraph primitives:
1. Nodes = computation, Edges = routing decisions
2. Conditional edges enable dynamic agent behavior based on state
3. Local models with Ollama = privacy + no API costs

Running gpt-oss:20b + embeddinggemma locally for a fully private RAG agent!

A huge shoutout to @AI Makerspace for making this possible.

#AI #Agents #LangGraph #OpenSource #LocalAI #BuildInPublic
```

<details>
<summary><h3>🚧 Advanced Build (Optional): Human-in-the-Loop with Interrupt</h3></summary>

> **Note**: Completing an Advanced Build earns full credit **in place of** doing the base assignment notebook questions/activities.

Implement a Human-in-the-Loop (HITL) pattern using LangGraph's interrupt feature:

- Add a checkpoint before tool execution using `interrupt_before=["tools"]`
- Create a mechanism to approve, reject, or modify tool inputs
- Resume execution after human approval

This pattern is critical for production systems requiring human oversight!

**Resources:**
- [LangGraph Human-in-the-Loop Guide](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)

#### Submitting the Advanced Build:
1. Complete all steps of the Main Assignment above
2. Document your HITL implementation: what you built, how it works, and example outputs
3. Add, commit and push your modifications to your repository

When submitting, provide:
- Your Loom video link demonstrating the HITL workflow
- The GitHub URL to your completed notebook with the Advanced Build

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
2. **IMPORTANT:** Start Cursor from the `04_Agentic_RAG_From_Scratch` folder (you can also use the _File -> Open Folder_ menu option of an existing Cursor window)
3. Answer Questions 1 - 4 using the `##### Answer:` markdown cell below them.
4. Complete Activity #1 and Activity #2 in the notebook.
5. Add, commit and push your modified `Agentic_RAG_From_Scratch_Assignment.ipynb` to your GitHub repository.

When submitting your homework, provide:
- Your Loom video link
- The GitHub URL to your completed notebook
