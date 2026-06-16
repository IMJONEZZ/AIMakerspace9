# %% [markdown]
# Session 19: RLVR for Financial AI

# %%
import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM

print(torch.__version__)
print("GPU:", torch.cuda.is_available())

# %%
user_profile = {
    "age": 60,
    "income": 70000,
    "risk_tolerance": "low",
    "goals": ["retirement income"],
    "assets": 500000
}

# %%
def reward_100_rule(response, user_profile):
    max_stock = 100 - user_profile["age"]
    match = re.search(r"(\d+)%\s*(stocks|equities)", response.lower())
    if match:
        return 1.0 if int(match.group(1)) <= max_stock else 0.0
    return 0.5

def reward_disclaimer(response):
    return 1.0 if "not financial advice" in response.lower() else 0.0

def reward_diversification(response):
    assets = ["stocks", "bonds", "etf", "cash"]
    count = sum(a in response.lower() for a in assets)
    return 1.0 if count >= 2 else 0.0

def compute_total_reward(response, user_profile):
    r = {
        "100_rule": reward_100_rule(response, user_profile),
        "disclaimer": reward_disclaimer(response),
        "diversification": reward_diversification(response),
    }
    r["total"] = sum(r.values()) / len(r)
    return r

# %%
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, device_map="auto")

# %%
def generate(prompt, n=2):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = []
    for _ in range(n):
        out = model.generate(**inputs, max_new_tokens=120, temperature=0.8)
        outputs.append(tokenizer.decode(out[0], skip_special_tokens=True))
    return outputs

# %%
responses = generate("What should I invest in at age 60?")
for r in responses:
    print("\n---")
    print(r)
    print(compute_total_reward(r, user_profile))
