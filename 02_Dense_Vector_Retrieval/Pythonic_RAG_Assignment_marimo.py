import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Your First RAG Application: Personal Wellness Assistant

    In this notebook, we'll walk you through each of the components that are involved in a simple RAG application by building a **Personal Wellness Assistant**.

    Imagine having an AI assistant that can answer your health and wellness questions based on a curated knowledge base - that's exactly what we'll build here. We won't be leveraging any fancy tools, just the OpenAI Python SDK, Numpy, and some classic Python.

    > NOTE: This was done with Python 3.12.3.

    > NOTE: There might be [compatibility issues](https://github.com/wandb/wandb/issues/7683) if you're on NVIDIA driver >552.44 As an interim solution - you can rollback your drivers to the 552.44.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents:

    - Task 1: Imports and Utilities
    - Task 2: Documents (Loading our Wellness Knowledge Base)
    - Task 3: Embeddings and Vectors
    - Task 4: Prompts
    - Task 5: Retrieval Augmented Generation (Building the Wellness Assistant)
      - 🚧 Activity #1: Enhance Your Wellness Assistant
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's look at a rather complicated looking visual representation of a basic RAG application.

    <img src="https://i.imgur.com/vD8b016.png" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Imports and Utilities

    We're just doing some imports and enabling `async` to work within the Jupyter environment here, nothing too crazy!
    """)
    return


@app.cell
def _():
    from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter
    from aimakerspace.vectordatabase import VectorDatabase
    from aimakerspace.openai_utils.embedding import EmbeddingModel
    import asyncio
    return (
        CharacterTextSplitter,
        EmbeddingModel,
        TextFileLoader,
        VectorDatabase,
        asyncio,
    )


@app.cell
def _():
    import nest_asyncio

    nest_asyncio.apply()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: Documents

    We'll be concerning ourselves with this part of the flow in the following section:

    <img src="https://i.imgur.com/jTm9gjk.png" />
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Loading Source Documents

    So, first things first, we need some documents to work with.

    While we could work directly with the `.txt` files (or whatever file-types you wanted to extend this to) we can instead do some batch processing of those documents at the beginning in order to store them in a more machine compatible format.

    In this case, we're going to parse our text file into a single document in memory.

    Let's look at the relevant bits of the `TextFileLoader` class:

    ```python
    def load_file(self):
            with open(self.path, "r", encoding=self.encoding) as f:
                self.documents.append(f.read())
    ```

    We're simply loading the document using the built in `open` method, and storing that output in our `self.documents` list.

    > NOTE: We're using a comprehensive Health & Wellness Guide as our sample data. This content covers exercise, nutrition, sleep, stress management, and healthy habits - perfect for building a personal wellness assistant!
    """)
    return


@app.cell
def _(TextFileLoader):
    text_loader = TextFileLoader("data/HealthWellnessGuide.txt")
    documents = text_loader.load_documents()
    len(documents)
    return (documents,)


@app.cell
def _(documents):
    print(documents[0][:100])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Splitting Text Into Chunks

    As we can see, there is one massive document.

    We'll want to chunk the document into smaller parts so it's easier to pass the most relevant snippets to the LLM.

    There is no fixed way to split/chunk documents - and you'll need to rely on some intuition as well as knowing your data *very* well in order to build the most robust system.

    For this toy example, we'll just split blindly on length.

    >There's an opportunity to clear up some terminology here, for this course we will stick to the following:
    >
    >- "source documents" : The `.txt`, `.pdf`, `.html`, ..., files that make up the files and information we start with in its raw format
    >- "document(s)" : single (or more) text object(s)
    >- "corpus" : the combination of all of our documents
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As you can imagine (though it's not specifically true in this toy example) the idea of splitting documents is to break them into manageable sized chunks that retain the most relevant local context.
    """)
    return


@app.cell
def _(CharacterTextSplitter, documents):
    text_splitter = CharacterTextSplitter()
    split_documents = text_splitter.split_texts(documents)
    len(split_documents)
    return split_documents, text_splitter


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's take a look at some of the documents we've managed to split.
    """)
    return


