<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 3: The Agent Loop</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/AIE9/tree/main/00_AIE_Quicklinks)

| 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
|[The Agent Loop](https://github.com/AI-Maker-Space/AIE9/blob/main/00_Docs/Session_Sheets/03_The_Agent_Loop.md) | Coming soon! | Coming soon! | You are here! | Coming soon! | Coming soon! |


### Outline:

🤜 BREAKOUT ROOM #1:
- Task 1: Dependencies
- Task 2: Environment Variables
- Task 3: LangChain Core Concepts (Runnables & LCEL)
- Task 4: Understanding the Agent Loop
- Task 5: Building Your First Agent with `create_agent()`
     - 🏗️ ACTIVITY #1: Create a Custom Tool

🤜 BREAKOUT ROOM #2:
- Task 6: Loading & Chunking Documents
- Task 7: Setting up Qdrant Vector Database
- Task 8: Creating a RAG Tool
- Task 9: Introduction to Middleware
- Task 10: Building Agentic RAG with Middleware
     - 🏗️ ACTIVITY #2: Enhance the Agent

### Steps to Run:

1. Install UV, which you can do through [this resource](https://docs.astral.sh/uv/#getting-started)
2. Run the command `uv sync`
3. Open your Jupyter notebook and select `.venv` for your kernel.

# Build 🏗️

Run the notebook!

# Ship 🚢

- Add one of the following enhancements (or whatever augmentations suit your use case) to the agentic RAG system:
     - Add a new tool (BMI calculator, calorie estimator, etc.)
     - Create custom middleware (logging, guardrails, rate limiting)
     - Improve the RAG tool (metadata filtering, reranking, citations)
     - Add conversation memory to the agent
- Make a simple diagram of your agent architecture
- Run the notebook
- When you're finished with augmentations, compare your enhanced agent to the baseline!
- Record a Loom video walking through the notebook, the questions in the notebook, and your addition!

# Share 🚀
- Show your Agent in a Loom video and explain the diagram
- Make a social media post about your final application and tag @AIMakerspace
- Share 3 lessons learned
- Share 3 lessons not learned

Here's a template to get your post started!

```
🚀 Exciting News! 🎉

I just built my first AI Agent using LangChain 1.0's create_agent API! 🤖💼

🔍 Three Key Takeaways:
1️⃣ The agent loop is the foundation of all AI agents - understanding it unlocks so much potential! 🧠✨
2️⃣ Middleware lets you hook into every step of the agent loop for logging, guardrails, and more! 🔧📈
3️⃣ Agentic RAG gives agents control over when to retrieve - way more flexible than traditional RAG! 🔄📚

A huge shoutout to @AI Makerspace for their invaluable resources and guidance. 🙌

Looking forward to more agentic adventures! 🌟 Feel free to connect if you'd like to chat more about it! 🤝

#AI #Agents #LangChain #BuildInPublic
```

### 🚧 Advanced Build (Optional): Human-in-the-Loop Middleware

Implement a Wellness RAG Agent with Human-in-the-Loop Middleware.

- Use `HumanInTheLoopMiddleware` to pause agent execution before tool calls
- Create a custom approval function that lets users approve, reject, or edit tool inputs
- Add the middleware to your wellness agent
- Test with queries that trigger different tools

This pattern is critical for production systems requiring human oversight!

> NOTE: Can be completed in lieu of full notebook

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
2. **IMPORTANT:** Start Cursor from the `03_The_Agent_Loop` folder (you can also use the _File -> Open Folder_ menu option of an existing Cursor window)
3. Answer Questions 1 - 4 using the `##### ✅ Answer:` markdown cell below them.
4. Complete Activity #1 and Activity #2 in the notebook.
5. Add, commit and push your modified `The_Agent_Loop_Assignment.ipynb` to your GitHub repository.

When submitting your homework, provide:
- Your Loom video link
- The GitHub URL to your completed notebook
