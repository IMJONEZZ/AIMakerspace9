# Session 9: 🧪 Synthetic Data Generation for Evals

🎯 Understand how to generate test data automatically to test agentic RAG applications when you don’t have any eval datasets.

📚 **Learning Outcomes**
- Learn to generate high-quality synthetic test data for AI applications using LLMs
- Understand the knowledge graph approach used to generate data
- Understand the process of metrics-driven development
- Learn to load datasets into LangSmith when generated elsewhere

🧰 **New Tools**
- Testset Generation: [RAGAS](https://docs.ragas.io/en/stable/getstarted/rag_testset_generation/) 
- Evaluation: [RAG ASessment](https://docs.ragas.io/en/stable)[, LangSmith Evaluations](https://docs.langchain.com/langsmith/evaluation)

## 📛 Required Tooling & Account Setup
No new tools or accounts required for this session
   
## 📜 Recommended Reading
- [Mastering LLM Techniques: Evaluation](https://developer.nvidia.com/blog/mastering-llm-techniques-evaluation/) (Jan 2025)

# 🗺️ Overview

# ⚗️ Synthetic Data Generation

In the case of AI Engineers leveraging SDG, we always want to ask ourselves a directional question:

<aside>
🤔

How can I use SDG to make my application better?

</aside>

Typically, when we refer to “better” when building AI applications, we’re often focused on either cost or performance.  With this in mind, we can think of a number of aims for SDG; namely:

- 🤓 Domain-Specific Data
    - Domain-Adapted Pretraining or Continued Pretraining
    - Domain-Adapted Language Models (e.g., fine-tuning an LLM chat model)
    - Domain-Adapted Retrieval (e.g., fine-tuning an embedding model)
    
    <aside>
    ❗
    
    We can use SDG to generate task-specific or language-specific data just as you can with domains!  We will discuss this more when we cover fine-tuning.
    
    </aside>
    
- ↔️ Alignment Data
    - Reinforcement Learning with Human Feedback (RLHF)
    - Reinforcement Learning with AI Feedback (RLAIF)
    - Direct Preference Optimization (DPO)
    - **Note that one can *align* models towards many targets!
- 📊 Evaluation Data
    - e.g., is my application “good” at what I want it to be good at?
    - For prompted LLM applications
    - For RAG applications
    - For agentic applications
    - … and more!

We will dig in to focus our attention on evaluation in session 7!  Welcome to the beginning of our investigation into how to best evaluate and assess RAG and agent applications beyond using the simple prompting techniques we’ve already covered!

# 🔍 Monitoring RAG Apps in Prod

When it comes to deploying RAG applications to production, there are some key aspects of our applications that we want to be tracking, including [[Ref](https://docs.ragas.io/en/latest/getstarted/monitoring.html)]:

1. **Hallucinations**:  Are answers based on factual reference material?  In the RAG ASsessment (RAGAS) framework, this is called `Faithfulness`
2. **Quality of Retrieval**: We can identify and define “poor context” or “bad” retrievals.
3. **Quality of Response**: We can identify and define “evasive, harmful, or toxic (a.k.a. bad)” responses.
4. **Quality of Format**: We can detect and quantify responses with incorrect formatting.

In short, we’re looking for fact-based, high-quality retrievals and responses with the correct formatting!  The first step towards getting there is SDG.  The second step, as we’ll cover in Session 8, is understanding how to compute the most relevant metrics!

# 〽️ Knowledge Graph Approach

The latest for test set generation **leverages a knowledge graph** in favor of the previous evolutionary approach (now deprecated, described below) based on the [WizardLM paper](https://arxiv.org/abs/2304.12244) that outlines the Evol-Instruct process!

So what is this about knowledge graphs for test set generation?

Instead of using different in-depth or in-breadth evolutionary techniques, we use knowledge graph transformations, also called [transforms](https://docs.ragas.io/en/latest/references/transforms/), to create rich starting data.  Then we build [scenarios](https://docs.ragas.io/en/latest/references/testset_schema/#ragas.testset.synthesizers.base.BaseScenario), also called schemas, based on the data.

Why do we need this more robust knowledge graph approach?

It’s simple: the previous method worked very well for *single-hop queries* that only need to retrieve data from one source.  In other words, evolutionary approach was sufficient for generating test data for RAG applications.

This new method is designed to work well with both *single-hop* and *multi-hop* queries.  Multi-hop queries involves multiple lookups across different sources or tables.

Think about it like this: a classic single-hop query might use a SQL database, whereas a classic multi-hop query might use a graph database.

In LLM terms, synthetic test data based on a single-hop query is good for assessing simple RAG applications, whereas multi-hop queries what you need to assess agentic applications with access to multiple tools.

Additionally, it’s worth noting that this new abstraction also signals a deeper structuring of the synthetic test data.  Now we can use transforms and schemas, rather than simple prompts to evolve data.

# 🧬 An Evolutionary Approach [Optional]

The approach we’ll use to create synthetic test data sets for evaluating our RAG applications leverages evolutionary algorithms.  For our Question-Answer pairs, we evolve data that increases the complexity and diversity of the initial data set.  After all, it is the case that:

1. The same question can be asked in different ways
2. The same answer can correspond to different questions

These two simple facts guide our path to evolution.  In the end, all we need are some relevant prompts!

Fundamentally, there are two dimensions that we will consider: `breadth` and `depth`.  That is, we can **evolve** our data in the direction of increasing depth or increasing breadth.

- 💬 In-Depth Evolver Prompt
    
    ```
    I want you act as a Prompt Rewriter.
    Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems
    (e.g., ChatGPT and GPT4) a bit harder to handle.
    But the rewritten prompt must be reasonable and must be understood and responded by humans.
    Your rewriting cannot omit the non-text parts such as the table and code in #Given Prompt#:. Also, please
    do not omit the input in #Given Prompt#.
    You SHOULD complicate the given prompt using the following method:
    Please add one more constraints/requirements into #Given Prompt#
    You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only
    add 10 to 20 words into #Given Prompt#.
    ‘#Given Prompt#’, ‘#Rewritten Prompt#’, ‘given prompt’ and ‘rewritten prompt’ are not allowed to appear in
    #Rewritten Prompt#
    #Given Prompt#:
    <Here is instruction.>
    #Rewritten Prompt#:
    ```
    
- 💬 In-Breadth Evolver Prompt
    
    ```
    I want you act as a Prompt Creator.
    Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.
    This new prompt should belong to the same domain as the #Given Prompt# but be even more rare.
    The LENGTH and difficulty level of the #Created Prompt# should be similar to that of the #Given Prompt#.
    The #Created Prompt# must be reasonable and must be understood and responded by humans.
    ‘#Given Prompt#’, ‘#Created Prompt#’, ‘given prompt’ and ‘created prompt’ are not allowed to appear in
    #Created Prompt#.
    #Given Prompt#:
    <Here is instruction.>
    #Created Prompt#:
    ```
    
    ```python
    I want you act as a Prompt Creator.
    Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.
    This new prompt should belong to the same domain as the #Given Prompt# but be even more rare.
    The LENGTH and difficulty level of the #Created Prompt# should be similar to that of the #Given Prompt#.
    The #Created Prompt# must be reasonable and must be understood and responded by humans.
    ‘#Given Prompt#’, ‘#Created Prompt#’, ‘given prompt’ and ‘created prompt’ are not allowed to appear in
    #Created Prompt#.
    #Given Prompt#:
    <Here is instruction.>
    #Created Prompt#:
    ```
    

The RAG ASsessment Framework (RAGAS), builds on these prompts and can evolve data along the following `In-Depth` dimension [[Ref](https://docs.ragas.io/en/latest/concepts/testset_generation.html)]:

- **Reasoning**: Rewrite the question in a way that enhances the need for reasoning to answer it effectively.
- **Conditioning**: Modify the question to introduce a conditional element to add complexity to the question.
- **Multi-Context**: Rephrase the question in a manner that necessitates information from multiple related sections or chunks to formulate an answer.
- **Conversational**: A portion of the questions, following the evolution process, can be transformed into conversational samples. These questions simulate a chat-based question-and-follow-up interaction, mimicking a chat-Q&A pipeline.

# 🕳️ Go Deeper

- Get ahead of Session 8 and connect SDG to eval clearly with this blog from The Wiz, et al.!
    
    [Mastering LLM Techniques: Evaluation | NVIDIA Technical Blog](https://developer.nvidia.com/blog/mastering-llm-techniques-evaluation/)

