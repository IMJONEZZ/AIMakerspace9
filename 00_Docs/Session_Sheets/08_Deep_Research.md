# Session 8: 🕵️ Deep Research

🎯 Understand how to deep research systems work under the hood and how to build them.

📚 **Learning Outcomes**
- Learn the lessons that the LangGraph team has learned building open deep research
- Understand the three step process for conducting research: scope, research, write

🧰 **New Tools**
- [Open Deep Research](https://github.com/langchain-ai/ope)
- [Deep Research from Scratch](https://github.com/langchain-ai/deep_research_from_scratch) 

## 📛 Required Tooling & Account Setup
No additional tools or accounts required.
   
## 📜 Recommended Reading
- [Read How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), (June 2025)
- [Learning the Bitter Lesson](https://rlancemartin.github.io/2025/07/30/bitter_lesson/) (July 2025)
- [Deep Research Bench](https://deepresearch-bench.github.io/)

# 🗺️ Overview


The killer app of 2025—the multi-agent system that helps us search and research—has seen broad adoption throughout the industry and will serve as our primary cohort use case, which we will build from scratch using OSS tools.

Doing **Deep Research**—that is, autonomously exploring, gathering, and synthesizing information from various sources (e.g., search tools, reference documents, or code execution)—is the kind of capability that, if you can build it intelligently for your domain and organization, will make you indispensable to leadership undergoing an AI transformation.

Let’s consider how many organizations have released their own “Deep Research” agents. The common goal is to produce a system capable of:

- Constructing a research plan  
- Searching or browsing the web  
- Summarizing, analyzing, and refining large volumes of information  
- Presenting findings in a clear and comprehensive format  

## Recent Deep Research Releases

### December 11, 2024  
[Google’s Deep Research](https://blog.google/products/gemini/google-gemini-deep-research/)

> “Deep Research uses AI to **explore complex topics on your behalf** and provide you with findings in a comprehensive, easy-to-read report.”

---

### February 2, 2025  
[OpenAI’s Deep Research](https://openai.com/index/introducing-deep-research/)

> “Deep research is OpenAI’s next agent that can **do work for you independently**—you give it a prompt, and ChatGPT will **find, analyze, and synthesize hundreds of online sources** to **create a comprehensive report at the level of the research analyst**.”

**July 17, 2025 update:**  
Deep Research can now go **even deeper and broader** with access to a visual browser as part of the ChatGPT agent. To access these updated capabilities, select **“agent mode”** from the dropdown in the composer and enter your query directly. The original Deep Research functionality remains available via the **“deep research”** option in the tools menu.

---

### February 4, 2025 (just 2 days later!)  
[Hugging Face Open Deep Research](https://huggingface.co/blog/open-deep-research)

> While powerful LLMs are now freely available in open source (see, e.g., [the recent DeepSeek R1 model](https://huggingface.co/deepseek-ai/DeepSeek-R1)), OpenAI didn’t disclose much about the agentic framework underlying Deep Research.
>
> So we decided to embark on a 24-hour mission to reproduce their results and open-source the needed framework along the way!
>
> The clock is ticking—let’s go! ⏱️

---

### February 14, 2025  
[Perplexity Deep Research](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research)

> Deep Research takes question answering to the next level by spending 2–4 minutes doing the work it would take a human expert many hours to perform.

**How it works:**

- **Research with reasoning** – Equipped with search and coding capabilities, Perplexity’s Deep Research mode iteratively searches, reads documents, and reasons about what to do next, refining its research plan as it learns more—much like a human researcher.
- **Report writing** – Once source materials are fully evaluated, the agent synthesizes the research into a clear and comprehensive report.
- **Export & Share** – Export the final report to a PDF or document, or convert it into a Perplexity Page to share with colleagues or friends.

---

### February 19, 2025  
[Grok 3 Beta – The Age of Reasoning Agents](https://x.ai/news/grok-3)

> **Grok Agents: Combining Reasoning and Tool Use**
>
> To understand the universe, we must interface Grok with the world. Equipped with code interpreters and internet access, Grok 3 models learn to query for missing context, dynamically adjust their approach, and improve their reasoning based on feedback.
>
> As a first step toward this vision, we are rolling out **`DeepSearch`**—our first agent. It’s a lightning-fast AI agent built to relentlessly seek the truth across the entire corpus of human knowledge. Designed to synthesize key information, reason about conflicting facts and opinions, and distill clarity from complexity, `DeepSearch` goes far beyond a traditional browser search. Its final summary results in a concise and comprehensive report.

---

### April 15, 2025  
[Claude Research](https://www.anthropic.com/news/research)

> **Research**
>
> Research transforms how Claude finds and reasons with information. Claude operates agentically, conducting multiple searches that build on each other while determining exactly what to investigate next. It explores different angles automatically and works through open questions systematically.
>
> The result is thorough, high-quality answers with easy-to-check citations—delivered in minutes—making it practical for everyday research tasks.

---

### July 17, 2025  
[Mistral AI Deep Research](https://mistral.ai/news/le-chat-dives-deep?utm_source=alphasignal&utm_campaign=2025-07-21&asuniq=bd20930c)

> **Dive deeper with Deep Research**
>
> Research mode turns Le Chat into a coordinated research assistant that can plan, clarify your needs, search, and synthesize. Ask a meaty question, and it will break it down, gather credible sources, and build a structured, reference-backed report that’s easy to follow.
>
> Powered by a tool-augmented Deep Research agent (in preview), it’s designed to feel simple, transparent, and genuinely helpful—like collaborating with a well-organized research partner.

---

> 🧪 **Aside**  
> Using AI to accelerate research is not a new idea. Scientists have been exploring this space for a long time, with frequent breakthroughs related to doing “deeper research.”  
>  
> For example, see [AlphaEvolve](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) and its recent [math breakthrough](https://www.youtube.com/watch?si=Xp8pHr-RjWb6YOUY&v=vC9nAosXrJw&feature=youtu.be).

---

We look forward to building our own Deep Research application!
