#!/usr/bin/env python3
"""Test script to verify core functionality works."""

import os

os.environ["OPENAI_API_KEY"] = "dummy-key"

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print("=" * 60)
print("Testing Open-Source Components (No Tracing)")
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
    embedding = embeddings.embed_query("test")
    print(f"   ✓ Embedding dimension: {len(embedding)}")
except Exception as e:
    print(f"   ✗ Embeddings Error: {e}")

print("\n" + "=" * 60)
print("All core tests completed!")
print("=" * 60)
