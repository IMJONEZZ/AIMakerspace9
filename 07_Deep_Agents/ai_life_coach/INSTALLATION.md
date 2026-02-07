# Installation and Setup Guide

🚀 **Get AI Life Coach Running in Minutes** - Step-by-Step Installation

---

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+, iOS 13+, Android 8+
- **Python**: 3.10 or higher
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 1GB free space
- **Internet**: Broadband connection required for AI features

### Recommended Setup
- **Memory**: 8GB+ RAM for optimal performance
- **Storage**: 2GB+ for full feature set
- **Internet**: Stable broadband connection
- **Display**: 720p+ resolution for best interface

---

## 🛠️ Installation Steps

### Step 1: Download the Application

#### Option A: Download from Website
1. Visit [https://ailifecoach.ai/download](https://ailifecoach.ai/download)
2. Select your operating system
3. Download the installer
4. Verify download completed fully

#### Option B: Package Manager
```bash
# Using pip (recommended)
pip install ai-life-coach

# Using conda
conda install -c ai-life-coach ai-life-coach

# Using Homebrew (macOS)
brew install ai-life-coach
```

### Step 2: Install the Application

#### Windows Installation
```bash
1. Run the downloaded installer (ai-life-coach-setup.exe)
2. Follow the installation wizard
3. Choose installation location (default recommended)
4. Select "Add to PATH" option during install
5. Complete installation and launch app
```

#### macOS Installation
```bash
1. Open the downloaded DMG file
2. Drag AI Life Coach to Applications folder
3. Right-click app and select "Open" (bypass Gatekeeper)
4. Follow any additional security prompts
5. Launch from Applications folder
```

#### Linux Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ai-life-coach

# Extract and run (alternative)
tar -xzf ai-life-coach-linux.tar.gz
cd ai-life-coach
./install.sh
```

### Step 3: Set Up Python Environment

#### Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv ai_life_coach_env

# Activate environment
# On Unix/macOS:
source ai_life_coach_env/bin/activate
# On Windows:
ai_life_coach_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Verify Python Setup
```bash
# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list

# Test installation
python -c "import ai_life_coach; print('Installation successful!')"
```

### Step 4: Configure Environment Variables

#### Create Environment File
```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file
nano .env  # or use your preferred editor
```

#### Environment Configuration
```env
# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Local Model (Optional)
LOCAL_MODEL_ENDPOINT=http://localhost:8080/v1
MODEL_NAME=glm-4.7

# Storage Configuration
WORKSPACE_DIR=./workspace
MEMORY_BACKEND=filesystem

# User Settings
DEFAULT_USER_ID=user123
DEBUG_MODE=false
LOG_LEVEL=INFO

# Security
ENCRYPTION_KEY=your_encryption_key_here
BACKUP_ENABLED=true
```

### Step 5: Initialize the Application

#### First-Time Setup
```bash
# Run initialization
python src/main.py --init

# This will:
# - Create workspace directories
# - Initialize memory store
# - Set up user profile
# - Create default settings
# - Generate encryption keys
```

#### Test Installation
```bash
# Run test to verify everything works
python src/main.py --test

# Expected output:
# ✓ Environment variables configured
# ✓ Memory store initialized
# ✓ Workspace directories created
# ✓ AI models accessible
# ✓ Database connection successful
# ✓ All systems ready
```

---

## 🔧 Configuration Options

### AI Model Selection

#### OpenAI Models
```env
OPENAI_API_KEY=sk-...
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4
```

#### Anthropic Models
```env
ANTHROPIC_API_KEY=sk-ant-...
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-3-sonnet
```

#### Local Models
```env
LOCAL_MODEL_ENDPOINT=http://localhost:8080/v1
MODEL_PROVIDER=local
MODEL_NAME=glm-4.7
```

#### Hybrid Configuration
```env
# Use different models for different tasks
PRIMARY_MODEL=openai:gpt-4
SECONDARY_MODEL=anthropic:claude-3-sonnet
LOCAL_MODEL_ENABLED=true
```

### Storage Configuration

#### Filesystem Storage (Default)
```env
STORAGE_BACKEND=filesystem
WORKSPACE_DIR=./workspace
BACKUP_ENABLED=true
BACKUP_INTERVAL=daily
```

#### Cloud Storage
```env
STORAGE_BACKEND=cloud
CLOUD_PROVIDER=aws
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
AWS_BUCKET=ai-life-coach-data
```

#### Database Storage
```env
STORAGE_BACKEND=database
DATABASE_URL=postgresql://user:pass@localhost/ailifecoach
```

---

## 🚀 Quick Start

### Launch the Application

#### Desktop Application
```bash
# Method 1: From command line
python src/main.py

# Method 2: Using installed executable
ai-life-coach

# Method 3: From application menu
# Find AI Life Coach in your applications
```

#### Web Interface
```bash
# Start web server
python src/main.py --web

# Access at http://localhost:8080
```

#### Command Line Interface
```bash
# Interactive mode
ai-life-coach --interactive

# Single query
ai-life-coach --query "How can I improve my work-life balance?"

# Help
ai-life-coach --help
```

### Your First Session

#### Initial Assessment
```bash
# The app will guide you through:
1. Welcome and introduction
2. Comprehensive life assessment (20-30 minutes)
3. Values clarification
4. Goal identification
5. Personalized plan creation
```

#### Example First Interaction
```python
from src.main import create_life_coach

# Create coach instance
coach = create_life_coach()

# Start your first session
result = coach.invoke({
    "messages": [{
        "role": "user",
        "content": "I'm ready to start improving my life. Can you guide me through the process?"
    }]
})

print(result["messages"][-1].content)
```

---

## 🛠️ Troubleshooting Installation

### Common Issues

#### Python Version Errors
```bash
# Error: Python 3.10+ required
# Solution: Install correct Python version

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv

# On macOS with Homebrew:
brew install python@3.11

# On Windows:
# Download from python.org and install
```

#### Permission Errors
```bash
# Error: Permission denied
# Solution: Use appropriate permissions

# On Unix/macOS:
sudo chown -R $USER ~/.ai-life-coach
chmod +x ai-life-coach

# On Windows:
# Run Command Prompt as Administrator
```

#### Dependency Installation Errors
```bash
# Error: Failed to install dependencies
# Solution: Update package manager and try alternatives

# Update pip
pip install --upgrade pip

# Use different package index
pip install -r requirements.txt -i https://pypi.org/simple/

# Install dependencies individually
pip install langchain langgraph openai anthropic
```

#### Model Connection Errors
```bash
# Error: Cannot connect to AI model
# Solution: Check API keys and network

# Verify API key
python -c "import openai; print(openai.api_key)"

# Test network connection
curl https://api.openai.com/v1/models

# Use local model as fallback
export MODEL_PROVIDER=local
```

#### Memory/Storage Errors
```bash
# Error: Cannot initialize memory store
# Solution: Check disk space and permissions

# Check available space
df -h

# Clear workspace and reinitialize
rm -rf ./workspace
python src/main.py --init
```

### Getting Help

#### Diagnostic Information
```bash
# Generate diagnostic report
python src/main.py --diagnostic

# This will output:
# - System information
# - Configuration details
# - Network connectivity
# - Dependency versions
# - Error logs
```

#### Support Resources
```text
📧 Email: support@ailifecoach.ai
💬 Live Chat: Available in app during business hours
🌐 Help Center: help.ailifecoach.ai
🐛 Bug Reports: github.com/ai-life-coach/issues
```

---

## 📱 Mobile Installation

### iOS Installation

#### App Store Installation
1. Open App Store on your iPhone/iPad
2. Search "AI Life Coach"
3. Tap "Get" to download
4. Wait for installation to complete
5. Open app and follow setup

#### Alternative Installation
```bash
# TestFlight (Beta)
1. Join TestFlight program
2. Install TestFlight app
3. Accept AI Life Coach invitation
4. Install beta version
```

### Android Installation

#### Google Play Store
1. Open Google Play Store
2. Search "AI Life Coach"
3. Tap "Install"
4. Accept permissions
5. Open app when installed

#### APK Installation
```bash
# Enable unknown sources
Settings > Security > Unknown Sources > Enable

# Download APK
wget https://ailifecoach.ai/latest.apk

# Install APK
adb install ai-life-coach.apk
# or tap on file in file manager
```

---

## 🔐 Security Setup

### Encryption Configuration

#### Generate Encryption Key
```bash
# Generate strong encryption key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env file
ENCRYPTION_KEY=your_generated_key_here
```

#### Configure Data Protection
```env
# Data encryption settings
DATA_ENCRYPTION_ENABLED=true
BACKUP_ENCRYPTION=true
SECURE_DELETE=true

# Access control
TWO_FACTOR_AUTH=true
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=3
```

### Privacy Settings

#### Data Sharing Preferences
```env
# Privacy controls
TELEMETRY_ENABLED=false
ANALYTICS_SHARING=false
CRASH_REPORTING=true
AUTOMATIC_BACKUP=true
```

---

## ✅ Verification Checklist

### Post-Installation Verification

#### Basic Functionality
- [ ] Application launches without errors
- [ ] Can access AI models (test with simple query)
- [ ] Memory store initializes correctly
- [ ] Workspace directories created
- [ ] Configuration file loads properly

#### Advanced Features
- [ ] Multi-agent coordination working
- [ ] Goal planning system functional
- [ ] Progress tracking operational
- [ ] Cross-device synchronization active
- [ ] Backup and restore working

#### Security and Privacy
- [ ] Data encryption enabled
- [ ] API keys stored securely
- [ ] Network connections encrypted
- [ ] Local file permissions correct
- [ ] Backup encryption functional

### Performance Testing

#### Response Time Verification
```bash
# Test AI response times
python src/performance_test.py

# Expected results:
# - Simple queries: < 5 seconds
# - Complex queries: < 30 seconds
# - Multi-agent coordination: < 60 seconds
```

#### Resource Usage
```bash
# Monitor resource usage
htop  # or Task Manager on Windows

# Acceptable ranges:
# - Memory usage: < 1GB normal, < 2GB peak
# - CPU usage: < 50% normal, < 80% peak
# - Disk usage: Stable, no uncontrolled growth
```

---

## 🎉 You're Ready!

### What to Expect Next

1. **Personalized Assessment**: Complete your comprehensive life evaluation
2. **Goal Setting**: Work with AI specialists to identify priorities  
3. **Action Planning**: Create structured 90-day plans
4. **Daily Engagement**: Start with check-ins and progress tracking
5. **Continuous Improvement**: Adapt and optimize based on results

### Success Tips

- **Be Consistent**: Daily check-ins create momentum
- **Be Honest**: Share real feelings and challenges
- **Be Patient**: Lasting change takes time
- **Be Open**: Try new approaches and strategies
- **Celebrate**: Acknowledge progress and wins

---

**Welcome to AI Life Coach! Your transformation journey starts now.** 🚀

*Need help? Check our comprehensive [Troubleshooting Guide](TROUBLESHOOTING.md) or contact support at support@ailifecoach.ai*