# AI Life Coach - Production CLI

A production-ready command-line interface for the AI Life Coach system.

## Features

- **Real User Interaction**: No demo profiles or predefined scenarios - accept real user input
- **Session Persistence**: Save and resume conversations across sessions
- **Multi-Domain Support**: Career, relationships, finance, wellness coaching
- **Progress Tracking**: Automatic session history and progress reports
- **Export Reports**: Generate progress reports in Markdown or JSON format
- **User Management**: Support for multiple user profiles
- **Error Handling**: Robust error handling with graceful shutdown

## Installation

No installation required - the CLI is part of the AI Life Coach system.

Ensure you're in the `ai_life_coach` directory:

```bash
cd ai_life_coach
```

## Usage

### Start Interactive Session

Start a new session with default user:

```bash
python life_coach_cli.py
```

Start a session for specific user:

```bash
python life_coach_cli.py --user john_doe
```

### Export Progress Report

Export a Markdown report:

```bash
python life_coach_cli.py --user john_doe --export markdown
```

Export a JSON report:

```bash
python life_coach_cli.py --user john_doe --export json
```

### Verbose Mode

Enable verbose logging:

```bash
python life_coach_cli.py --verbose
```

### Help

Show help information:

```bash
python life_coach_cli.py --help
```

## Interactive Commands

Once in interactive mode, you can use these commands:

- `exit` or `quit` - End session and save progress
- `help` - Show available commands
- `report` - Generate and display progress report
- `clear` - Clear the screen

## Session Data

All session data is stored in:

```
~/.ai_life_coach/
├── sessions/          # User session files
│   └── {user_id}.json # Individual user sessions
├── reports/           # Exported progress reports
│   └── {user_id}_report_{timestamp}.{format}
└── cli.log           # Application logs
```

## Example Session

```bash
$ python life_coach_cli.py --user alex

============================================================
AI Life Coach
============================================================
User: alex
Session started: 2024-02-08

Commands:
  exit/quit   - End session and save progress
  help        - Show available commands
  report      - Generate progress report
  clear       - Clear screen
============================================================

Welcome! This appears to be your first session.
Feel free to share anything about yourself - your goals, challenges,
or what you'd like help with. I'm here to guide you across all areas of life.

You: Hi, I'd like some help with my career
<Coach responds with personalized advice>
```

## Architecture

The CLI consists of three main components:

1. **SessionManager**: Handles session persistence and state management
2. **ReportGenerator**: Creates progress reports in various formats
3. **AILifeCoachCLI**: Main CLI interface with interactive loop

## Requirements

- Python 3.8+
- All dependencies from the AI Life Coach system
- See `requirements.txt` or `pyproject.toml` for full list

## Testing

Run the test suite:

```bash
python test_cli.py
```

This will verify:
- Session manager functionality
- CLI initialization
- Message handling
- Command processing

## Differences from Demo Script

This production CLI differs from `demo_session.py` in several key ways:

| Feature | Demo Script | Production CLI |
|---------|-------------|----------------|
| User Input | Hardcoded demo profiles | Real user input via stdin |
| Scenarios | Predefined scenarios | Natural conversation flow |
| Formatting | Demo-specific (emojis, narrator) | Clean production output |
| Persistence | Not implemented | Full session persistence |
| Reports | None | Markdown/JSON export |
| Error Handling | Basic | Comprehensive with logging |
| Session Management | None | Multi-user support |

## Logging

Application logs are stored in `~/.ai_life_coach/cli.log`.

Enable verbose logging with the `--verbose` flag for detailed debugging information.

## Support

For issues or questions:
1. Check the logs at `~/.ai_life_coach/cli.log`
2. Run with `--verbose` flag for detailed output
3. Review session data in `~/.ai_life_coach/sessions/`

## License

Part of the AI Life Coach system. See main project license for details.