@app.cell
def _(split_documents):
    split_documents[0:1]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Embeddings and Vectors

    Next, we have to convert our corpus into a "machine readable" format as we explored in the Embedding Primer notebook.

    Today, we're going to talk about the actual process of creating, and then storing, these embeddings, and how we can leverage that to intelligently add context to our queries.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### OpenAI API Key

    In order to access OpenAI's APIs, we'll need to provide our OpenAI API Key!

    You can work through the folder "OpenAI API Key Setup" for more information on this process if you don't already have an API Key!
    """)
    return


@app.cell
def _():
    import os
    import openai
    from getpass import getpass

    openai.api_key = getpass("OpenAI API Key: ")
    os.environ["OPENAI_API_KEY"] = openai.api_key
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Vector Database

    Let's set up our vector database to hold all our documents and their embeddings!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    While this is all baked into 1 call - we can look at some of the code that powers this process to get a better understanding:

    Let's look at our `VectorDatabase().__init__()`:

    ```python
    def __init__(self, embedding_model: EmbeddingModel = None):
            self.vectors = defaultdict(np.array)
            self.embedding_model = embedding_model or EmbeddingModel()
    ```

    As you can see - our vectors are merely stored as a dictionary of `np.array` objects.

    Secondly, our `VectorDatabase()` has a default `EmbeddingModel()` which is a wrapper for OpenAI's `text-embedding-3-small` model.

    > **Quick Info About `text-embedding-3-small`**:
    > - It has a context window of **8191** tokens
    > - It returns vectors with dimension **1536**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### ❓Question #1:

    The default embedding dimension of `text-embedding-3-small` is 1536, as noted above.

    1. Is there any way to modify this dimension?
    2. What technique does OpenAI use to achieve this?

    > NOTE: Check out this [API documentation](https://platform.openai.com/docs/api-reference/embeddings/create) for the answer to question #1.1, and [this paper](https://arxiv.org/abs/2205.13147) for an answer to question #1.2!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### ✅ Answer:
    1. Yes,

    ```
    dimensions
    integer
    Optional
    The number of dimensions the resulting output embeddings should have. Only supported in text-embedding-3 and later models.
    ```

    2. Matryoshka
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can call the `async_get_embeddings` method of our `EmbeddingModel()` on a list of `str` and receive a list of `float` back!

    ```python
    async def async_get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
            return await aget_embeddings(
                list_of_text=list_of_text, engine=self.embeddings_model_name
            )
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We cast those to `np.array` when we build our `VectorDatabase()`:

    ```python
    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
            embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
            for text, embedding in zip(list_of_text, embeddings):
                self.insert(text, np.array(embedding))
            return self
    ```

    And that's all we need to do!
    """)
    return


