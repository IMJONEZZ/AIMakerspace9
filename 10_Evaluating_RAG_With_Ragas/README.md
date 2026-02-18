<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 10: Evaluating RAG with Ragas</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/AIE9/tree/main/00_AIE_Quicklinks)

| Session Sheet | Recording     | Slides        | Repo         | Homework      | Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Agentic RAG Evaluation](https://github.com/AI-Maker-Space/AIE9/blob/main/00_Docs/Session_Sheets/10_Agentic_RAG_Evaluation.md) |[Recording!](https://us02web.zoom.us/rec/share/m75V8ObrHg1O-RKKaMlSHoizy8eWMwLBf0nE0W8V7ui41RD2Q-IBFO3-QD304fZ3.qktR96_n9PRz5BCU) <br> passcode: `3jsJKD=o`| [Session 10 Slides](https://www.canva.com/design/DAG-ECzru48/iaesY_gFRif-Fu3s3vlDVQ/edit?utm_content=DAG-ECzru48&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [Session 10 Assignment: RAGAS](https://forms.gle/oMC198vEgmV4khej8) | [Feedback 2/12](https://forms.gle/pHwLY2mcALEbWCcr8) |

### Outline:

**Notebook 1: Evaluating_RAG_Assignment.ipynb**
- Task 1: Installing Required Libraries
- Task 2: Set Environment Variables
- Task 3: Synthetic Dataset Generation for Evaluation using Ragas
- Task 4: Construct our RAG application
- Task 5: Evaluating our Application with Ragas
- Task 6: Making Adjustments and Re-Evaluating
     - **Activity #1**: Implement a Different Reranking Strategy

**Notebook 2: Evaluating_Agents_Assignment.ipynb**
- Task 1: Installing Required Libraries
- Task 2: Set Environment Variables
- Task 3: Building a ReAct Agent with Metal Price Tool
- Task 4: Implementing the Agent Graph Structure
- Task 5: Converting Agent Messages to Ragas Evaluation Format
- Task 6: Evaluating the Agent's Performance using Ragas Metrics
     - Tool Call Accuracy
     - Agent Goal Accuracy
     - Topic Adherence
     - **Activity #1**: Evaluate Tool Call Accuracy
     - **Activity #2**: Evaluate Topic Adherence

### Prerequisites:

#### 1. API Keys Required

You'll need the following API keys for this session:

- **OpenAI API Key**: For LLM and embedding models - [Get one here](https://platform.openai.com/api-keys)
- **Cohere API Key**: For reranking models - [Get one here](https://dashboard.cohere.com/api-keys)
- **LangSmith API Key** (optional): For tracing - [Get one here](https://smith.langchain.com/)
- **Metal API Key**: For the agent notebook - [Get one here](https://metals.dev/)

#### 2. Copy Environment Template

```bash
cp .env.sample .env

```
Then edit .env and replace the placeholder values with your actual API keys.

NOTE: Do not copy this file if you want to be able to enter the API keys via a prompt in the notebook.

### Steps to Run:

1. Install UV, which you can do through [this resource](https://docs.astral.sh/uv/#getting-started)
2. Run the command `uv sync`
3. Open your Jupyter notebook and select `.venv` for your kernel.

# Build

Run both notebooks:
1. `Evaluating_RAG_Assignment.ipynb` - Learn synthetic data generation and RAG evaluation with Ragas
2. `Evaluating_Agents_Assignment.ipynb` - Learn agent evaluation with Ragas

# Ship

- Complete all questions and activities in both notebooks
- Make a diagram showing how Ragas metrics relate to RAG pipeline components
- Record a Loom video walking through the notebooks, the questions, and your improvements!

# Share

- Make a social media post about your RAG evaluation learnings and tag @AIMakerspace
- Share 3 lessons learned
- Share 3 lessons not learned

Here's a template to get your post started!

```
Just learned how to systematically evaluate RAG systems with Ragas!

Key insights:
1. Synthetic test data generation creates realistic evaluation scenarios
2. Metrics like Faithfulness and Context Recall reveal specific weaknesses
3. Reranking can dramatically improve retrieval quality

Building better AI systems through better evaluation!

A huge shoutout to @AI Makerspace for making this possible.

#AI #RAG #Evaluation #LangChain #LangGraph #BuildInPublic
```

<details>
<summary><h3>Advanced Build (Optional): Semantic Chunking Strategy</h3></summary>

> **Note**: Completing an Advanced Build earns full credit **in place of** doing the base assignment notebook questions/activities.

##### MINIMUM REQUIREMENTS:

1. Baseline `LangGraph RAG` Application using `NAIVE RETRIEVAL`
2. Baseline Evaluation using `RAGAS METRICS`
   - [Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/faithfulness.html)
   - [Answer Relevancy](https://docs.ragas.io/en/stable/concepts/metrics/answer_relevance.html)
   - [Context Precision](https://docs.ragas.io/en/stable/concepts/metrics/context_precision.html)
   - [Context Recall](https://docs.ragas.io/en/stable/concepts/metrics/context_recall.html)
   - [Answer Correctness](https://docs.ragas.io/en/stable/concepts/metrics/answer_correctness.html)
3. Implement a `SEMANTIC CHUNKING STRATEGY`
4. Create a `LangGraph RAG` Application using `SEMANTIC CHUNKING` with `NAIVE RETRIEVAL`
5. Compare and contrast results

##### SEMANTIC CHUNKING REQUIREMENTS:

Chunk semantically similar (based on designed threshold) sentences, and then paragraphs, greedily, up to a maximum chunk size. Minimum chunk size is a single sentence.

Have fun!

#### Submitting the Advanced Build:

1. Complete all steps of the Main Assignment above
2. Create a notebook that meets or exceeds the MINIMUM REQUIREMENTS as well as the SEMANTIC CHUNKING REQUIREMENTS
3. Add, commit and push your completed notebook to your repository

When submitting, provide:
- Your Loom video link demonstrating the semantic chunking implementation
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
2. **IMPORTANT:** Start Cursor from the `09_Evaluating_RAG_With_Ragas` folder (you can also use the _File -> Open Folder_ menu option of an existing Cursor window)
3. Answer Questions 1 - 4 using the `##### Answer:` markdown cell below them in `Evaluating_RAG_Assignment.ipynb`
4. Complete Activity #1 in `Evaluating_RAG_Assignment.ipynb`
5. Answer Questions 1 - 4 using the `##### Answer:` markdown cell below them in `Evaluating_Agents_Assignment.ipynb`
6. Complete Activities #1 and #2 in `Evaluating_Agents_Assignment.ipynb`
7. Add, commit and push your modified notebooks to your GitHub repository.

When submitting your homework, provide:
- Your Loom video link
- The GitHub URL to the `09_Evaluating_RAG_With_Ragas` folder on your assignment branch
