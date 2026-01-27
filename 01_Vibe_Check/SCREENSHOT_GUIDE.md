SCREENSHOT GUIDE FOR VIBE CHECK ASSIGNMENT
==========================================

## Screenshots Required

You need to take screenshots of 10 test interactions with your application (5 from Activity #1, 3 from Activity #2, 2 from Activity #3).

## How to Take Screenshots

### Option 1: Using Web Browser (http://localhost:3000)

1. Open your web browser and go to: http://localhost:3000
2. For each test prompt below:
   - Type the prompt in the chat input
   - Press Enter or click Send
   - Wait for the AI response
   - Take a screenshot of the conversation

### Option 2: Using Terminal Test Results

Since we tested via curl commands and saved responses, you can capture screenshots of the VIBE_CHECK_RESULTS.md file which contains all responses.

## Recommended Prompt Screenshots

### Activity #1 Prompts (5 screenshots):

1. **OOP Explanation**: "Explain the concept of object-oriented programming in simple terms to a complete beginner."
2. **Text Summary**: "Read the following paragraph and provide a concise summary of the key points: Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves. Deep learning is a specialized subset of machine learning that uses artificial neural networks with multiple layers to progressively extract higher-level features from raw input."
3. **Creative Story**: "Write a short, imaginative story (100–150 words) about a robot finding friendship in an unexpected place."
4. **Math Problem**: "If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each do I need to buy to get exactly 12 apples and 9 oranges?"
5. **Formal Tone**: "Rewrite the following paragraph in a professional, formal tone: Hey guys, so like, I was thinking maybe we could, you know, totally change the whole way we do our project. It would be super cool if we could make it way more organized and stuff. I mean, it is kind of a mess right now and we should probably fix it."

### Activity #2 Prompts (3 screenshots):

6. **Programming Decision**: "Help me think through the pros and cons of learning a new programming language vs. improving my skills in the language I already know."
7. **Career Choice**: "What are the pros and cons of working at a startup versus working at a large corporation as the next step in my career?"
8. **Follow-up Email**: "Draft a polite follow-up email to a hiring manager who hasn't responded to my interview invitation from last week."

### Activity #3 Prompts (2 screenshots):

9. **Schedule Check**: "What does my schedule look like tomorrow?"
10. **Airport Travel**: "What time should I leave for the airport if my flight departs at 5:00 PM and it takes 45 minutes to get there?"

## How to Take Screenshots

### On Linux (gnome-screenshot or similar):
```bash
# Install if needed
sudo apt install gnome-screenshot

# Take interactive screenshot (select area)
gnome-screenshot -a

# Or take window screenshot
gnome-screenshot -w
```

### Using Print Screen Key:
- Press `Print Screen` for full screen
- Press `Alt + Print Screen` for active window

### On macOS:
- Command + Shift + 3 (full screen)
- Command + Shift + 4 (select area)
- Command + Shift + 5 (screenshot tool）

### On Windows:
- Windows Key + Shift + S (snipping tool)
- Print Screen (full screen to clipboard)

## Saving Screenshots

Option 1: Save to `/home/imjonezz/Desktop/AIE9/01_Vibe_Check/screenshots/`

```bash
mkdir -p /home/imjonezz/Desktop/AIE9/01_Vibe_Check/screenshots

# Save with descriptive names like:
# activity1_q1_oop_explanation.png
# activity1_q2_text_summary.png
# etc.
```

Option 2: Save anywhere and note their location for submission.

## Alternative: Document Screenshots

If taking individual screenshots seems tedious:

1. Take a screenshot of the `/home/imjonezz/Desktop/AIE9/01_Vibe_Check/VIBE_CHECK_RESULTS.md` file open in your text editor or terminal
2. This document contains all 10 test responses with details
3. Mention in submission that this contains all vibe check results

## For Google Form Submission

The Google Form asks for screenshots. You can:
- Upload individual screenshots of key interactions
- Upload compiled screenshots showing multiple prompts
- Upload screenshots of the VIBE_CHECK_RESULTS.md file

Choose the approach that best demonstrates your application's functionality while respecting the form's requirements.