@app.cell
def _(EmbeddingModel, VectorDatabase, asyncio, split_documents):
    embedding_model = EmbeddingModel()
    vector_db = VectorDatabase(embedding_model=embedding_model)
    vector_db = asyncio.run(vector_db.abuild_from_list(split_documents))
    return (vector_db,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### ❓Question #2:

    What are the benefits of using an `async` approach to collecting our embeddings?

    > NOTE: Determining the core difference between `async` and `sync` will be useful! If you get stuck - ask ChatGPT!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### ✅ Answer: It allows us to wait for embeddings to be returned (and to possibly execute other non-dependent code while we're waiting) instead of erroring out immediately.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    So, to review what we've done so far in natural language:

    1. We load source documents
    2. We split those source documents into smaller chunks (documents)
    3. We send each of those documents to the `text-embedding-3-small` OpenAI API endpoint
    4. We store each of the text representations with the vector representations as keys/values in a dictionary
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Semantic Similarity

    The next step is to be able to query our `VectorDatabase()` with a `str` and have it return to us vectors and text that is most relevant from our corpus.

    We're going to use the following process to achieve this in our toy example:

    1. We need to embed our query with the same `EmbeddingModel()` as we used to construct our `VectorDatabase()`
    2. We loop through every vector in our `VectorDatabase()` and use a distance measure to compare how related they are
    3. We return a list of the top `k` closest vectors, with their text representations

    There's some very heavy optimization that can be done at each of these steps - but let's just focus on the basic pattern in this notebook.

    > We are using [cosine similarity](https://www.engati.com/glossary/cosine-similarity) as a distance metric in this example - but there are many many distance metrics you could use - like [these](https://flavien-vidal.medium.com/similarity-distances-for-natural-language-processing-16f63cd5ba55)

    > We are using a rather inefficient way of calculating relative distance between the query vector and all other vectors - there are more advanced approaches that are much more efficient, like [ANN](https://towardsdatascience.com/comprehensive-guide-to-approximate-nearest-neighbors-algorithms-8b94f057d6b6)
    """)
    return


@app.cell
def _(vector_db):
    vector_db.search_by_text("What exercises help with lower back pain?", k=3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Prompts

    In the following section, we'll be looking at the role of prompts - and how they help us to guide our application in the right direction.

    In this notebook, we're going to rely on the idea of "zero-shot in-context learning".

    This is a lot of words to say: "We will ask it to perform our desired task in the prompt, and provide no examples."
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### XYZRolePrompt

    Before we do that, let's stop and think a bit about how OpenAI's chat models work.

    We know they have roles - as is indicated in the following API [documentation](https://platform.openai.com/docs/api-reference/chat/create#chat/create-messages)

    There are three roles, and they function as follows (taken directly from [OpenAI](https://platform.openai.com/docs/guides/gpt/chat-completions-api)):

    - `{"role" : "system"}` : The system message helps set the behavior of the assistant. For example, you can modify the personality of the assistant or provide specific instructions about how it should behave throughout the conversation. However note that the system message is optional and the model’s behavior without a system message is likely to be similar to using a generic message such as "You are a helpful assistant."
    - `{"role" : "user"}` : The user messages provide requests or comments for the assistant to respond to.
    - `{"role" : "assistant"}` : Assistant messages store previous assistant responses, but can also be written by you to give examples of desired behavior.

    The main idea is this:

    1. You start with a system message that outlines how the LLM should respond, what kind of behaviours you can expect from it, and more
    2. Then, you can provide a few examples in the form of "assistant"/"user" pairs
    3. Then, you prompt the model with the true "user" message.

    In this example, we'll be forgoing the 2nd step for simplicity's sake.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Utility Functions

    You'll notice that we're using some utility functions from the `aimakerspace` module - let's take a peek at these and see what they're doing!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### XYZRolePrompt
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here we have our `system`, `user`, and `assistant` role prompts.

    Let's take a peek at what they look like:

    ```python
    class BasePrompt:
        def __init__(self, prompt):
            \"\"\"
            Initializes the BasePrompt object with a prompt template.

            :param prompt: A string that can contain placeholders within curly braces
            \"\"\"
            self.prompt = prompt
            self._pattern = re.compile(r"\{([^}]+)\}")

        def format_prompt(self, **kwargs):
            \"\"\"
            Formats the prompt string using the keyword arguments provided.

            :param kwargs: The values to substitute into the prompt string
            :return: The formatted prompt string
            \"\"\"
            matches = self._pattern.findall(self.prompt)
            return self.prompt.format(**{match: kwargs.get(match, "\") for match in matches})

        def get_input_variables(self):
            \"\"\"
            Gets the list of input variable names from the prompt string.

            :return: List of input variable names
            \"\"\"
            return self._pattern.findall(self.prompt)
    ```

    Then we have our `RolePrompt` which laser focuses us on the role pattern found in most API endpoints for LLMs.

    ```python
    class RolePrompt(BasePrompt):
        def __init__(self, prompt, role: str):
            \"\"\"
            Initializes the RolePrompt object with a prompt template and a role.

            :param prompt: A string that can contain placeholders within curly braces
            :param role: The role for the message ('system', 'user', or 'assistant')
            \"\"\"
            super().__init__(prompt)
            self.role = role

        def create_message(self, **kwargs):
            \"\"\"
            Creates a message dictionary with a role and a formatted message.

            :param kwargs: The values to substitute into the prompt string
            :return: Dictionary containing the role and the formatted message
            \"\"\"
            return {"role": self.role, "content": self.format_prompt(**kwargs)}
    ```

    We'll look at how the `SystemRolePrompt` is constructed to get a better idea of how that extension works:

    ```python
    class SystemRolePrompt(RolePrompt):
        def __init__(self, prompt: str):
            super().__init__(prompt, "system")
    ```

    That pattern is repeated for our `UserRolePrompt` and our `AssistantRolePrompt` as well.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### ChatOpenAI
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next we have our model, which is converted to a format analogous to libraries like LangChain and LlamaIndex.

    Let's take a peek at how that is constructed:

    ```python
    class ChatOpenAI:
        def __init__(self, model_name: str = "gpt-4.1-mini"):
            self.model_name = model_name
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if self.openai_api_key is None:
                raise ValueError("OPENAI_API_KEY is not set")

        def run(self, messages, text_only: bool = True):
            if not isinstance(messages, list):
                raise ValueError("messages must be a list")

            openai.api_key = self.openai_api_key
            response = openai.ChatCompletion.create(
                model=self.model_name, messages=messages
            )

            if text_only:
                return response.choices[0].message.content

            return response
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### ❓ Question #3:

    When calling the OpenAI API - are there any ways we can achieve more reproducible outputs?

    > NOTE: Check out [this section](https://platform.openai.com/docs/guides/text-generation/) of the OpenAI documentation for the answer!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### ✅ Answer: Yes, we can submit context-free grammars to get structured outputs! Or we can let them do the structured outputs on their end, whatever floats your boat ig
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Creating and Prompting OpenAI's `gpt-4.1-mini`!

    Let's tie all these together and use it to prompt `gpt-4.1-mini`!
    """)
    return


@app.cell
def _():
    from aimakerspace.openai_utils.prompts import (
        UserRolePrompt,
        SystemRolePrompt,
        AssistantRolePrompt,
    )

    from aimakerspace.openai_utils.chatmodel import ChatOpenAI

    chat_openai = ChatOpenAI()
    user_prompt_template = "{content}"
    user_role_prompt = UserRolePrompt(user_prompt_template)
    system_prompt_template = (
        "You are an expert in {expertise}, you always answer in a kind way."
    )
    system_role_prompt = SystemRolePrompt(system_prompt_template)

    messages = [
        system_role_prompt.create_message(expertise="Python"),
        user_role_prompt.create_message(
            content="What is the best way to write a loop?"
        ),
    ]

    response = chat_openai.run(messages)
    return ChatOpenAI, SystemRolePrompt, UserRolePrompt, chat_openai, response


@app.cell
def _(response):
    print(response)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Retrieval Augmented Generation

    Now we can create a RAG prompt - which will help our system behave in a way that makes sense!

    There is much you could do here, many tweaks and improvements to be made!
    """)
    return


@app.cell
def _(SystemRolePrompt, UserRolePrompt):
    RAG_SYSTEM_TEMPLATE = """You are a helpful personal wellness assistant that answers health and wellness questions based strictly on provided context.

    Instructions:
    - Only answer questions using information from the provided context
    - If the context doesn't contain relevant information, respond with "I don't have information about that in my wellness knowledge base"
    - Be accurate and cite specific parts of the context when possible
    - Keep responses {response_style} and {response_length}
    - Only use the provided context. Do not use external knowledge.
    - Include a gentle reminder that users should consult healthcare professionals for medical advice when appropriate
    - Only provide answers when you are confident the context supports your response."""

    RAG_USER_TEMPLATE = """Context Information:
    {context}

    Number of relevant sources found: {context_count}
    {similarity_scores}

    Question: {user_query}

    Please provide your answer based solely on the context above."""

    rag_system_prompt = SystemRolePrompt(
        RAG_SYSTEM_TEMPLATE,
        strict=True,
        defaults={"response_style": "concise", "response_length": "brief"},
    )

    rag_user_prompt = UserRolePrompt(
        RAG_USER_TEMPLATE,
        strict=True,
        defaults={"context_count": "", "similarity_scores": ""},
    )
    return rag_system_prompt, rag_user_prompt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we can create our pipeline!
    """)
    return


@app.cell
def _(ChatOpenAI, VectorDatabase, rag_system_prompt, rag_user_prompt):
    class RetrievalAugmentedQAPipeline:
        def __init__(
            self,
            llm: ChatOpenAI,
            vector_db_retriever: VectorDatabase,
            response_style: str = "detailed",
            include_scores: bool = False,
        ) -> None:
            self.llm = llm
            self.vector_db_retriever = vector_db_retriever
            self.response_style = response_style
            self.include_scores = include_scores

        def run_pipeline(
            self, user_query: str, k: int = 4, **system_kwargs
        ) -> dict:
            # Retrieve relevant contexts
            context_list = self.vector_db_retriever.search_by_text(user_query, k=k)

            context_prompt = ""
            similarity_scores = []

            for i, (context, score) in enumerate(context_list, 1):
                context_prompt += f"[Source {i}]: {context}\n\n"
                similarity_scores.append(f"Source {i}: {score:.3f}")

            # Create system message with parameters
            system_params = {
                "response_style": self.response_style,
                "response_length": system_kwargs.get(
                    "response_length", "detailed"
                ),
            }

            formatted_system_prompt = rag_system_prompt.create_message(
                **system_params
            )

            user_params = {
                "user_query": user_query,
                "context": context_prompt.strip(),
                "context_count": len(context_list),
                "similarity_scores": f"Relevance scores: {', '.join(similarity_scores)}"
                if self.include_scores
                else "",
            }

            formatted_user_prompt = rag_user_prompt.create_message(**user_params)

            return {
                "response": self.llm.run(
                    [formatted_system_prompt, formatted_user_prompt]
                ),
                "context": context_list,
                "context_count": len(context_list),
                "similarity_scores": similarity_scores
                if self.include_scores
                else None,
                "prompts_used": {
                    "system": formatted_system_prompt,
                    "user": formatted_user_prompt,
                },
            }
    return (RetrievalAugmentedQAPipeline,)


@app.cell
def _(RetrievalAugmentedQAPipeline, chat_openai, vector_db):
    rag_pipeline = RetrievalAugmentedQAPipeline(
        vector_db_retriever=vector_db,
        llm=chat_openai,
        response_style="detailed",
        include_scores=True,
    )

    result = rag_pipeline.run_pipeline(
        "What are some natural remedies for improving sleep quality?",
        k=3,
        response_length="comprehensive",
        include_warnings=True,
        confidence_required=True,
    )

    print(f"Response: {result['response']}")
    print(f"\nContext Count: {result['context_count']}")
    print(f"Similarity Scores: {result['similarity_scores']}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### ❓ Question #4:

    What prompting strategies could you use to make the LLM have a more thoughtful, detailed response?

    What is that strategy called?

    > NOTE: You can look through our [OpenAI Responses API](https://colab.research.google.com/drive/14SCfRnp39N7aoOx8ZxadWb0hAqk4lQdL?usp=sharing) notebook for an answer to this question if you get stuck!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##### ✅ Answer: CoT (and derivatives, my fav is Thread of Thought), self-criticism, ensembling,
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🏗️ Activity #1:

    Enhance your Personal Wellness Assistant in some way!

    Suggestions are:

    - **PDF Support**: Allow it to ingest wellness PDFs (meal plans, workout guides, medical information sheets)
    - **New Distance Metric**: Implement a different similarity measure - does it improve retrieval for health queries?
    - **Metadata Support**: Add metadata like topic categories (exercise, nutrition, sleep) or difficulty levels to help filter results
    - **Different Embedding Model**: Try a different embedding model - does domain-specific tuning help for health content?
    - **Multi-Source Ingestion**: Add the capability to ingest content from YouTube health videos, podcasts, or health blogs

    While these are suggestions, you should feel free to make whatever augmentations you desire! Think about what features would make this wellness assistant most useful for your personal health journey.

    When you're finished making the augments to your RAG application - vibe check it against the old one - see if you can "feel the improvement"!

    > NOTE: These additions might require you to work within the `aimakerspace` library - that's expected!

    > NOTE: If you're not sure where to start - ask Cursor (CMD/CTRL+L) to guide you through the changes!
    """)
    return


@app.cell
def _(text_splitter, vector_db):
    ### YOUR CODE HERE
    from aimakerspace.pdf_utils import PDFIngestionPipeline

    pdf_support = PDFIngestionPipeline(
        vector_db=vector_db, text_splitter=text_splitter
    )

    text = pdf_support.extract_text_from_pdf("data/PhD CV.pdf")
    split_text = pdf_support.split_text(text)
    pdf_support.add_to_vector_db(split_text)
    vector_db.search_by_text("What was I doing in 2023?", k=3)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
