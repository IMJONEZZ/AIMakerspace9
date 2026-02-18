# Session 11: 🐕 Advanced Retrievers

🎯 Learn best practices for retrieval and a systematic approach for deciding on the best retriever for your AI applications.

📚 **Learning Outcomes**
- Understand how retrieval, chunking, and ranking can enhance context given to agentic RAG applications
- Understand today’s best practices for retrieval
- Learn to systematically compare the performance of retrieval algorithms

🧰 **New Tools**
Retrievers: [LangChain Retrievers](https://docs.langchain.com/oss/python/integrations/retrievers)

## 📛 Required Tooling & Account Setup
No new tools or accounts required

## 📜 Recommended Reading

- [BM25](https://www.nowpublishers.com/article/Details/INR-019) (2009)
- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) (2009)
- [Semantic Chunking](https://x.com/GregKamradt/status/1737921395974430953?s=20) (2023)

# 🗺️ Overview

# 📂 **The Role of Advanced Retrieval Methods**

Retrieval in RAG is essential for feeding the right data into a large language model (LLM) to improve the quality of generated responses. It is crucial to avoid hallucinations and redundancy while ensuring the returned reference material is relevant and fact-checkable.

Retrieval involves embedding a query into vector space and searching for similar documents based on that representation. This involves both dense vector retrieval and in-context learning, which augments the context provided to the LLM before generating a response.

The more relevant the retrieved context, the more accurate the generation, which is the fundamental principle of RAG.

Chunks are created when natural language (text) from our source documents gets split. Common methods for text splitting include:

- By no. of characters, with overlapping sliding window.
- By sentence or paragraph.
- A hybrid of the two (e.g., recursive character text splitter)

The [recursive character text splitter](https://python.langchain.com/docs/how_to/recursive_text_splitter/) has become the de facto standard for building RAG systems. 

Despite the utility of these text splitters, if you have ever built a RAG system, you know that deciding on chunk sizes for your data - even using the most advanced text splitter - is a bit of a black art, as we’ve seen previously.

[ChunkViz](https://chunkviz.up.railway.app/)

# 🧰 **Methods for Your Toolkit**

There are some key retrieval methods that are important to understand.  We start with the most basic (and naive) approach, and move to the most computationally intensive and latest approach - [*semantic chunking*](https://x.com/thesephist/status/1724159343237456248?s=20) - during this session!

- **Naive Retrieval**: The simplest form of retrieval, where the system retrieves chunks of data similar to the query based on cosine similarity. While easy to set up, it can sometimes return less relevant information or redundant content. We simply use similarity, and return the Top K chunks.
- **Parent Document Retrieval**: Instead of returning small chunks directly, this method returns the larger parent document (or section) from which the chunk originated. This approach helps provide broader context without overwhelming the LLM with smaller pieces of potentially disjointed information.
- **Contextual Compression (Reranking)**: This method reduces the number of returned chunks by focusing on those that are most relevant to the query. By compressing the context or reranking the results, the LLM can work with a more refined dataset, improving efficiency and cost-effectiveness.  We will use Cohere’s [Rerank](https://cohere.com/rerank), and industry standard, to accomplish contextual compression.
- **Multi-Query Retriever:** This style of retriever works by taking the original user query and creating `n` number of new user queries using an LLM. Then, we retrieve documents for each query. Finally, we use all unique retrieved documents as context.
- **Ensemble Retrieval**: This is exactly what it sounds like!  We use an ensemble of retrievers and combine their retrieved documents. based on a rank-fusion algorithm.  We will use the [Reciprocal Rank Fusion](https://www.google.com/url?q=https%3A%2F%2Fplg.uwaterloo.ca%2F%7Egvcormac%2Fcormacksigir09-rrf.pdf) algorithm.
- Semantic Chunking: The recursive character text splitter has become the de facto standard for building RAG systems.  Semantic chunking takes it to the next level by allowing us to combine entire groups of adjacent sentences.

These methods offer flexibility depending on the nature of the dataset and the type of task (e.g., answering questions, and summarizing long documents). The goal is to optimize retrieval to ensure that only high-quality and relevant data is used in generating responses, thus improving the overall performance of the system.

# 🕳️ Go Deeper

- To go even deeper on the topics we covered today, check out our events on [Advanced Retrieval Methods](https://www.youtube.com/live/xmfPh1Fv2kk?si=Z622xCPGCWO62Ga3) and [Semantic Chunking](https://www.youtube.com/live/dt1Iobn_Hw0?si=qDfn0uWj2eIyD30F)!
