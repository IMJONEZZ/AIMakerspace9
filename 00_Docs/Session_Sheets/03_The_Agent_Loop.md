# Session 3: 🔁 The Agent Loop

🎯 **Goal**: Understand what an “agent” is and how to use the latest abstractions for building production-grade agents fast

📚 **Learning Outcomes**
- Understand agents and the foundational agent loop
- Learn the core constructs of LangChain
- Learn the key components of building agents in LangChain, including create_agent and middleware

🧰 **New Tools**
- Orchestration: [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- Vector Database: [QDrant](https://github.com/qdrant)
- Monitoring: [LangSmith Observability ](https://docs.langchain.com/langsmith/observability)

## 📛 Required Tooling & Account Setup
In addition to the tools we've already learned, in this session you'll need:
    
1. Create a [LangSmith](https://smith.langchain.com/) account
       
## 📜 Recommended Reading

1. [ReAct](https://arxiv.org/abs/2210.03629): Synergizing Reasoning and Acting in Language Models (Oct 2022)
2. LangChain 1.0 [Release Blog](https://blog.langchain.com/langchain-langgraph-1dot0/) (Oct 2025)
3. Great overviews from the LangChain docs!   
- [Philosophy](https://docs.langchain.com/oss/python/langchain/philosophy)
- [Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [Component Architecture](https://docs.langchain.com/oss/python/langchain/component-architecture)
- [Context Overview](https://docs.langchain.com/oss/python/concepts/context)
- [Context engineering in agents](https://docs.langchain.com/oss/python/langchain/context-engineering)
- [Middleware](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts)

# 🗺️ Overview

In Session 3, we introduce the Agent. What is an agent, exactly, and how do we use the construct to build awesome AI applications? And by the way, what does "agent" have to do with "RAG?"

The core **concepts** we'll cover include the big idea behind the definition of an agent that's [been agreed upon](https://simonwillison.net/2025/Sep/18/agents/) by the industry; that is, that "an LLM agent runs tools in a loop to achieve a goal." We'll take this idea further and discuss the "agent harness" as well. In addition, we'll cover a bit of the history of Langchain and its evolution to v1.0. 

The core **code** we'll cover includes the fundamentals of LangChain - the core constructs behind the framework, and when to choose one level of abstraction (e.g., [LangChain](https://docs.langchain.com/oss/python/langchain/overview)) versus another (e.g., [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)). We'll build a simple agent and we'll also learn how to monitor our application using [LangSmith](https://docs.langchain.com/langsmith/home). From there, we'll use LangChain's [Middleware](https://docs.langchain.com/oss/python/langchain/middleware/overview) along with our choice for best vector databse ([QDrant](https://qdrant.tech/)) to build a "RAG Agent." In other words, we'll build an agent that uses a tool, and that tool will do RAG. .

# 🕴️ What is an Agent?

The term “agent” is often quite confusing. What does it mean for something to be “agentic?”

> "[**Agents**] might be neurons ... neurons [form] brains ... *At each level, new **emergent structures** [form] and engage in new emergent behaviors.*  Complexity [is] a science of **emergence**.”  ~ M. Mitchel Waldrop, [Complexity](https://www.goodreads.com/book/show/337123.Complexity)
>

While the level of complexity of what we consider an AI agent is bound to increase with time, you must understand a few things if you’re looking to build, ship, and share agentic applications today.

- Agent == Agentic; this is not a useful distinction to quibble about.
- Agents are a pattern, not a thing.  The Reasoning-Action pattern.
- Agents leverage tools through function calling. Most tools are aimed at improving search and retrieval.
- Better retrieval = better RAG.  Therefore, agents often leverage the RAG pattern.

Here is our current, working definition, of the word “Agent” in the context of building production LLM applications.

<aside>
📖

**Agent**: A system that can leverage (or emulate) reasoning (or equivalent processes) to make dynamic decisions in an application flow

</aside>

Luckily, for us, there has been some progress on this front! As of September 18, 2025, we appear to have converged

> **An LLM agent runs tools in a loop to achieve a goal. ~** [I think “agent” may finally have a widely enough agreed upon definition to be useful jargon now](https://simonwillison.net/2025/Sep/18/agents/) by Simon Willison
> 

Though we have seen many [agent-definitions](https://simonwillison.net/tags/agent-definitions/) and we have looked at many ourselves (e.g., [What is An Agent?](https://www.youtube.com/live/PsjMHb4nl24?si=HxgUJ5AByzUnhfYR)) - and it gets quite fascinating! - these days we basically have enough of a handle on things to move forth and build 🏗️, ship 🚀, and share 🚀 some agents!

# 🤔 The Reasoning-Action (ReAct) Framework

The Reasoning Action pattern looks new, but describes logic as old as AI.

- **Reason**: If (something happens)
- **Action**: Then do (something else)

The ReAct paper was built specifically by combining two ideas:

> While large language models (LLMs) have demonstrated impressive performance across tasks in language understanding and interactive decision making, their abilities for reasoning (e.g. **chain-of-thought prompting**) and acting (e.g. **action plan generation**) have primarily been studied as separate topics.  ~ Cao, et al.
> 

The idea is simple but wide-ranging: 

> reasoning traces help the model induce, track and update action plans as well as handle exceptions, which actions allow it to interface with and gather additional information from external sources such as knowledge bases or environments.
> 

It’s worth reviewing the primary figure from the original paper in detail, as well as other use cases:

<p align="center">
  <img src="https://github.com/user-attachments/assets/09aed67e-9855-4105-bc0a-756389269f2c" width="80%" />
</p>

# 🧰 Tool Calling (i.e., Function Calling)

Note the line from the last section: “**gather additional information from external sources** such as knowledge bases or environments.”

Gathering additional information, especially information that is current, is often the job that’s left to tool calling, also known as function calling.

OpenAI was the first to release function calling in July 2023, but since then it’s gained much steam and there are even [function-calling leaderboards](https://gorilla.cs.berkeley.edu/leaderboard.html) now that rates function-calling against benchmarks.

Simply put, LLMs are *fine-tuned* for function calling.  That is, their output schema is constrained to output code capable of calling another API, or function.  This, in effect, makes connecting GPTs to external tools and APIs much easier and more reliable.

It should be noted that the beginning of function calling was simple prompting; that is, engineers telling the LLM `always output answers in JSON format`.  Over time, few-shot learning became fine-tuning, as it tends to as we move down the task-specific spectrum.  These days, we can simply set the `response_format` to `{ "type": "json_object" }` directly when using OpenAI (and other function-calling) tooling.

# 🪟 Context Engineering

It is important to understand where agents fit into Context Engineering. To do that, let’s properly visit the fundamental foundations from which the term was coined:

As Dex Horthy reminds us:

> Everything that makes agents good is context engineering ~ [12-factor Agents: Patterns of reliable LLM applications](https://www.youtube.com/watch?v=8kMaTybvDUw) by Dex Horonty
> 

It’s worth digging into the talk that coined the term in more detail here, as it’s similar in some sense to reading the OG RAG paper. Here are the 12 (err, 13) factors:

- [Factor 1: Natural Language to Tool Calls](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-01-natural-language-to-tool-calls.md)
- [Factor 2: Own your prompts](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-02-own-your-prompts.md)
- [Factor 3: Own your context window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
- [Factor 4: Tools are just structured outputs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-04-tools-are-structured-outputs.md)
- [Factor 5: Unify execution state and business state](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)
- [Factor 6: Launch/Pause/Resume with simple APIs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md)
- [Factor 7: Contact humans with tool calls](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md)
- [Factor 8: Own your control flow](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)
- [Factor 9: Compact Errors into Context Window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)
- [Factor 10: Small, Focused Agents](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md)
- [Factor 11: Trigger from anywhere, meet users where they are](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md)
- [Factor 12: Make your agent a stateless reducer](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-12-stateless-reducer.md)

**Honorable Mentions / other advice**

- [Factor 13: Pre-fetch all the context you might need](https://github.com/humanlayer/12-factor-agents/blob/main/content/appendix-13-pre-fetch.md)

# ⛓️ Core Constructs: LangChain (Classic)

When orchestrating complex LLM applications that leverage context and reasoning,  LangChain has emerged as a best-practice tool.  To begin, it’s instructive to start with how we can leverage the pattern of Retrieval Augmented Generation to build apps using LangChain.

What are the core components we need to understand?

Let us start, where we should, with the abstraction of the `chain` in LangChain.

<aside>
⛓️ Chain: a sequence of calls to other components

</aside>

With this idea of chains in mind, we can understand that `LangChain Expression Language, or LCEL`, allows us to ***compose chains*** easily.  LCEL also enables us to build production-grade prototypes that can be deployed with no code changes.

**A Simple Chain - Chat Models and Prompts**

The first chain we’ll build with LCEL combines `Model` and `Prompt` from Models I/O.

Using LLM models that have been instruction-tuned and fine-tuned for chat is a best practice for LLM-powered applications.  Just as we learned about the {System, User, Assistant} roles in OpenAI, we can leverage chat-style models using the {System, Human, AI} roles in LangChain.  These are, for all intents and purposes, the same.

<p align="center">
  <img src="https://github.com/user-attachments/assets/8e69dd36-4320-4c84-96e5-ea23bf260ddd" width="80%" />
</p>

Chat completions roles, OpenAI vs. LangChain.

Building our first LLM chain requires a chat prompt template.  We have seen this in our Pythonic RAG system. Here is what our first chain looks like in code.

> `chain = chat_prompt | openai_chat_model`
> 

**Our Second Chain - Retrieval Augmented Generation**

If we wanted to, we could do RAG with LangChain like this too, leveraging exactly the same process we used to build our Pythonic RAG application.

Here’s an example in code of such a RAG chain👇

1. Create **Database**
    1. `Document Loader` 
    2. `Text Splitter` 
    3. `Embedding Model`
    4. `Vector Store`
2. Ask **Question**
    1. `Embedding Model`
3. Find **References**
    1. `Retriever`
4. **Augment** the Prompt
    1. `Prompt`
5. **Generate** a better answer!
    1. `Model`

```python
simple_rag  = (
    {"context": retriever, "query": RunnablePassthrough()}
    | chat_prompt
    | openai_chat_model
    | StrOutputParser()
)
```

Of course, we don't have to do this anymore!

However, it's useful to dig in because notice that little word “Runnable” in the code.

# **The Runnable**

In LangChain, a Runnable is like a LEGO brick in your AI application - it's a standardized component that can be easily connected with other components. The real power of Runnables comes from their ability to be combined in flexible ways using LCEL (LangChain Expression Language).

*Every component of a chain is a **runnable**.*  

In fact, **the primary abstraction in the LangChain ecosystem is the runnable**.

> We often refer to a `Runnable` created using LCEL as a "chain" [[Ref](https://python.langchain.com/docs/concepts/lcel/)]
> 

## **Key Features of Runnables**

**1. Universal Interface**

Every Runnable in LangChain follows the same pattern:

- Takes an input
- Performs some operation
- Returns an output

This consistency means you can treat different components (like models, retrievers, or parsers) in the same way.

**2. Built-in Parallelization**

Runnables come with methods for handling multiple inputs efficiently:

```python
# Process inputs in parallel, maintain order
results = chain.batch([input1, input2, input3])

# Process inputs as they complete
for result in chain.batch_as_completed([input1, input2, input3]):
    print(result)
```

**3. Streaming Support**

Perfect for responsive applications:

```python
# Stream outputs as they're generated
for chunk in chain.stream({"query": "Tell me a story"}):
    print(chunk, end="", flush=True)
```

**4. Easy Composition**

The `|` operator makes building pipelines intuitive, as seen above! e.g.;

```python
# Create a basic RAG chain
rag_chain = retriever | prompt | model | output_parser
```

**Common Types of Runnables**

- Language Models: Like our `ChatOpenAI` instance
- Prompt Templates: Format inputs consistently
- Retrievers: Get relevant context from a vector store
- Output Parsers: Structure model outputs
- LangGraph Nodes: Individual components in our graph

Think of Runnables as the building blocks of your LLM application. Just like how you can combine LEGO bricks in countless ways, you can mix and match Runnables to create increasingly sophisticated applications!

# 🔁 Core Construct: LangChain v1.0 - The Agent Loop

With the new release of v1.0, LangChain has [made it easier than ever for us to build agents](https://youtu.be/r5Z_gYZb4Ns?si=9qOJ_Og2_NJ9hs3W) with the Agent Loop. 

It consists of two main steps:

1. **Model call** - calls the LLM with a prompt and available tools, returns either a response or a request to execute tools
2. **Tool execution** - executes the tools that the LLM requested, returns tool results
3. Repeat

The `create_agent` construct is what we use to build agent loops. That's what we'll do in today's session!

At least, it's what we use when you use LangChain. As we'll see, when we get more complex we need to go to a heavier duty tool like LangGraph.

# ⚒️ LangSmith

> **LangSmith** provides tools for developing, debuggind, and deploying LLM applications. [[Ref](https://docs.langchain.com/langsmith/home)]
> 

In addition to building out a RAG application with LangChain, we will also learn what the developer sees behind the scenes when users interact with our LangChain application!  Enter … LangSmith.

> “LangSmith turns LLM “magic” into enterprise-ready applications.”
> 

Ultimately, we will use LangSmith for evaluation and for visibility.

**Evaluation**

The key to understanding the right way to do quantitative evaluation with tools like LangSmith is Metrics Driven Development (MDD). There are three steps to keep in mind:

1. Establish a baseline
2. **Change stuff** that potentially improves baseline
3. **Recalculate** metrics

It’s not about absolute values.  Rather, MDD is about *relative changes* in evaluation metrics.

In LangSmith, we can define our own or use pre-built evaluators.

- Ex. Correctness evaluation, the source code from [`correctness.py`](https://github.com/langchain-ai/openevals/blob/main/python/openevals/prompts/correctness.py?utm_source=chatgpt.com) 👇
    
    ```python
    CORRECTNESS_PROMPT = """You are an expert data labeler evaluating model outputs for correctness. Your task is to assign a score based on the following rubric:
    
    <Rubric>
      A correct answer:
      - Provides accurate and complete information
      - Contains no factual errors
      - Addresses all parts of the question
      - Is logically consistent
      - Uses precise and accurate terminology
    
      When scoring, you should penalize:
      - Factual errors or inaccuracies
      - Incomplete or partial answers
      - Misleading or ambiguous statements
      - Incorrect terminology
      - Logical inconsistencies
      - Missing key information
    </Rubric>
    
    <Instructions>
      - Carefully read the input and output
      - Check for factual accuracy and completeness
      - Focus on correctness of information rather than style or verbosity
    </Instructions>
    
    <Reminder>
      The goal is to evaluate factual correctness and completeness of the response.
    </Reminder>
    
    <input>
    {inputs}
    </input>
    
    <output>
    {outputs}
    </output>
    
    Use the reference outputs below to help you evaluate the correctness of the response:
    
    <reference_outputs>
    {reference_outputs}
    </reference_outputs>
    """
    ```
    

Can you spot the prompting best practices at play in the prompt (e.g., instruction, context, input, output)?

## Monitoring

When it comes to observing and assessing the performance of our application, in addition to evals we should also be watching key production metrics including `token count` and `latency`. 

More generally, monitoring gives us visibility into the inside of our application. It allows us to drill down into problems as soon as they become obvious.

[Tracing](https://docs.langchain.com/langsmith/observability-quickstart) allows us to keep track of everything throughout each piece of our LLM application pipeline.  A run represents a single unit of work or operation within your LLM application, and a trace is a collection of runs!

Ultimately, we will use LangSmith for monitoring _and evaluation_. But that's for another day! We will explore LangSmith further in future sessions!

--

Do you have any questions about how to best prepare for Session 1 after reading? Please don't hesitate to provide direct feedback to `greg@aimakerspace.io` or `Dr Greg` on Discord!

