# Command Line Interface (CLI)

Moves provides a comprehensive command-line interface built with Typer that offers intuitive commands for managing speakers, controlling presentations, and configuring the system. The CLI is organized into logical subcommands with consistent patterns and helpful feedback.

## Table of Contents

- [Overview](#overview)
- [CLI Structure](#cli-structure)
- [Speaker Management Commands](#speaker-management-commands)
- [Presentation Control Commands](#presentation-control-commands)
- [Settings Management Commands](#settings-management-commands)
- [Command Patterns](#command-patterns)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

## Overview

**Location**: `app.py`

The CLI is built using Typer, providing a modern, user-friendly command-line experience with automatic help generation, type validation, and rich formatting. All commands follow consistent patterns for arguments, options, and output formatting.

```python
# Main CLI application
app = typer.Typer(
    help="moves CLI - AI-powered presentation control system for seamless slide navigation.",
    add_completion=False,
)

# Subcommand applications
speaker_app = typer.Typer(help="Manage speaker profiles, files, and processing")
presentation_app = typer.Typer(help="Live presentation control with voice navigation")
settings_app = typer.Typer(help="Configure system settings (model, API key)")
```

## CLI Structure

### Main Command Groups

```
uv run python app.py
├── speaker          # Speaker profile management
│   ├── add          # Create new speaker profile
│   ├── edit         # Update speaker files
│   ├── list         # Show all speakers
│   ├── show         # Display speaker details
│   ├── process      # Generate AI sections
│   └── delete       # Remove speaker
├── presentation     # Live presentation control
│   └── control      # Start voice navigation
└── settings         # System configuration
    ├── list         # Show current settings
    ├── set          # Update setting value
    └── unset        # Reset to default
```

### Help System

```bash
# Main help
uv run python app.py --help

# Subcommand help
uv run python app.py speaker --help
uv run python app.py speaker add --help

# Command-specific help
uv run python app.py settings set --help
```

## Speaker Management Commands

### `speaker add` - Create Speaker Profile

```bash
uv run python app.py speaker add <NAME> <PRESENTATION_FILE> <TRANSCRIPT_FILE>
```

**Purpose**: Create a new speaker profile with presentation and transcript files.

**Arguments**:

- `NAME`: Speaker's name (used for identification and ID generation)
- `PRESENTATION_FILE`: Path to presentation PDF file
- `TRANSCRIPT_FILE`: Path to transcript PDF file

**Examples**:

```bash
# Basic usage
uv run python app.py speaker add "Dr. Sarah Johnson" ./presentation.pdf ./transcript.pdf

# With spaces in filenames
uv run python app.py speaker add "John Doe" "./My Presentation.pdf" "./My Transcript.pdf"

# Using absolute paths
uv run python app.py speaker add "Prof. Smith" /Users/smith/slides.pdf /Users/smith/notes.pdf
```

**Output**:

```
Speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) added.
    ID -> dr-sarah-johnson-Ax9K2
    Presentation -> /path/to/presentation.pdf
    Transcript -> /path/to/transcript.pdf
```

**Error Handling**:

```bash
# Missing files
uv run python app.py speaker add "Test Speaker" missing.pdf transcript.pdf
# Output: Could not add speaker 'Test Speaker'.
#             Presentation file not found: missing.pdf

# Name conflicts
uv run python app.py speaker add "dr-sarah-johnson-Ax9K2" presentation.pdf transcript.pdf
# Output: Could not add speaker 'dr-sarah-johnson-Ax9K2'.
#             Given name conflicts with existing speaker ID.
```

### `speaker edit` - Update Speaker Files

```bash
uv run python app.py speaker edit <SPEAKER> [OPTIONS]
```

**Purpose**: Update presentation or transcript files for existing speaker.

**Arguments**:

- `SPEAKER`: Speaker name or ID to update

**Options**:

- `--presentation, -p`: New presentation file path
- `--transcript, -t`: New transcript file path

**Examples**:

```bash
# Update presentation only
uv run python app.py speaker edit "Dr. Sarah Johnson" --presentation ./new-presentation.pdf

# Update transcript only
uv run python app.py speaker edit "dr-sarah-johnson-Ax9K2" -t ./updated-transcript.pdf

# Update both files
uv run python app.py speaker edit "Dr. Sarah Johnson" -p ./new-slides.pdf -t ./new-notes.pdf
```

**Output**:

```
Speaker 'Dr. Sarah Johnson' updated.
    Presentation -> /path/to/new-presentation.pdf
    Transcript -> /path/to/updated-transcript.pdf
```

### `speaker list` - Show All Speakers

```bash
uv run python app.py speaker list
```

**Purpose**: Display all registered speakers with their status.

**Output**:

```
Registered Speakers (2)

ID              NAME         STATUS
─────────────── ──────────── ──────────
dr-sarah-johnson Sarah       Ready
john-doe-Xy5Z8  John         Not Ready
```

**Status Meanings**:

- **Ready**: Speaker has been processed and is ready for voice control
- **Not Ready**: Speaker added but not yet processed for AI navigation

### `speaker show` - Display Speaker Details

```bash
uv run python app.py speaker show <SPEAKER>
```

**Purpose**: Show detailed information about a specific speaker.

**Arguments**:

- `SPEAKER`: Speaker name or ID to display

**Examples**:

```bash
uv run python app.py speaker show "Dr. Sarah Johnson"
uv run python app.py speaker show "dr-sarah-johnson-Ax9K2"
```

**Output**:

```
Showing details for speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2)
    ID -> dr-sarah-johnson-Ax9K2
    Name -> Dr. Sarah Johnson
    Status -> Ready
    Presentation -> /Users/sarah/presentation.pdf
    Transcript -> /Users/sarah/transcript.pdf
```

### `speaker process` - Generate AI Sections

```bash
uv run python app.py speaker process [SPEAKERS...] [OPTIONS]
```

**Purpose**: Use AI to generate navigable sections from presentation and transcript.

**Arguments**:

- `SPEAKERS`: Optional list of speaker names/IDs to process

**Options**:

- `--all, -a`: Process all registered speakers

**Examples**:

```bash
# Process specific speaker
uv run python app.py speaker process "Dr. Sarah Johnson"

# Process multiple speakers
uv run python app.py speaker process "Sarah" "John Doe" "Prof. Smith"

# Process all speakers
uv run python app.py speaker process --all
```

**Output**:

```
Processing speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2)...
Speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) processed.
    25 sections created.
```

**Batch Processing Output**:

```
Processing 3 speakers...
3 speakers processed.
    'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) -> 25 sections created.
    'John Doe' (john-doe-Xy5Z8) -> 18 sections created.
    'Prof. Smith' (prof-smith-Ab3C4) -> 32 sections created.
```

### `speaker delete` - Remove Speaker

```bash
uv run python app.py speaker delete <SPEAKER>
```

**Purpose**: Delete speaker profile and all associated data.

**Arguments**:

- `SPEAKER`: Speaker name or ID to delete

**Examples**:

```bash
uv run python app.py speaker delete "Dr. Sarah Johnson"
uv run python app.py speaker delete "dr-sarah-johnson-Ax9K2"
```

**Output**:

```
Speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) deleted.
```

## Presentation Control Commands

### `presentation control` - Start Voice Navigation

```bash
uv run python app.py presentation control <SPEAKER>
```

**Purpose**: Begin live voice-controlled presentation navigation.

**Arguments**:

- `SPEAKER`: Speaker name or ID (must be processed)

**Examples**:

```bash
uv run python app.py presentation control "Dr. Sarah Johnson"
uv run python app.py presentation control "dr-sarah-johnson-Ax9K2"
```

**Output**:

```
Starting presentation control for 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2).
    25 sections loaded
    READY & LISTENING

    Press Ctrl+C to exit.

Keyboard controls:
  → (Right Arrow): Next section
  ← (Left Arrow): Previous section
  Ins (Insert): Pause/Resume automatic navigation

Waiting for 12 words to first trigger, keep speaking...
```

**Real-Time Feedback**:

```
[3/25]
Speech  -> learning fundamentals of machine learning algorithms
Match   -> machine learning fundamentals and basic concepts overview

[Manual Next] 3/25 -> 4/25

[Paused]

[Resumed]
```

**Exit**:

```
Control session ended.
```

## Settings Management Commands

### `settings list` - Show Current Configuration

```bash
uv run python app.py settings list
```

**Purpose**: Display current system settings.

**Output**:

```
Application Settings.
    model (LLM Model) -> gemini/gemini-2.0-flash
    key (API Key) -> your-api-key-here
```

**Unconfigured Output**:

```
Application Settings.
    model (LLM Model) -> Not configured
    key (API Key) -> Not configured
```

### `settings set` - Update Setting Value

```bash
uv run python app.py settings set <KEY> <VALUE>
```

**Purpose**: Configure system settings like LLM model and API key.

**Arguments**:

- `KEY`: Setting name (`model` or `key`)
- `VALUE`: New setting value

**Examples**:

```bash
# Set LLM model
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set model "gpt-4"
uv run python app.py settings set model "claude-3-opus"

# Set API key
uv run python app.py settings set key "your-api-key-here"
uv run python app.py settings set key "sk-1234567890abcdef..."
```

**Output**:

```
Setting 'model' updated.
    New Value -> gemini/gemini-2.0-flash
```

**Error Handling**:

```bash
# Invalid key
uv run python app.py settings set invalid_key "value"
# Output: Error: Invalid setting key 'invalid_key'
#         Valid keys: model, key
```

### `settings unset` - Reset to Default

```bash
uv run python app.py settings unset <KEY>
```

**Purpose**: Reset a setting to its default template value.

**Arguments**:

- `KEY`: Setting name to reset

**Examples**:

```bash
# Reset model to default
uv run python app.py settings unset model

# Reset API key (to null)
uv run python app.py settings unset key
```

**Output**:

```
Setting 'model' reset to default.
    New Value -> gemini/gemini-2.0-flash
```

## Command Patterns

### Consistent Argument Patterns

All commands follow consistent patterns for common operations:

**Speaker Resolution**:

- Commands accept either speaker name or speaker ID
- Case-sensitive matching for names
- Automatic disambiguation for unique matches
- Clear error messages for ambiguous matches

**File Path Handling**:

- Support for relative and absolute paths
- Automatic path resolution and validation
- Clear error messages for missing files
- Proper handling of spaces in filenames

**Output Formatting**:

- Consistent "Direct Summary" format
- Success confirmations with key details
- Error messages with actionable guidance
- Progress indicators for long-running operations

### Option Conventions

```bash
# Short and long options
--presentation, -p    # File path options
--transcript, -t     # File path options
--all, -a           # Boolean flags

# Consistent help text
--help              # Available on all commands
```

### Return Codes

All commands use consistent exit codes:

- **0**: Success
- **1**: Error (file not found, validation failure, processing error)

## Error Handling

### Validation Errors

```bash
# Missing required arguments
uv run python app.py speaker add
# Output: Error: Missing argument 'NAME'

# Invalid file paths
uv run python app.py speaker add "Test" nonexistent.pdf transcript.pdf
# Output: Could not add speaker 'Test'.
#         Presentation file not found: nonexistent.pdf
```

### Configuration Errors

```bash
# LLM not configured
uv run python app.py speaker process "Test Speaker"
# Output: Error: LLM model not configured. Use 'moves settings set model <model>' to configure.

# API key not configured
uv run python app.py speaker process "Test Speaker"
# Output: Error: LLM API key not configured. Use 'moves settings set key <key>' to configure.
```

### Processing Errors

```bash
# Speaker not found
uv run python app.py speaker show "Unknown Speaker"
# Output: Error: No speaker found matching 'Unknown Speaker'.

# Speaker not processed
uv run python app.py presentation control "Unprocessed Speaker"
# Output: Error: Speaker 'Unprocessed Speaker' has not been processed yet.
#         Please run 'moves speaker process' first to generate sections.
```

### Network/API Errors

```bash
# LLM processing failure
uv run python app.py speaker process "Test Speaker"
# Output: Processing error: LLM call failed: Invalid API key
```

## Usage Examples

### Complete Workflow Example

```bash
# 1. Configure system
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-api-key"

# 2. Add speaker
uv run python app.py speaker add "Dr. AI Expert" ./ai-presentation.pdf ./ai-transcript.pdf

# 3. Check speaker status
uv run python app.py speaker list
# Shows "Not Ready"

# 4. Process for AI navigation
uv run python app.py speaker process "Dr. AI Expert"

# 5. Verify processing
uv run python app.py speaker show "Dr. AI Expert"
# Shows "Ready"

# 6. Start presentation
uv run python app.py presentation control "Dr. AI Expert"
# Begin voice-controlled navigation
```

### Batch Operations Example

```bash
# Add multiple speakers
uv run python app.py speaker add "Speaker 1" ./pres1.pdf ./trans1.pdf
uv run python app.py speaker add "Speaker 2" ./pres2.pdf ./trans2.pdf
uv run python app.py speaker add "Speaker 3" ./pres3.pdf ./trans3.pdf

# Process all at once
uv run python app.py speaker process --all

# List all speakers
uv run python app.py speaker list
```

### Configuration Management Example

```bash
# Check current settings
uv run python app.py settings list

# Try different models
uv run python app.py settings set model "gpt-4"
uv run python app.py settings set model "claude-3-opus"

# Reset to defaults
uv run python app.py settings unset model
uv run python app.py settings unset key
```

### Error Recovery Example

```bash
# Update files after initial setup
uv run python app.py speaker edit "Dr. AI Expert" --presentation ./updated-presentation.pdf

# Reprocess after file changes
uv run python app.py speaker process "Dr. AI Expert"

# Clean up when done
uv run python app.py speaker delete "Dr. AI Expert"
```

The CLI provides a powerful, user-friendly interface that makes complex AI-powered presentation control accessible through simple, consistent commands. Its comprehensive help system, error handling, and feedback ensure users can effectively manage speakers, control presentations, and configure the system.
