# moves CLI Requirements Specification

## Overview

The moves CLI is a command-line interface for the moves presentation control system, designed to provide fast, intuitive, and reliable management of speakers, presentations, and system settings. This document serves as the definitive specification for implementing the CLI commands in `app.py`.

## Architecture

The CLI is built using Typer and organized into three main command groups:

- **speaker**: Speaker profile and data management
- **presentation**: Live presentation control
- **settings**: System configuration management

## General Implementation Requirements

### Framework and Dependencies

- Use Typer for all CLI functionality with type safety enabled
- Import required dependencies at the module level
- Implement proper error handling with try-catch blocks at the command level
- Use type annotations for all function parameters and return values

### Error Handling Strategy

- Wrap all commands in try-catch blocks for high-level error management
- Catch and handle errors from underlying modules gracefully
- Provide meaningful, user-friendly error messages
- Maintain consistent error reporting across all commands
- Use appropriate exit codes for different error scenarios

### Input Validation

- Perform type-safe parameter filtering at the CLI level
- Validate required arguments before passing to underlying modules
- Handle optional parameters with proper defaults
- Provide clear feedback for invalid input

### Output Formatting

- Use clean, minimal text formatting without colors or emojis
- Ensure output is informative, balanced, and understandable
- Maintain consistency across all commands
- Avoid excessive formatting while ensuring readability
- Structure output logically with appropriate spacing

### Core Component Integration

The CLI integrates with three main core components:

```python
def speaker_manager_instance():
    from src.core.speaker_manager import SpeakerManager
    return SpeakerManager()

def presentation_controller_instance(sections, start_section, selected_mic=None):
    from src.core.presentation_controller import PresentationController
    return PresentationController(sections, start_section, window_size=12, selected_mic=selected_mic)

def settings_editor_instance():
    from src.core.settings_editor import SettingsEditor
    return SettingsEditor()
```

## Command Hierarchy

### Speaker Management Commands

```
moves speaker add <name> <source-presentation> <source-transcript>
moves speaker edit <speaker> [--presentation PATH] [--transcript PATH]
moves speaker list
moves speaker show <speaker>
moves speaker process <speakers> [--all]
moves speaker delete <speaker>
```

### Presentation Control Commands

```
moves presentation control <speaker>
```

### Settings Management Commands

```
moves settings list
moves settings set <key> <value>
moves settings unset <key>
```

## Detailed Command Specifications

### Speaker Management Commands

The speaker command group manages speaker profiles, their presentation files, and processing operations.

#### speaker add

Creates a new speaker profile with associated presentation and transcript files.

**Signature:**

```python
def speaker_add(
    name: str = typer.Argument(..., help="Speaker's name"),
    source_presentation: Path = typer.Argument(..., help="Path to presentation file"),
    source_transcript: Path = typer.Argument(..., help="Path to transcript file"),
):
```

**Parameters:**

- `name` [str]: The speaker's display name (also used as speaker ID)
- `source_presentation` [Path]: File path to the presentation PDF
- `source_transcript` [Path]: File path to the transcript PDF

**Implementation:**

1. Create speaker manager instance using `speaker_manager_instance()`
2. Validate that both file paths exist and are accessible
3. Call `speaker_manager.add(name, source_presentation, source_transcript)`
4. Handle potential conflicts
5. Display success message with created speaker information

**Error Handling:**

- File not found errors for presentation or transcript paths
- File permission issues
- Invalid file formats

#### speaker edit

Updates an existing speaker's presentation or transcript file.

**Signature:**

```python
def speaker_edit(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
    source_presentation: Optional[Path] = typer.Option(None, "--presentation", "-p", help="New presentation file path"),
    source_transcript: Optional[Path] = typer.Option(None, "--transcript", "-t", help="New transcript file path"),
):
```

**Parameters:**

- `speaker` [str]: Speaker name or ID to update
- `--presentation/-p` [Optional[Path]]: New presentation file path
- `--transcript/-t` [Optional[Path]]: New transcript file path

**Implementation:**

1. Create speaker manager instance
2. Resolve speaker using `speaker_manager.resolve(speaker)` (must return exactly one match)
3. Validate at least one update parameter is provided
4. Validate new file paths exist if specified
5. Call `speaker_manager.edit(resolved_speaker, source_presentation, source_transcript)`
6. Display updated speaker information

**Error Handling:**

- Speaker not found or ambiguous matches
- No update parameters provided
- New file paths not found or inaccessible
- File permission issues

#### speaker list

Lists all registered speakers in the system.

**Signature:**

```python
def speaker_list():
```

**Implementation:**

1. Create speaker manager instance
2. Call `speaker_manager.list()` to get all speakers
3. Format and display speaker information in a consistent table format
4. Show speaker ID, name, presentation file, and transcript file for each speaker
5. Display count of total speakers

**Error Handling:**

- Data access errors
- Corrupted speaker data files

#### speaker show

Displays detailed information for a specific speaker.

**Signature:**

```python
def speaker_show(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
```

**Parameters:**

- `speaker` [str]: Speaker name or ID to display

**Implementation:**

1. Create speaker manager instance
2. Resolve speaker using `speaker_manager.resolve(speaker)` (must return exactly one match)
3. Display comprehensive speaker information including:
   - Speaker ID and name
   - Source presentation file path and status
   - Source transcript file path and status
   - Processing status (if sections.json exists)
   - Last modified dates

**Error Handling:**

- Speaker not found or ambiguous matches
- File access issues when checking file status

#### speaker process

Processes speakers to generate presentation sections using LLM analysis.

**Signature:**

```python
def speaker_process(
    speakers: str = typer.Argument(..., help="Speaker(s) to process"),
    all: bool = typer.Option(False, "--all", "-a", help="Process all speakers"),
):
```

