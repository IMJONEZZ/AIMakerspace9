# AI Life Coach TUI - User Guide

## Overview

The **AI Life Coach TUI** (Terminal User Interface) is a feature-rich terminal interface for the AI Life Coach system, featuring the beautiful **Gruvbox Dark Hard** color theme. It provides an enhanced user experience with styled messages, dashboards, animations, and rich visual feedback while maintaining 100% compatibility with the original CLI functionality.

## Theme: Gruvbox Dark Hard

The TUI uses the official [Gruvbox](https://github.com/gruvbox-community/gruvbox) Dark Hard color palette for a retro groove aesthetic that's easy on the eyes:

### Color Palette

**Backgrounds:**
- `#1d2021` - Main background (darkest)
- `#282828` - Standard dark
- `#3c3836` - Panels, borders
- `#504945` - Secondary elements
- `#665c54` - Tertiary elements

**Foregrounds:**
- `#fbf1c7` - Brightest text (titles)
- `#ebdbb2` - Main body text
- `#d5c4a1` - Secondary text
- `#bdae93` - Dimmed text
- `#a89984` - Metadata, timestamps

**Accent Colors:**
- Red: `#fb4934`
- Green: `#b8bb26` (user messages, success)
- Yellow: `#fabd2f`
- Blue: `#83a598` (coach responses)
- Purple: `#d3869b`
- Aqua: `#8ec07c` (progress, export)
- Orange: `#fe8019`

## Installation

The TUI version requires the **Rich** library for terminal UI rendering:

```bash
# Rich is likely already installed in your virtual environment
python3 -c "import rich; print('Rich installed!')"

# If not, install it:
python3 -m pip install rich
```

## Quick Start

### Basic Usage

```bash
# Start a new interactive session
python3 life_coach_tui.py

# Resume a specific user's session
python3 life_coach_tui.py --user john

# Export progress report
python3 life_coach_tui.py --export markdown
python3 life_coach_tui.py --export json

# Enable verbose logging
python3 life_coach_tui.py --verbose
```

### Interactive Commands

Once in the TUI, you can use these commands:

| Command | Shortcut | Description |
|---------|----------|-------------|
| `/help` or `/?` | `?` | Show available commands |
| `/report` or `/r` | `r` | Generate and display progress report |
| `/export [format]` | `e` | Export report (markdown/json) |
| `/clear` or `/c` | `c` | Clear the screen |
| `/dashboard` or `/d` | `d` | Show session statistics dashboard |
| `/exit` or `/quit` | `q` | End session and save progress |

## Features

### 1. 🎨 Gruvbox Dark Hard Theme

Consistent, beautiful color scheme throughout:
- User messages: **Green** (right-aligned)
- Coach responses: **Blue** (left-aligned)
- Panels and borders: Muted grays
- Success indicators: **Green**
- Errors: **Red**

### 2. 💬 Styled Chat Interface

- Clear visual separation between user and coach messages
- Timestamps in dimmed gray for easy tracking
- Right-aligned user messages for intuitive reading flow
- Left-aligned coach responses
- Smooth typing indicator animation

### 3. 📊 Session Dashboard

Real-time statistics display:
- Total exchange count
- Session duration
- Mood tracker with emoji-based focus areas (Personal Growth, Career, Wellness, Relationships)
- Last save time indicator

### 4. ✨ Animated Welcome Screen

- App branding with Gruvbox colors
- Personalized greeting (Welcome back for returning users)
- Current date and time display
- Quick tips for first-time users
- Smooth fade-in effect

### 5. 📝 Enhanced Report Viewer

- Full Markdown rendering with syntax highlighting
- Gruvbox colors for code blocks and headers
- Clean, readable layout
- Export to Markdown or JSON formats

### 6. 📤 Progress Bar for Exports

Animated progress bar when exporting reports:
- Spinner animation
- Percentage indicator
- Time elapsed display
- Visual confirmation on completion

### 7. 🎯 Command Palette

Styled help screen showing:
- All available commands
- Keyboard shortcuts
- Shortcuts for quick reference
- Color-coded command types

### 8. 📡 Status Bar

Bottom status bar showing:
- Connection status (green dot = connected)
- Auto-save indicator
- Always visible for system state awareness

## Usage Examples

### Starting a Conversation

```bash
$ python3 life_coach_tui.py

🧠 AI Life Coach
━━━━━━━━━━━━━━━

Welcome to your personal growth journey!

📅 Monday, February 8, 2026  •  🕐 04:45 PM

Quick Tips:
• Type your message to chat with the coach
• Use /help for commands
• All conversations are saved automatically

● Connected  │  💾 Auto-save enabled

You: I'm feeling stuck in my career. What should I do?
```

### Viewing Session Statistics

```bash
You: /dashboard

┏━━━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━━━┓
│ Session Statistics │  │ Current Focus Areas │
├────────────────────┤  ├────────────────────┤
│ Metric             │  │ Area              │
│ Total Exchanges    │5 │ 🎯 Personal Growth│
│ Session Duration   │  │ 💼 Career Dev     │
│ Session Started    │  │ 💪 Wellness       │
└────────────────────┘  │ 🤝 Relationships  │
                        └────────────────────┘

💾 Last saved: 04:45:23
```

### Generating Reports

```bash
You: /report

┏━━━━━━━━━━━━━━━━━━━━━┓
│ Progress Report      │
├─────────────────────┤
│ # AI Life Coach...  │
│ **User ID:** john   │
│ ...                 │
└─────────────────────┘

Export report? [y/n]: y

⠋ Exporting report... ████████████ 100% 1.2s

✅ Report exported successfully!
```

## Architecture

### Key Components

**GruvboxColors Class**
- Centralized color palette management
- Official Gruvbox Dark Hard hex codes
- Easy theme customization

**TUIRenderer Class**
- Handles all visual presentation
- Wraps Rich library functionality
- Provides styled UI components:
  - `print_welcome()` - Welcome screen
  - `print_message()` - Chat messages
  - `print_dashboard()` - Statistics panel
  - `print_help()` - Command palette
  - `print_report()` - Report viewer
  - `print_export_progress()` - Progress bar

**AILifeCoachTUI Class**
- Main TUI application logic
- Reuses `SessionManager` and `ReportGenerator` from original CLI
- Interactive loop with command handling
- Zero breaking changes to core functionality

### File Structure

```
ai_life_coach/
├── life_coach_cli.py      # Original CLI (unchanged)
├── life_coach_tui.py      # New TUI version
└── TUI_README.md          # This documentation
```

## Compatibility

### Zero Breaking Changes

✅ **Original CLI remains unchanged** - `life_coach_cli.py` is not modified
✅ **All features work identically** - Session persistence, reports, export
✅ **Same session files** - Both versions use the same storage format
✅ **Seamless switching** - Can switch between CLI and TUI anytime

### Cross-Platform Support

✅ **Linux** - Full support
✅ **macOS** - Full support
✅ **Windows** - Supported with modern terminal (Windows Terminal recommended)

### Performance

- Minimal overhead compared to original CLI
- Rich rendering is optimized for fast terminals
- No significant slowdown in message processing

## Advanced Usage

### Customizing Colors

To customize the theme, edit the `GruvboxColors` class in `life_coach_tui.py`:

```python
class GruvboxColors:
    # Change background color
    BG_HARD = "#1d2021"  # Modify this hex code

    # Change accent colors
    BRIGHT_GREEN = "#b8bb26"
    BRIGHT_BLUE = "#83a598"
```

### Session Persistence

Sessions are automatically saved to:
- `~/.ai_life_coach/sessions/{user_id}.json`

Reports are exported to:
- `~/.ai_life_coach/reports/{user_id}_report_{timestamp}.{format}`

### Logging

TUI-specific logs are saved to:
- `~/.ai_life_coach/tui.log`

Enable verbose logging with `--verbose` flag:
```bash
python3 life_coach_tui.py --verbose
```

## Troubleshooting

### Rich Not Installed

```bash
Error: No module named 'rich'
```

Solution:
```bash
python3 -m pip install rich
```

### Terminal Not Supported

The TUI requires a terminal that supports ANSI colors and styling. Most modern terminals work:
- Linux: gnome-terminal, kitty, alacritty
- macOS: Terminal.app, iTerm2
- Windows: Windows Terminal (recommended), not CMD

### Colors Not Displaying Correctly

Ensure your terminal supports 256 colors or true color (24-bit). Most modern terminals do.

### Performance Issues

If the TUI feels slow:
1. Check terminal size (too small can cause issues)
2. Reduce history length in session
3. Disable animations (edit `print_export_progress` method)

## Migration from Original CLI

Migrating from the original CLI to TUI is seamless:

1. **Your sessions are preserved** - Same storage format
2. **No data loss** - All conversations available in TUI
3. **Same functionality** - All commands work the same

Simply switch from:
```bash
python3 life_coach_cli.py
```

To:
```bash
python3 life_coach_tui.py
```

## Comparison: CLI vs TUI

| Feature | Original CLI | TUI Version |
|---------|--------------|-------------|
| Basic chat | ✅ | ✅ (styled) |
| Session persistence | ✅ | ✅ |
| Report generation | ✅ | ✅ (enhanced) |
| Export functionality | ✅ | ✅ (with progress bar) |
| Color support | ❌ Plain text | ✅ Gruvbox theme |
| Dashboard/Statistics | ❌ | ✅ |
| Help system | ✅ Basic | ✅ Enhanced with shortcuts |
| Animations | ❌ | ✅ (typing, progress) |
| Visual feedback | Basic text | Rich panels and indicators |

## Future Enhancements

Potential improvements for future versions:

- [ ] Interactive menu navigation (arrow keys)
- [ ] Session history browser
- [ ] Goal setting visualizer
- [ ] Mood tracking with charts (using rich.table)
- [ ] Syntax highlighting for code blocks in responses
- [ ] Multi-language support
- [ ] Custom theme selection

## Contributing

Contributions welcome! Areas for improvement:

1. Additional color themes (Solarized, Nord, etc.)
2. More dashboard widgets
3. Enhanced report templates
4. Better error handling and recovery

## License

Same as the main AI Life Coach project.

## Support

For issues or questions:
- Check logs: `~/.ai_life_coach/tui.log`
- Report bugs in the main project issue tracker
- Mention "TUI" in bug reports for visibility

---

**Enjoy your AI Life Coach experience with the beautiful Gruvbox Dark Hard theme! 🎨✨**