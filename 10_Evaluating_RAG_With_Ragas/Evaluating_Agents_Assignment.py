import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 10: Using Ragas to Evaluate an Agent Application built with LangChain and LangGraph

    In the following notebook, we'll be looking at how [Ragas](https://github.com/explodinggradients/ragas) can be helpful in a number of ways when looking to evaluate your RAG applications!

    While this example is rooted in LangChain/LangGraph - Ragas is framework agnostic (you don't even need to be using a framework!).

    We'll:

    - Collect our data
    - Create a simple Agent application
    - Evaluate our Agent application

    > NOTE: This notebook is very lightly modified from Ragas' [LangGraph tutorial](https://docs.ragas.io/en/stable/howtos/integrations/_langgraph_agent_evaluation/)!

    ## 🤝 Breakout Room #2
      - Task 1: Installing Required Libraries
      - Task 2: Set Environment Variables
      - Task 3: Building a ReAct Agent with Metal Price Tool
      - Task 4: Implementing the Agent Graph Structure
      - Task 5: Converting Agent Messages to Ragas Evaluation Format
      - Task 6: Evaluating the Agent's Performance using Ragas Metrics
      - ***Activity #1: Evaluate Tool Call Accuracy***
      - ***Activity #2: Evaluate Topic Adherence***
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 1: Installing Required Libraries

    If you have not already done so, install the required libraries using the uv package manager:
    ``` bash

    uv sync

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 2: Set Environment Variables:

    We'll also need to provide our API keys.
    > NOTE: In addition to OpenAI's models, this notebook will be creating a metals pricing tool using the API from metals.dev. Please be sure to sign up for an account on [metals.dev](https://metals.dev/) to get your API key.
    You have two options for supplying your API keys in this session:
    - Use environment variables (see Prerequisite #2 in the README.md)
    - Provide them via a prompt when the notebook runs

    The following code will load all of the environment variables in your `.env`. Then, it checks for the two API keys we need. If they are not there, it will prompt you to provide them.

    First, OpenAI's for our LLM/embedding model combination!

    Second, metals.dev's for our metals pricing tool.
    """)
    return


@app.cell
def _():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "Dummy-API-Key"
    return


@app.cell
def _():
    from langfuse import get_client
    from langfuse.langchain import CallbackHandler

    langfuse = get_client()
    langfuse_handler = CallbackHandler()
    return (langfuse_handler,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 3: Building a ReAct Agent with Metal Price Tool
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Define the get_metal_price Tool

    The get_metal_price tool will be used by the agent to fetch the price of a specified metal. We'll create this tool using the @tool decorator from LangChain.
    """)
    return


@app.cell
def _():
    import json
    from pathlib import Path
    from langchain_core.tools import tool

    @tool
    def get_metal_price(metal_name: str) -> float:
        """Fetches the current per gram price of the specified metal.

        Args:
            metal_name : The name of the metal (e.g., 'gold', 'silver', 'platinum').

        Returns:
            float: The current price of the metal in dollars per gram.

        Raises:
            KeyError: If the specified metal is not found in the data source.
        """
        try:
            metal_name = metal_name.lower().strip()

            data_path = Path(__file__).parent / "data" / "metals_prices.json"
            with open(data_path, "r") as f:
                metal_data = json.load(f)

            available_metals = [k for k in metal_data.keys() if k != "last_updated"]
            if metal_name not in metal_data:
                raise KeyError(
                    f"Metal '{metal_name}' not found. Available metals: {', '.join(available_metals)}"
                )
            return metal_data[metal_name]
        except Exception as e:
            raise Exception(f"Error fetching metal price: {str(e)}")

    @tool
    def calculate(expression: str) -> str:
        """Evaluate a mathematical expression. Use this for any math calculations.

        Args:
            expression: A mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')
        """
        try:
            # Using eval with restricted globals for safety
            result = eval(expression, {"__builtins__": {}}, {})
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error evaluating expression: {e}"

    return calculate, get_metal_price


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Binding the Tool to the LLM
    With the get_metal_price tool defined, the next step is to bind it to the ChatOpenAI model. This enables the agent to invoke the tool during its execution based on the user's requests allowing it to interact with external data and perform actions beyond its native capabilities.
    """)
    return


@app.cell
def _(get_metal_price):
    from langchain_openai import ChatOpenAI

    _tools = [get_metal_price]
    llm = ChatOpenAI(
        model="minimax-m2.5-mlx@4bit", base_url="http://192.168.1.79:8080/v1"
    )
    llm_with_tools = llm.bind_tools(_tools)
    return ChatOpenAI, llm_with_tools


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 4: Implementing the Agent Graph Structure

    In LangGraph, state plays a crucial role in tracking and updating information as the graph executes. As different parts of the graph run, the state evolves to reflect the changes and contains information that is passed between nodes.

    For example, in a conversational system like this one, the state is used to track the exchanged messages. Each time a new message is generated, it is added to the state and the updated state is passed through the nodes, ensuring the conversation progresses logically.

    ### Defining the State
    To implement this in LangGraph, we define a state class that maintains a list of messages. Whenever a new message is produced it gets appended to this list, ensuring that the conversation history is continuously updated.
    """)
    return


@app.cell
def _():
    from typing import Annotated

    from langchain_core.messages import AnyMessage
    from langgraph.graph import END
    from langgraph.graph.message import add_messages
    from typing_extensions import TypedDict

    class GraphState(TypedDict):
        messages: Annotated[list[AnyMessage], add_messages]

    return END, GraphState


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Defining the should_continue Function
    The `should_continue` function determines whether the conversation should proceed with further tool interactions or end. Specifically, it checks if the last message contains any tool calls (e.g., a request for metal prices).

    - If the last message includes tool calls, indicating that the agent has invoked an external tool, the conversation continues and moves to the "tools" node.
    - If there are no tool calls, the conversation ends, represented by the END state.
    """)
    return


@app.cell
def _(END, GraphState):
    # Define the function that determines whether to continue or not
    def should_continue(state: GraphState):
        _messages = state["messages"]
        last_message = _messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    return (should_continue,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Calling the Model
    The `call_model` function interacts with the Language Model (LLM) to generate a response based on the current state of the conversation. It takes the updated state as input, processes it and returns a model-generated response.
    """)
    return


@app.cell
def _(GraphState, llm_with_tools):
    # Define the function that calls the model
    def call_model(state: GraphState):
        _messages = state["messages"]
        response = llm_with_tools.invoke(_messages)
        return {"messages": [response]}

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Creating the Assistant Node
    The `assistant` node is a key component responsible for processing the current state of the conversation and using the Language Model (LLM) to generate a relevant response. It evaluates the state, determines the appropriate course of action, and invokes the LLM to produce a response that aligns with the ongoing dialogue.
    """)
    return


@app.cell
def _(GraphState, llm_with_tools):
    # Node
    def assistant(state: GraphState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    return (assistant,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Creating the Tool Node
    The `tool_node` is responsible for managing interactions with external tools, such as fetching metal prices or performing other actions beyond the LLM's native capabilities. The tools themselves are defined earlier in the code, and the tool_node invokes these tools based on the current state and the needs of the conversation.
    """)
    return


@app.cell
def _(calculate, get_metal_price):
    from langgraph.prebuilt import ToolNode

    _tools = [get_metal_price, calculate]
    # Node
    tool_node = ToolNode(_tools)
    return (tool_node,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Building the Graph
    The graph structure is the backbone of the agentic workflow, consisting of interconnected nodes and edges. To construct this graph, we use the StateGraph builder which allows us to define and connect various nodes. Each node represents a step in the process (e.g., the assistant node, tool node) and the edges dictate the flow of execution between these steps.
    """)
    return


@app.cell
def _(END, GraphState, assistant, should_continue, tool_node):
    from IPython.display import Image, display
    from langgraph.graph import START, StateGraph

    # Define a new graph for the agent
    builder = StateGraph(GraphState)

    # Define the two nodes we will cycle between
    builder.add_node("assistant", assistant)
    builder.add_node("tools", tool_node)

    # Set the entrypoint as `agent`
    builder.add_edge(START, "assistant")

    # Making a conditional edge
    # should_continue will determine which node is called next.
    builder.add_conditional_edges("assistant", should_continue, ["tools", END])

    # Making a normal edge from `tools` to `agent`.
    # The `agent` node will be called after the `tool`.
    builder.add_edge("tools", "assistant")

    # Compile and display the graph for a visual overview
    react_graph = builder.compile()
    return (react_graph,)


@app.cell
def _(react_graph):
    react_graph
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To test our setup, we will run the agent with a query. The agent will fetch the price of copper using the metals.dev API.
    """)
    return


@app.cell
def _(langfuse_handler, react_graph):
    from langchain_core.messages import HumanMessage

    _messages = [HumanMessage(content="What is the price of copper?")]
    result = react_graph.invoke(
        {"messages": _messages}, config={"callbacks": [langfuse_handler]}
    )
    return HumanMessage, result


@app.cell
def _(result):
    result["messages"]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 5: Converting Agent Messages to Ragas Evaluation Format

    In the current implementation, the GraphState stores messages exchanged between the human user, the AI (LLM's responses), and any external tools (APIs or services the AI uses) in a list. Each message is an object in LangChain's format

    ```python
    # Implementation of Graph State
    class GraphState(TypedDict):
        messages: Annotated[list[AnyMessage], add_messages]
    ```

    Each time a message is exchanged during agent execution, it gets added to the messages list in the GraphState. However, Ragas requires a specific message format for evaluating interactions.

    Ragas uses its own format to evaluate agent interactions. So, if you're using LangGraph, you will need to convert the LangChain message objects into Ragas message objects. This allows you to evaluate your AI agents with Ragas’ built-in evaluation tools.

    **Goal:**  Convert the list of LangChain messages (e.g., HumanMessage, AIMessage, and ToolMessage) into the format expected by Ragas, so the evaluation framework can understand and process them properly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To convert a list of LangChain messages into a format suitable for Ragas evaluation, Ragas provides the function [convert_to_ragas_messages][ragas.integrations.langgraph.convert_to_ragas_messages], which can be used to transform LangChain messages into the format expected by Ragas.

    Here's how you can use the function:
    """)
    return


@app.cell
def _(result):
    from ragas.integrations.langgraph import convert_to_ragas_messages

    # Assuming 'result["messages"]' contains the list of LangChain messages
    ragas_trace = convert_to_ragas_messages(result["messages"])
    return convert_to_ragas_messages, ragas_trace


@app.cell
def _(ragas_trace):
    ragas_trace  # List of Ragas messages
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #1:

    Describe in your own words what a "trace" is.

    ##### Answer:

    *A trace is _meant_ to be a full context capture of an interaction with an LLM. In practice, it's impossible to actually get full context, especially with syntax-only systems, so we just make do.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Task 6: Evaluating the Agent's Performance  using Ragas Metrics
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For this tutorial, let us evaluate the Agent with the following metrics:

    - [Tool call Accuracy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/agents/#tool-call-accuracy):ToolCallAccuracy is a metric that can be used to evaluate the performance of the LLM in identifying and calling the required tools to complete a given task.

    - [Agent Goal accuracy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/agents/#agent-goal-accuracy): Agent goal accuracy is a metric that can be used to evaluate the performance of the LLM in identifying and achieving the goals of the user. This is a binary metric, with 1 indicating that the AI has achieved the goal and 0 indicating that the AI has not achieved the goal.
    - [Topic Adherence](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/agents/): Topic adherence is a metric that can be used to ensure the Agent system is staying "on-topic", meaning that it's not straying from the intended use case. You can think of this as a kinda of faithfulness, where the responses of the LLM should stay faithful to the topic provided.


    First, let us actually run our Agent with a couple of queries, and make sure we have the ground truth labels for these queries.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #2:

    Describe *how* each of the above metrics are calculated. This will require you to read the documentation for each metric.

    ##### Answer:

    *Tool Call Accuracy: Compares actual tool calls against reference tool calls, evaluating both sequence alignment (whether tools are called in the correct order) and argument accuracy (whether parameters match). The final score is argument accuracy multiplied by 1 if sequence aligns, or 0 if not.
    Agent Goal Accuracy: A binary metric (0 or 1) that evaluates whether the agent achieved the user's goal. WithReference compares the final outcome against a provided reference; WithoutReference infers both the intended goal and achieved outcome from the conversation, then determines if they match.
    Topic Adherence: Uses precision, recall, and F1 score to measure how well the AI stays on predefined topics. Precision = answered queries adhering to reference topics / all answered queries; Recall = answered queries adhering to topics / (answered adhering + queries that should have been refused).*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Tool Call Accuracy
    """)
    return


@app.cell
async def _(ChatOpenAI, convert_to_ragas_messages, result):
    import ragas.messages as r
    from ragas.dataset_schema import MultiTurnSample
    from ragas.metrics import ToolCallAccuracy

    ragas_trace_1 = convert_to_ragas_messages(messages=result["messages"])
    _sample = MultiTurnSample(
        user_input=ragas_trace_1,
        reference_tool_calls=[
            r.ToolCall(name="get_metal_price", args={"metal_name": "copper"})
        ],
    )
    tool_accuracy_scorer = ToolCallAccuracy()
    tool_accuracy_scorer.llm = ChatOpenAI(
        model="minimax-m2.5-mlx@4bit",
        base_url="http://192.168.1.79:8080/v1",
        api_key="dummy-key",
    )
    await tool_accuracy_scorer.multi_turn_ascore(_sample)
    return MultiTurnSample, ToolCallAccuracy


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Tool Call Accuracy: 1, because the LLM correctly identified and used the necessary tool (get_metal_price) with the correct parameters (i.e., metal name as "copper").
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Agent Goal Accuracy
    """)
    return


@app.cell
def _(HumanMessage, langfuse_handler, react_graph):
    _messages = [HumanMessage(content="What is the price of 10 grams of silver?")]
    result_1 = react_graph.invoke(
        {"messages": _messages}, config={"callbacks": [langfuse_handler]}
    )
    return (result_1,)


@app.cell
def _(result_1):
    result_1["messages"]  # List of Langchain messages
    return


@app.cell
def _(convert_to_ragas_messages, result_1):
    ragas_trace_2 = convert_to_ragas_messages(result_1["messages"])
    ragas_trace_2  # List of Ragas messages converted using the Ragas function
    return (ragas_trace_2,)


@app.cell
async def _(ChatOpenAI, MultiTurnSample, ragas_trace_2):
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import AgentGoalAccuracyWithReference

    _sample = MultiTurnSample(
        user_input=ragas_trace_2, reference="Price of 10 grams of silver"
    )
    _scorer = AgentGoalAccuracyWithReference()
    _evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="minimax-m2.5-mlx@4bit",
            base_url="http://192.168.1.79:8080/v1",
            api_key="dummy-key",
        )
    )
    _scorer.llm = _evaluator_llm
    await _scorer.multi_turn_ascore(_sample)
    return (LangchainLLMWrapper,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Agent Goal Accuracy: 1, because the LLM correctly achieved the user’s goal of retrieving the price of 10 grams of silver.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Topic Adherence
    """)
    return


@app.cell
def _(HumanMessage, langfuse_handler, react_graph):
    _messages = [HumanMessage(content="How fast can an eagle fly?")]
    result_2 = react_graph.invoke(
        {"messages": _messages}, config={"callbacks": [langfuse_handler]}
    )
    return (result_2,)


@app.cell
def _(result_2):
    result_2["messages"]
    return


@app.cell
def _(convert_to_ragas_messages, result_2):
    ragas_trace_3 = convert_to_ragas_messages(result_2["messages"])
    ragas_trace_3  # List of Ragas messages converted using the Ragas function
    return (ragas_trace_3,)


@app.cell
async def _(ChatOpenAI, LangchainLLMWrapper, MultiTurnSample, ragas_trace_3):
    from ragas.metrics import TopicAdherenceScore

    _sample = MultiTurnSample(user_input=ragas_trace_3, reference_topics=["metals"])
    _evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="minimax-m2.5-mlx@4bit",
            base_url="http://192.168.1.79:8080/v1",
            api_key="dummy-key",
        )
    )
    _scorer = TopicAdherenceScore(llm=_evaluator_llm, mode="precision")
    await _scorer.multi_turn_ascore(_sample)
    return (TopicAdherenceScore,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As we can see, the current implementation fails due to talking about birds, when it should be talking about metal!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #3:

    If you were deploying this metal price agent as a production wellness assistant (imagine it's a financial wellness tool for tracking investment metals), what are the implications of each metric (Tool Call Accuracy, Agent Goal Accuracy, Topic Adherence) for user trust and safety?

    ##### Answer:

    *Tool Call Accuracy matters most—if it calls the wrong metal or wrong parameters, users get bad price data and could make poor investment decisions. Agent Goal Accuracy ensures the tool actually delivers what users need, which builds trust over time. Topic Adherence keeps the assistant focused on finance; if it starts rambling about unrelated topics, users will question whether it's actually helping with their investment goals.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #4:

    How would you design a comprehensive test suite for evaluating this metal price agent? What test cases would you include to ensure robustness across the three metrics (Tool Call Accuracy, Agent Goal Accuracy, Topic Adherence)?

    ##### Answer:

    *A solid test suite would cover correct metals (gold, silver, platinum), invalid metal names for error handling, multi-step queries requiring sequential tool calls, off-topic requests to verify topic adherence fails appropriately, and various user goals like simple price lookups vs. calculations.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Activity #1: Evaluate Tool Call Accuracy with a New Query

    Create a new test case for Tool Call Accuracy. Run the agent with a different metal query (e.g., "What is the price of platinum?") and evaluate its tool call accuracy.

    **Requirements:**
    1. Create a new query for the agent
    2. Run the agent and collect the trace
    3. Define the expected reference tool calls
    4. Evaluate using ToolCallAccuracy
    5. Document your results
    """)
    return


@app.cell
async def _(
    ChatOpenAI,
    HumanMessage,
    MultiTurnSample,
    ToolCallAccuracy,
    convert_to_ragas_messages,
    langfuse_handler,
    react_graph,
):
    ### YOUR CODE HERE ###

    # 1. Create a new query (and a new tool)
    query_1 = "Compare the price of silver to the price of platinum. What percentage is the price of silver of the price of platinum?"

    # 2. Run the agent
    messages_1 = [HumanMessage(content=query_1)]
    result_activity_1 = react_graph.invoke(
        {"messages": messages_1}, config={"callbacks": [langfuse_handler]}
    )

    # 3. Convert to Ragas format
    ragas_trace_4 = convert_to_ragas_messages(result_activity_1["messages"])

    # 4. Create MultiTurnSample with reference_tool_calls
    from ragas.messages import ToolCall

    sample_1 = MultiTurnSample(
        user_input=ragas_trace_4,
        reference_tool_calls=[
            ToolCall(name="get_metal_price", args={"metal_name": "silver"}),
            ToolCall(name="get_metal_price", args={"metal_name": "platinum"}),
            ToolCall(name="calculate", args={"expression": "(77.0305 / 2026.834) x 100"})
        ],
    )

    # 5. Evaluate with ToolCallAccuracy
    tool_accuracy_scorer_1 = ToolCallAccuracy()
    tool_accuracy_scorer_1.llm = ChatOpenAI(
        model="minimax-m2.5-mlx@4bit",
        base_url="http://192.168.1.79:8080/v1",
        api_key="dummy-key",
    )
    score_1 = await tool_accuracy_scorer_1.multi_turn_ascore(sample_1)
    return ragas_trace_4, score_1


@app.cell
def _(ragas_trace_4):
    ragas_trace_4
    return


@app.cell
def _(score_1):
    score_1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Activity #2: Evaluate Topic Adherence with an On-Topic Query

    Create a test case that should PASS the Topic Adherence check. Run the agent with a metals-related query and verify it stays on topic.

    **Requirements:**
    1. Create a metals-related query for the agent
    2. Run the agent and collect the trace
    3. Create a MultiTurnSample with reference_topics=["metals"]
    4. Evaluate using TopicAdherenceScore
    5. The score should be 1.0 (or close to it) since the query is on-topic
    """)
    return


@app.cell
async def _(
    ChatOpenAI,
    HumanMessage,
    LangchainLLMWrapper,
    MultiTurnSample,
    TopicAdherenceScore,
    convert_to_ragas_messages,
    langfuse_handler,
    react_graph,
):


    ### YOUR CODE HERE ###

    # 1. Create a metals-related query (more complex to test topic adherence)
    query_2 = "Compare gold, silver, and platinum. Which one has been the best investment over the past year?"

    # 2. Run the agent
    messages_2 = [HumanMessage(content=query_2)]
    result_activity_2 = react_graph.invoke(
        {"messages": messages_2}, config={"callbacks": [langfuse_handler]}
    )

    # 3. Convert to Ragas format
    ragas_trace_5 = convert_to_ragas_messages(result_activity_2["messages"])

    # 4. Create MultiTurnSample with reference_topics=["metals"]
    sample_2 = MultiTurnSample(user_input=ragas_trace_5, reference_topics=["metals"])

    # 5. Evaluate with TopicAdherenceScore
    evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="minimax-m2.5-mlx@4bit",
            base_url="http://192.168.1.79:8080/v1",
            api_key="dummy-key",
        )
    )
    topic_scorer = TopicAdherenceScore(llm=evaluator_llm, mode="precision")
    score_2 = await topic_scorer.multi_turn_ascore(sample_2)
    print(f"{('\n\n').join([i.content for i in result_activity_2['messages']])}")
    print(f"Topic Adherence Score: {score_2}")
    return


if __name__ == "__main__":
    app.run()
