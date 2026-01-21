#!/usr/bin/env python3
"""Test script to verify the agent loop works with open-source components."""

import os

# Set environment variables for local services
os.environ["OPENAI_API_KEY"] = "dummy-key"
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-test"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-test"
os.environ["LANGFUSE_BASE_URL"] = "http://localhost:3000"

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langfuse import get_client
from langfuse.langchain import CallbackHandler

print("=" * 60)
print("Testing Open-Source Components")
print("=" * 60)

# Test 1: LangChain with local LLM
print("\n1. Testing ChatOpenAI with local endpoint...")
try:
    llm = ChatOpenAI(
        model="openai/gpt-oss-120b",
        base_url="http://192.168.1.79:8080/v1",
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human", "Say hello in one word."),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": "hello"})
    print(f"   ✓ LLM Response: {response[:50]}")
except Exception as e:
    print(f"   ✗ LLM Error: {e}")

# Test 2: Embeddings with local endpoint
print("\n2. Testing OpenAIEmbeddings with local endpoint...")
try:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-nomic-embed-text-v2-moe",
        base_url="http://192.168.1.79:8080/v1",
    )
    embedding = embeddings.embed_query("test sentence")
    print(f"   ✓ Embedding dimension: {len(embedding)}")
except Exception as e:
    print(f"   ✗ Embeddings Error: {e}")

# Test 3: LangFuse initialization
print("\n3. Testing LangFuse initialization...")
try:
    langfuse = get_client()
    langfuse_handler = CallbackHandler()
    print(f"   ✓ LangFuse client initialized")
    print(f"   ✓ CallbackHandler created: {type(langfuse_handler).__name__}")
except Exception as e:
    print(f"   ✗ LangFuse Error: {e}")

# Test 4: LangChain with LangFuse callback
print("\n4. Testing LangChain with LangFuse tracing...")
try:
    response_with_trace = chain.invoke(
        {"question": "what is 2+2?"}, config={"callbacks": [langfuse_handler]}
    )
    print(f"   ✓ Response with tracing: {response_with_trace[:50]}")
    langfuse.flush()
    print(f"   ✓ Traces flushed to LangFuse")
except Exception as e:
    print(f"   ✗ Tracing Error: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