**Parameters:**

- `speakers` [str]: Space-separated list of speaker names/IDs (ignored if --all is used)
- `--all/-a` [bool]: Process all registered speakers

**Implementation:**

1. Create speaker manager and settings editor instances
2. Get LLM configuration from settings (`llm_model` and `llm_api_key`)
3. Validate LLM settings are configured
4. If `--all` flag is used:
   - Get all speakers using `speaker_manager.list()`
5. Otherwise:
   - Split speakers string by spaces
   - Resolve each speaker name/ID using `speaker_manager.resolve()`
   - Collect resolved speakers into list
6. Call `speaker_manager.process(speaker_list)` with resolved speakers
7. Display processing results and status

**Error Handling:**

- Missing LLM configuration in settings
- Speaker resolution failures
- Processing errors from LLM or file operations
- Network connectivity issues for LLM API

#### speaker delete

Removes a speaker and all associated data from the system.

**Signature:**

```python
def speaker_delete(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
```

**Parameters:**

- `speaker` [str]: Speaker name or ID to delete

**Implementation:**

1. Create speaker manager instance
2. Resolve speaker using `speaker_manager.resolve(speaker)` (must return exactly one match)
3. Confirm deletion with user (display speaker details)
4. Call `speaker_manager.delete(resolved_speaker)`
5. Display confirmation of successful deletion

**Error Handling:**

- Speaker not found or ambiguous matches
- File permission issues during deletion
- Directory removal failures

### Presentation Control Commands

The presentation command group manages live presentation control functionality.

#### presentation control

Starts live presentation control for a specific speaker, enabling real-time slide navigation based on speech recognition.

**Signature:**

```python
def presentation_control(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
```

**Parameters:**

- `speaker` [str]: Speaker name or ID for presentation control

**Implementation:**

1. Create speaker manager and settings editor instances
2. Get microphone setting from settings editor using `settings_editor.list().selected_mic`
3. Resolve speaker using `speaker_manager.resolve(speaker)` (must return exactly one match)
4. Check for processed sections data:
   - Use data_handler to locate `sections.json` in speaker's directory
   - File must exist and be readable
5. Load sections data:
   - Use section_producer to convert JSON file to `list[Section]`
   - Validate sections data integrity
6. Determine starting section (typically first section)
7. Create presentation controller instance:
   - Call `presentation_controller_instance(sections, start_section, selected_mic)`
8. Start presentation control loop
9. Handle graceful shutdown and cleanup

**Error Handling:**

- Speaker not found or ambiguous matches
- Missing sections.json file (speaker not processed)
- Corrupted or invalid sections data
- Audio device access issues
- Microphone configuration problems
- Real-time processing errors

**Prerequisites:**

- Speaker must be processed (sections.json exists)
- Microphone must be configured and accessible
- Audio system must be functional

### Settings Management Commands

The settings command group manages system configuration including LLM settings and microphone selection.

#### settings list

Displays all current application settings and available audio input devices.

**Signature:**

```python
def settings_list():
```

**Implementation:**

1. Create settings editor instance
2. Get current settings using `settings_editor.list()` which returns Settings object
3. Query available audio input devices using `sounddevice.query_devices(kind='input')`
4. Display formatted output showing:
   - Current LLM model configuration
   - Current LLM API key status (masked for security)
   - Selected microphone index and name
   - List of all available input devices with indices
5. Highlight currently selected microphone if configured

**Error Handling:**

- Settings file access issues
- Audio system query failures
- Malformed settings data

#### settings set

Updates a specific application setting value.

**Signature:**

```python
def settings_set(
    key: str = typer.Argument(..., help="Setting name to update"),
    value: str = typer.Argument(..., help="New setting value"),
):
```

**Parameters:**

- `key` [str]: Setting key to update (must be valid setting key)
- `value` [str]: New value for the setting

**Implementation:**

1. Create settings editor instance
2. Validate key is a recognized setting key
3. Call `settings_editor.set(key, value)`
4. Check if operation was successful
5. Display confirmation with new setting value
6. For sensitive settings (API keys), mask the value in output

**Error Handling:**

- Invalid setting key
- Setting update failures (file permissions, validation errors)
- Invalid value format for specific settings

**Valid Setting Keys:**

- `llm_model`: LLM model identifier for section generation
- `llm_api_key`: API key for LLM provider
- `selected_mic`: Audio input device index for presentation control

#### settings unset

Resets a setting to its default value from the template.

**Signature:**

```python
def settings_unset(
    key: str = typer.Argument(..., help="Setting name to reset"),
):
```

**Parameters:**

- `key` [str]: Setting key to reset to default value

**Implementation:**

1. Create settings editor instance
2. Call `settings_editor.unset(key)`
3. Check if operation was successful
4. Display confirmation showing the reset value
5. If key was not in template, show that it was removed

**Error Handling:**

- Setting unset failures (file permissions, access issues)
- Invalid key handling

## Implementation Patterns and Examples

### Error Handling Template

```python
@command_app.command("example")
def example_command():
    try:
        # Command implementation
        pass
    except SpecificError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)
```

### Output Formatting Guidelines

- Use `typer.echo()` for all output
- Provide clear, informative messages
- Use consistent formatting for similar operations
- Include relevant details without overwhelming users
- Use appropriate spacing and structure for readability

### Component Integration Pattern

```python
def command_implementation():
    # 1. Create instances
    manager = component_instance()

    # 2. Validate inputs
    if not required_condition:
        raise ValueError("Clear error message")

    # 3. Execute operation
    result = manager.operation(parameters)

    # 4. Format and display result
    typer.echo(f"Operation completed: {result}")
```

This specification provides complete implementation guidance for all CLI commands in alignment with the existing codebase structure and requirements.
