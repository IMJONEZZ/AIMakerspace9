# LangChain + LMStudio Compatibility Fix

## Problem Summary

Your system is experiencing critical compatibility issues between LangChain's `with_structured_output()` method and LMStudio's OpenAI-compatible API.

### Error 1: `response_format.type` must be 'json_schema' or 'text'
- **Cause**: LangChain's `method="json_mode"` sends `response_format.type: "json_object"`
- **LMStudio Issue**: #189 (open since Nov 2024)
- **Status**: LMStudio only accepts `"json_schema"` or `"text"`, not `"json_object"`

### Error 2: Invalid `tool_choice` type: 'object'
- **Cause**: LangChain's `method="function_calling"` sends `tool_choice` as an object
- **LMStudio Issue**: #670 (open since May 2025)
- **Status**: LMStudio only accepts string values: `"none"`, `"auto"`, or `"required"`

## Root Cause

LMStudio has strict OpenAI API compatibility validation that rejects:
1. `response_format.type = "json_object"` (requires `"json_schema"` or `"text"`)
2. `tool_choice = {"type": "function", "function": {...}}` (requires string values)

LangChain's `with_structured_output()` method uses these incompatible formats internally.

## Solution Applied

I've modified the codebase to use `PydanticOutputParser` instead of `with_structured_output()`:

### 1. Updated Imports
Added to `open_deep_library/deep_researcher.py`:
```python
import json
from langchain_core.output_parsers import PydanticOutputParser
```

### 2. Modified `clarify_with_user()` function
**Before:**
```python
clarification_model = (
    configurable_model
    .with_structured_output(ClarifyWithUser, method="function_calling")
    .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
    .with_config(model_config)
)
response = await clarification_model.ainvoke([HumanMessage(content=prompt_content)])
```

**After:**
```python
parser = PydanticOutputParser(pydantic_object=ClarifyWithUser)
clarification_model = (
    configurable_model
    .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
    .with_config(model_config)
)

prompt_content = clarify_with_user_instructions.format(
    messages=get_buffer_string(messages),
    date=get_today_str(),
    format_instructions=parser.get_format_instructions()
)

raw_response = await clarification_model.ainvoke([HumanMessage(content=prompt_content)])
response = parser.parse(raw_response.content)
```

### 3. Modified `write_research_brief()` function
Same pattern as above, using `PydanticOutputParser` with `ResearchQuestion` schema.

### 4. Updated Prompts
Added `{format_instructions}` placeholders to:
- `clarify_with_user_instructions`
- `transform_messages_into_research_topic_prompt`

### 5. Added Helper Function
Created `parse_structured_output_with_retry()` in `utils.py` for robust parsing with retry logic.

## How It Works

1. **PydanticOutputParser** generates format instructions that tell the model exactly what JSON structure to output
2. The model receives these instructions in the system prompt
3. The model outputs JSON as text (not via structured output API)
4. `PydanticOutputParser.parse()` validates and converts the JSON to your Pydantic model
5. If parsing fails, retry logic kicks in with error feedback

## Benefits

- ✅ Works with LMStudio's strict API validation
- ✅ Compatible with any OpenAI-compatible API
- ✅ More control over error handling and retries
- ✅ No dependency on `with_structured_output()` method
- ✅ Works with all models (local, hosted, OpenAI, Anthropic, etc.)

## LMStudio's Supported Format

LMStudio supports structured output via `response_format` with `json_schema`:

```python
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "my_schema",
        "strict": "true",
        "schema": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

However, LangChain's `with_structured_output()` doesn't use this format directly, which is why we're using `PydanticOutputParser` as a workaround.

## Alternative Solutions (Not Implemented)

### Option A: Use OpenAI Client Directly
```python
from openai import OpenAI
import json

client = OpenAI(base_url="http://192.168.1.79:8080/v1", api_key="lm-studio")

response = client.chat.completions.create(
    model="glm-4.7",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "clarify_response",
            "strict": "true",
            "schema": ClarifyWithUser.model_json_schema()
        }
    }
)
result = json.loads(response.choices[0].message.content)
```

### Option B: Subclass ChatOpenAI
Create a custom ChatOpenAI subclass that intercepts requests and converts:
- `tool_choice` object → `tool_choice: "auto"`
- `response_format.type: "json_object"` → `response_format.type: "json_schema"`

### Option C: Wait for LMStudio Updates
LMStudio team is aware of these issues:
- Issue #189: Support for `json_object` response_format
- Issue #670: Support for object-type `tool_choice`

## Testing the Fix

1. Ensure LMStudio is running at `http://192.168.1.79:8080/v1`
2. Load your model (glm-4.7) in LMStudio
3. Run your research workflow
4. The system should now successfully:
   - Ask clarifying questions (if enabled)
   - Generate research briefs
   - Without the 400 errors

## References

- LMStudio Issue #189: https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/189
- LMStudio Issue #670: https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/670
- LMStudio Structured Output Docs: https://lmstudio.ai/docs/developer/openai-compat/structured-output
- LangChain Structured Output Docs: https://python.langchain.com/docs/how_to/structured_output/

## Notes

- This fix maintains backward compatibility with other model providers (OpenAI, Anthropic, etc.)
- The retry logic in `parse_structured_output_with_retry()` handles malformed JSON gracefully
- Format instructions are automatically generated from your Pydantic models
