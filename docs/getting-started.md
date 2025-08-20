# Getting Started with moves

This guide will help you set up and start using moves, the AI-powered presentation control system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Initial Configuration](#initial-configuration)
- [Creating Your First Speaker Profile](#creating-your-first-speaker-profile)
- [Processing Presentation Data](#processing-presentation-data)
- [Starting Voice-Controlled Navigation](#starting-voice-controlled-navigation)
- [Basic Usage Workflow](#basic-usage-workflow)
- [Common Issues](#common-issues)

## Prerequisites

Before installing moves, ensure you have:

### System Requirements

- **Python 3.13+**: Required for all functionality
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: At least 2GB free space for models and data
- **Network**: Internet connection for AI processing

### Hardware Requirements

- **Microphone**: Any USB or built-in microphone for speech recognition
- **Audio Drivers**: Properly configured audio input device
- **Presentation Setup**: Display/projector for slide projection

### Software Dependencies

- **uv**: Python package manager (automatically handles dependencies)
- **PDF Reader**: For preparing presentation and transcript files

## Installation

moves uses `uv` for dependency management, which simplifies the installation process.

### Step 1: Clone or Download

```bash
# If using git
git clone <repository-url> moves
cd moves

# Or download and extract the project files
```

### Step 2: Install Dependencies

```bash
# Install all required packages and create virtual environment
uv sync
```

This command will:

- Create a virtual environment
- Install all dependencies from `pyproject.toml`
- Download and setup required ML models

### Step 3: Verify Installation

```bash
# Test the CLI interface
uv run python app.py --help
```

You should see the main help menu with available commands.

## Initial Configuration

### Step 1: Configure LLM Settings

moves requires an LLM (Large Language Model) API for processing presentations:

```bash
# Set your preferred LLM model
uv run python app.py settings set model "gemini/gemini-2.0-flash"

# Set your API key
uv run python app.py settings set key "your-api-key-here"
```

**Supported Models:**

- Gemini: `gemini/gemini-2.0-flash`, `gemini/gemini-pro`
- OpenAI: `gpt-4`, `gpt-3.5-turbo`
- Anthropic: `claude-3-opus`, `claude-3-sonnet`
- See [LiteLLM documentation](https://models.litellm.ai/) for complete list

### Step 2: Verify Configuration

```bash
# Check current settings
uv run python app.py settings list
```

Output should show:

```
Application Settings.
    model (LLM Model) -> gemini/gemini-2.0-flash
    key (API Key) -> your-api-key-here
```

## Creating Your First Speaker Profile

A speaker profile contains your presentation and transcript, which moves uses for intelligent navigation.

### Step 1: Prepare Your Files

You need two PDF files:

1. **Presentation PDF**: Your slide deck exported as PDF
2. **Transcript PDF**: Text of your speech, one section per slide

**Transcript Format Example:**

```
Page 1: Welcome to our presentation on AI technology.

Page 2: Today we'll cover three main topics: machine learning, natural language processing, and computer vision.

Page 3: Let's start with machine learning fundamentals.
```

### Step 2: Add Speaker Profile

```bash
# Add a new speaker with their files
uv run python app.py speaker add "John Doe" ./presentation.pdf ./transcript.pdf
```

**Success Output:**

```
Speaker 'John Doe' (john-doe-Ax9K2) added.
    ID -> john-doe-Ax9K2
    Presentation -> /path/to/presentation.pdf
    Transcript -> /path/to/transcript.pdf
```

### Step 3: List Speakers

```bash
# View all registered speakers
uv run python app.py speaker list
```

**Output:**

```
Registered Speakers (1)

ID              NAME    STATUS
─────────────── ──────  ──────────
john-doe-Ax9K2  John    Not Ready
```

**Status Meanings:**

- **Not Ready**: Speaker added but not processed for AI navigation
- **Ready**: Speaker processed and ready for voice-controlled presentations

## Processing Presentation Data

Before using voice navigation, moves must process your presentation using AI to create intelligent content mappings.

### Step 1: Process Speaker Data

```bash
# Process a specific speaker
uv run python app.py speaker process "John Doe"

# Or process all speakers
uv run python app.py speaker process --all
```

**Processing Steps:**

1. **PDF Extraction**: Extracts text from presentation and transcript
2. **AI Analysis**: Uses LLM to align transcript content with slides
3. **Section Creation**: Generates navigable sections for voice control
4. **Data Storage**: Saves processed data for real-time navigation

**Success Output:**

```
Processing speaker 'John Doe' (john-doe-Ax9K2)...
Speaker 'John Doe' (john-doe-Ax9K2) processed.
    25 sections created.
```

### Step 2: Verify Processing

```bash
# Check speaker status
uv run python app.py speaker show "John Doe"
```

**Output:**

```
Showing details for speaker 'John Doe' (john-doe-Ax9K2)
    ID -> john-doe-Ax9K2
    Name -> John Doe
    Status -> Ready
    Presentation -> /path/to/presentation.pdf
    Transcript -> /path/to/transcript.pdf
```

## Starting Voice-Controlled Navigation

Once your speaker is processed, you can start live voice-controlled presentation navigation.

### Step 1: Prepare Your Environment

1. **Open Presentation**: Launch your slide deck in presentation mode
2. **Position Microphone**: Ensure clear audio input
3. **Test Audio**: Speak normally to verify microphone detection

### Step 2: Start Voice Control

```bash
# Begin voice-controlled navigation
uv run python app.py presentation control "John Doe"
```

**Startup Output:**

```
Starting presentation control for 'John Doe' (john-doe-Ax9K2).
    25 sections loaded
    READY & LISTENING

    Press Ctrl+C to exit.

Keyboard controls:
  → (Right Arrow): Next section
  ← (Left Arrow): Previous section
  Ins (Insert): Pause/Resume automatic navigation

Waiting for 12 words to first trigger, keep speaking...
```

### Step 3: Begin Presenting

1. **Start Speaking**: Begin your presentation normally
2. **Automatic Navigation**: moves will navigate slides based on your speech
3. **Manual Override**: Use keyboard controls when needed
4. **Pause/Resume**: Use Insert key to pause automatic navigation

**Navigation Output:**

```
[3/25]
Speech  -> learning fundamentals of machine learning algorithms
Match   -> machine learning fundamentals and basic concepts overview
```

## Basic Usage Workflow

Here's the typical workflow for using moves:

### 1. Preparation Phase

```bash
# Configure system
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-api-key"

# Add speaker
uv run python app.py speaker add "Speaker Name" presentation.pdf transcript.pdf

# Process for AI navigation
uv run python app.py speaker process "Speaker Name"
```

### 2. Presentation Phase

```bash
# Start voice control
uv run python app.py presentation control "Speaker Name"

# Present normally - system handles navigation automatically
# Use keyboard controls for manual override when needed
```

### 3. Management Phase

```bash
# Update speaker files
uv run python app.py speaker edit "Speaker Name" --presentation new-presentation.pdf

# Re-process after changes
uv run python app.py speaker process "Speaker Name"

# Clean up when done
uv run python app.py speaker delete "Speaker Name"
```

## Common Issues

### Audio Issues

**Problem**: Microphone not detected
**Solution**:

- Check system audio settings
- Ensure microphone permissions are granted
- Test with other audio applications first

**Problem**: Poor speech recognition
**Solution**:

- Speak clearly and at normal volume
- Reduce background noise
- Position microphone 6-12 inches from mouth

### Processing Issues

**Problem**: LLM processing fails
**Solution**:

- Verify API key is correct and has sufficient credits
- Check network connection
- Try a different model if current one is unavailable

**Problem**: PDF extraction errors
**Solution**:

- Ensure PDFs are text-based (not scanned images)
- Try re-exporting PDFs from original source
- Check file permissions and paths

### Navigation Issues

**Problem**: Slides navigate incorrectly
**Solution**:

- Ensure transcript closely matches your actual speech
- Re-process speaker data after transcript improvements
- Use manual keyboard controls as backup

**Problem**: Navigation is too sensitive/slow
**Solution**:

- Adjust speaking pace and clarity
- Consider editing transcript for better matching
- Use pause feature during transitions

## Next Steps

- **Learn More**: Read the [Architecture Overview](./architecture.md) to understand how moves works
- **Customize**: Check [Configuration](./configuration.md) for advanced settings
- **Troubleshoot**: See [Troubleshooting Guide](./troubleshooting.md) for detailed solutions
- **Contribute**: Read [Development Guide](./development.md) to extend moves functionality

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](./troubleshooting.md)
2. Review logs in `~/.moves/logs/` for error details
3. Verify all prerequisites and dependencies are properly installed
4. Test with a simple presentation first before complex ones
