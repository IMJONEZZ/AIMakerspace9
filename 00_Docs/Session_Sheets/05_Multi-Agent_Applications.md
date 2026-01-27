# Session #5: 🔄 Multi-Agent Applications

🎯 Understand when to add additional agents to optimize context and how to construct agent teams using typical patterns.

📚 **Learning Outcomes**
- Understand multi-agent systems, and typical multi-agent patterns
- Learn when to add more agents to optimize context 
- Visualize, debug, and interact with your agent applications

🧰 **New Tools**
- Agent Tools: [Tavily Search](https://www.tavily.com/?utm_term=tavily&utm_campaign=Tavily+Brand+-+General&utm_source=adwords&utm_medium=ppc&matchtype=e&device=c&utm_content=789180622957_&utm_position=&gad_source=1&gad_campaignid=23289739393&gbraid=0AAAABB_ZBWrAq-75KiYAuqIBFNb0FjkZm&gclid=CjwKCAiAj8LLBhAkEiwAJjbY79-3SS5jmAv3MoEzecsB7GrPm_P9cbu_KSKwffFEhBjTNK4DV31q8BoC1rEQAvD_BwE)
- Visualization, Interaction, and Debugging: [LangSmith Studio](https://docs.langchain.com/langsmith/studio)

## 📛 Required Tooling & Account Setup
In addition to the tools we've already learned, in this session you'll need:
    
1. [Tavily API](https://www.tavily.com/)
   
## 📜 Recommended Reading

- [Don’t Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) (June 2025)
- [Context Rot](https://research.trychroma.com/context-rot) (July 2025)
- [Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents), by LangGraph

# 🗺️ Overview

# Overview

In Session 5, we’ll cover multi-agent applications!  This class of LLM applications adds an additional layer of complexity to our ability to create agentic applications.

The same core concepts will be used to understand multi-agent systems as we used to understand agents in the first place, including tools, enhanced retrieval and search (a.k.a. “Fancy RAG), the Reasoning-Action pattern and function calling.

There are other frameworks you’ll hear about for building multi-agent applications; we’ve covered many of them on [YouTube](https://www.youtube.com/playlist?list=PLrSHiQgy4VjHDm_5pg09Ps9Yg5Eq7X7gO).

Multi-agent systems allow us to functionally split up and allocate work to our agents based on their specific responsibilities. This allows us to create clean conceptual models that are quite useful and often align with the way work is split up today between humans in different roles or by a single human completing multiple tasks towards the solution of a problem.

# 🤖 Multi-Agent Systems

If we define an agent as “a system that can leverage reasoning to make dynamic decisions in an application flow,” we can extend this definition directly to multiple agents.

<aside>
📖

Multi-Agent System: A system that can leverage reasoning from multiple independent agents to make dynamic decisions in an application flow

</aside>

According to LangChain, “multi-agent” means “**multiple independent actors powered by language models connected in a specific way.**” [[Ref](https://blog.langchain.dev/langgraph-multi-agent-workflows/)].

This all makes multi-agent systems sound quite abstract and confusing.  However, we can clarify this by saying that the ***agents within multi-agent systems are specialized LLMs*.** 

What is important to understand now is that *each agent/LLM in a multi-agent system must play a specialized role*.

What role should each agent play?  It depends - on the application and the implementation.

# ♾️ Many vs. One: Why?

Why would we need many agents if it’s hard enough to set up a single agent in a useful way?

> “Agents are useful when you need an LLM to determine the workflow of an app” ~ [**✅ When to use agents / ⛔ when to avoid them](https://huggingface.co/blog/smolagents#%E2%9C%85-when-to-use-agents--%E2%9B%94-when-to-avoid-them)** by Hugging Face
> 

Well, yes, it is. 

And we should use many agents only when we really need to use many agents.

Think about the questions you should be able to answer before building an agentic system of any kind, even with just one agent:

> Do I **really need flexibility** in the **workflow** to efficiently **solve the task** at hand?
> 

We always want to consider how much agency we need in our workflows, as we know “agentic systems consist of both workflows and agents (and everything in between.” [[Ref](https://blog.langchain.com/how-to-think-about-agent-frameworks/)]

We might ask the question a slightly different way for a single agent system so that it is extensible to multiple agents:

> Do I really need **dynamic reasoning** to solve the task (or problem) more effectively than a rigid workflow could?
> 

If we use this kind of approach, we can more easily understand the Keep-It-Simple-Stupid approaches that we’re always reminded of by leading researchers and labs; e.g.,

> “When building applications with LLMs, we recommend **finding the simplest solution possible**, and *only increasing complexity when needed*.” ~ [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), by Anthropic
> 

The additional benefit of this approach is that it scales to multiple agents.

> Do I really need several specialized **dynamic** **reasoning** machines collaborating to solve the task (or problem) **more effectively** than a single agent could?
> 

In other words, for one agent, how much agency over workflow do I need?

- Do I have too many if-elseif-elseif-else statements?

And then, to add an additional agent, how much additional agency over the agentic workflow I already have do I need. Again:

- Do I have too many if-elseif-elseif-else statements?

While agents can give rise to complexity, the key benefit of setting up systems using a multi-agent framework is to **reduce complexity**. This gives us more clarity on our problem and solution, and ideally, even better performance.

Here are the techniques we’ll use to reduce complexity and increase performance by going from one to many:

1. 🧑‍🤝‍🧑 **Grouping** tools and responsibilities: analogous to how we separate work between people in an organization.
2. 🗨️ **Separating** prompts and few-shot examples: toward using multiple fine-tuned, specialized LLMs. 
3. 🧩 Easier **piecewise optimization**: using a simple conceptual model with plug-and-play pieces allows us to focus on each piece without jeopardizing the whole

Given these core ideas, here are a few thinking questions!

- 🙋 Could you use a single monolithic agentic application and/or mega prompt instead of a multi-agent setup?
    - ✅ Likely, Yes. But, as we’ll see, that would be stupid for many reasons.
- 🙋 Theoretically, if we had achieved AGI would there be any need for multiple agents?
    - ✅ Technically, no.  However, from a business perspective, it would make sense to “right-size” the LLMs we need, making them less general and more specific, and eliminate any additional compute and model capability we don’t need before deploying our product at scale to many users. Also, from a context engineering perspective, this would simply not be feasible by the limitations of LLM technology!

# 🪟 Context Engineering for Multi-Agent Systems

Insofar as definitive work exists for this space, we can point to a few leading thinkers who have developed some of the latest and greatest ideas:

1. **Dex Horthy: 12-Factor Agents [[GitHub](https://github.com/humanlayer/12-factor-agents?tab=readme-ov-file), [Talk](https://www.youtube.com/watch?v=8kMaTybvDUw)]**

> In the spirit of Heroku's 12 Factor Apps (https://12factor.net/), these principles focus on the engineering practices that make LLM applications more reliable, scalable, and maintainable. Even as models get exponentially more powerful, these core techniques will remain valuable.
> 

<aside>
💡

Big idea: own your context window and treat it like prime real estate; minimize “context utilization”

</aside>

1. **swyx: Agent Engineering [[Blog](https://www.latent.space/p/agent), [Talk](https://youtu.be/5N33E9tC400)]**

<aside>
💡

Big idea: agent reliability = great context construction

</aside>

1. **Chroma: Context Rot  [[Blog](https://research.trychroma.com/context-rot)]**

> “Large Language Models (LLMs) are typically presumed to process context uniformly—that is, the model should handle the 10,000th token just as reliably as the 100th. However, in practice, this assumption does not hold.”
> 

<aside>
💡

Big idea: longer ≠ better when it comes to context; performance can *degrade* as you shove in more tokens

</aside>

1. **Design Patterns for Securing LLM Agents against Prompt Injections [[Ref](https://arxiv.org/abs/2506.08837)], reviewed by [Simon Willison](https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/#the-context-minimization-pattern)**

> [The Context-Minimization Pattern](https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/#the-context-minimization-pattern): To prevent certain user prompt injections, the agent system can remove unnecessary content from the context over multiple interactions.💡 Big Idea (for this context!): Prompt injection is a very hard problem to solve, but one way to mitigate the risk of prompt injections is to minimize what is put in context
> 

<aside>
💡

Big Idea: one way to help secure against Prompt Injections is to minimize the amount of stuff you put in context 

</aside>

1. **Context Engineering for AI Agents: Lessons from Building Manus [[Ref](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)],** [reviewed by Dex Horthy](https://boundaryml.com/podcast/2025-08-12-manus-context-engineering)

> *"Context Engineering is an active process. It's about managing the model's memory with smart cache strategies, structuring inputs for efficiency, and reinforcing key information to guide the LLM, ensuring it stays on-task and performs effectively."*
> 
- Reinforce context, don’t just assume you can rely on short- or long-term memory
- Use few-shot prompting sparingly
- Prompt structure directly impacts speed and cost

<aside>
💡

Big Idea: context becomes long over time when applications are used; managing context is a journey, not a destination

</aside>

What can we learn?

- Own and minimize context to optimize it
- Actively manage context over time

That is, the volume and type of data we put in context at any point in our AI application’s lifecycle drives not only the quality of output, but also the security of our systems.

TL;DR: Garbage in, Garbage Out. Too much Garbage in is actually unsafe. Super trash.

# 🧱 Multi-Agent Implementations

LangChain describes multi-agent systems as being “connected in a specific way.”  The “specific way” we connect agents outlines the implementation we use in our application flow.

While there are no hard and fast hierarchies or limits to how we can connect agents, either with tools or more generically by calling any Python function, we do have starting points that we’ll discuss.

As an introduction, let’s consider three typical implementations outlined in [LangGraph: Multi-Agent Workflows](https://blog.langchain.dev/langgraph-multi-agent-workflows/):

1. Multi-Agent Collaboration: all the work done by any agent is visible to all others
2. Agent Supervisor: supervisors are responsible for routing to individual contributors (agents)
3. Hierarchical Agent Teams: A supervisor of teams routes to supervisors responsible for routing to individual agents

But of course, this just scratches the surface of the many ways that we can think about building with complex multi-agent patterns, even just using LLMs!

We can go deeper into patterns through [**Zero to One: Learning Agentic Patterns** from Phil Schmi](https://www.philschmid.de/agentic-pattern)d (June, 2025) and [Key Agentic Design Patterns](https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/?utm_campaign=The%20Batch&utm_source=hs_email&utm_medium=email&_hsenc=p2ANqtz-8TZzur2df1qdnGx09b-Fg94DTsc3-xXao4StKvKNU2HR51el3n8yOm0CPSw6GiAoLQNKua), by [Deeplearning.ai](http://Deeplearning.ai) (March-April, 2024). In fact, we can broadly categorize many of these patterns into three types:

1. Single Agent
    - **Router**/Gating
    - **Tool** using ReAct Loop
    - **Planning** (Decompose-then-execute)
    - **Reflection**/Self-Critique
    - **Evaluator**Optimizer
    - **Self-consistency** & committees
    - **Memory** patterns
    - **Parallelization**
    - **HITL**/Interrupts & Approvals
    - **Guardrails** & “tool-required”
2. Multi-Agent
    - **Orchestrator**Workers (**Supervisor**)
    - **Handoffs** as Tools
    - **Hierarchical Teams** (Team-of-Teams)
    - **Network**/Free-Graph **Swarms**
    - **Debate**/Adversarial collaboration
    - **Role**playing
    - **Mixture** of-Agents
3. Domain-Specific
    - **Deep Research Loops**
    - **Coding Agent Loops**

Of course, it’s easy to get lost in the sauce of multi-agent systems, especially as we consider reasoning more generally, multi-modal and world models, as well as simulation environments. For this session, however, we’ll get a taste of complexity and some key insights into how to best deal with matching the complexity of our problem to the complexity of the solutions that we build!
