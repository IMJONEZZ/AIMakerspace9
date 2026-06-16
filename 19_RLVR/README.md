# Session 19: RLVR for Financial Compliance and Risk Alignment

| 📋 Session Sheet | 🎥 Recording | 📊 Slides | 👾 Repo | 📝 Homework | 📣 Feedback |
|-----------------|-------------|-----------|---------|-------------|-------------|
| [Session Sheet](https://aimakerspace.io) | [Recording!](https://youtube.com) | [Slides](https://google.com) | You are here! | [Assignment](https://github.com) | [Feedback](https://forms.gle) |

---

## Prerequisites
1. **Environment**: Create a `.env` file with your `OPENAI_API_KEY`.
2. **Data**: This module uses `finance_ground_truth.txt` to verify model outputs.
3. **Objective**: Use Reinforcement Learning (GRPO) to ensure the model aligns investment risk with user age and follows regulatory compliance.

---

## Build 🏗️
### 🤝 Breakout Room #1 — Verifiable Finance Rewards
- **Activity #1**: Implement a reward function that penalizes "Aggressive" advice for "Conservative" users based on the Age-Based Risk Rule in our ground truth file.

### 🤝 Breakout Room #2 — Compliance Training
- **Activity #2**: Train **Qwen 1.5B** to automatically include financial disclaimers and age-appropriate asset allocations using the GRPO loop.

---

## Advanced Build 🏋️ (Optional)
See `RLVR_Advanced_Assignment.ipynb` to implement **Process-Oriented Rewards**:
- Reward the model for "showing its math" in `<thought>` tags when calculating a user's Debt-to-Income ratio.