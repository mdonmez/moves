# Settings Editor

The `SettingsEditor` manages system configuration with a template-based approach that provides default values while allowing user customization. It handles LLM model selection, API key management, and other system settings with automatic validation and fallback mechanisms.

## Table of Contents

- [Overview](#overview)
- [Template-Based Configuration](#template-based-configuration)
- [Configuration Management](#configuration-management)
- [Settings Operations](#settings-operations)
- [Data Persistence](#data-persistence)
- [Validation and Error Handling](#validation-and-error-handling)
- [Usage Examples](#usage-examples)

## Overview

**Location**: `src/core/settings_editor.py`

The SettingsEditor provides a robust configuration management system that combines default templates with user customizations. It ensures system reliability by maintaining fallback defaults while allowing full user control over configurable parameters.

```python
class SettingsEditor:
    template = Path("src/data/settings_template.yaml")
    settings = data_handler.DATA_FOLDER / Path("settings.yaml")

    def __init__(self):
        # Load template defaults
        self.template_data = yaml.load(self.template.read_text()) or {}

        # Load user settings
        user_data = yaml.load(data_handler.read(self.settings)) or {}

        # Merge template + user settings
        self._data = {**self.template_data, **user_data}
```

## Template-Based Configuration

### Template Structure

**Location**: `src/data/settings_template.yaml`

```yaml
# LLM to be used for section generation based on transcript and presentation
# Available providers and models: https://models.litellm.ai/
model: gemini/gemini-2.0-flash

# API key for the LLM provider.
key: null
```

### Template Loading Strategy

```python
def __init__(self):
    try:
        # Load template with error handling
        self.template_data = yaml.load(self.template.read_text(encoding="utf-8")) or {}
    except Exception:
        # Graceful fallback for missing/corrupted template
        self.template_data = {}

    try:
        # Load existing user settings
        user_data = yaml.load(data_handler.read(self.settings)) or {}
    except Exception:
        # Handle missing user settings file
        user_data = {}

    # Template provides defaults, user settings override
    self._data = ({**self.template_data, **user_data}
                  if isinstance(self.template_data, dict) else user_data)
```

**Template Features**:

- **Default Values**: Provides sensible defaults for all settings
- **Documentation**: Includes comments explaining each setting
- **Extensibility**: Easy to add new configuration options
- **Validation**: Serves as schema for valid configuration keys

## Configuration Management

### Settings Hierarchy

The SettingsEditor implements a three-tier configuration hierarchy:

```
1. Template Defaults (lowest priority)
   ↓
2. User Settings (medium priority)
   ↓
3. Runtime Values (highest priority)
```

### Data Merging Logic

```python
# Configuration merge priority:
self._data = {**self.template_data, **user_data}

# Template provides structure and defaults:
template_data = {
    "model": "gemini/gemini-2.0-flash",
    "key": None
}

# User overrides specific values:
user_data = {
    "model": "gpt-4",
    "key": "user-api-key"
}

# Result combines both:
final_data = {
    "model": "gpt-4",           # User override
    "key": "user-api-key"       # User override
}
```

### Automatic Initialization

```python
def __init__(self):
    # Load and merge configurations
    # ...

    try:
        # Automatically save merged configuration
        self._save()
    except Exception:
        # Non-fatal: continue with in-memory config
        pass
```

## Settings Operations

### Setting Values

```python
def set(self, key: str, value: str) -> bool:
    # Validate key exists in template
    if key not in self.template_data:
        return False

    # Update in-memory data
    self._data[key] = value

    try:
        # Persist to disk
        self._save()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to set key '{key}': {e}") from e
```

**Setting Process**:

1. **Validation**: Ensure key exists in template schema
2. **Memory Update**: Update in-memory configuration
3. **Persistence**: Save to disk with error handling
4. **Result**: Return success/failure status

### Unsetting Values (Reset to Default)

```python
def unset(self, key: str) -> bool:
    if key in self.template_data:
        # Reset to template default
        self._data[key] = self.template_data[key]
    else:
        # Remove non-template key
        self._data.pop(key, None)

    try:
        self._save()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to unset key '{key}': {e}") from e
```

**Unset Logic**:

- **Template Keys**: Reset to template default value
- **Non-Template Keys**: Remove entirely from configuration
- **Persistence**: Save changes to disk

### Retrieving Settings

```python
def list(self) -> Settings:
    return Settings(**self._data)
```

The `list()` method returns a strongly-typed `Settings` object that provides structure and validation for configuration data.

## Data Persistence

### File Format and Location

- **Format**: YAML for human readability and editability
- **Location**: `~/.moves/settings.yaml`
- **Encoding**: UTF-8 for international character support

### Save Operation

```python
def _save(self) -> bool:
    try:
        # Ensure data directory exists
        self.settings.parent.mkdir(parents=True, exist_ok=True)

        # Create node based on template structure
        node = copy.deepcopy(self.template_data) if isinstance(self.template_data, dict) else {}

        # Update with current values
        for key in node.keys():
            if key in self._data:
                node[key] = self._data[key]

        # Write to file
        with self.settings.open("w", encoding="utf-8") as f:
            yaml.dump(node, f)
        return True

    except Exception as e:
        raise RuntimeError(f"Failed to save settings: {e}") from e
```

**Save Features**:

- **Directory Creation**: Automatically creates data directories
- **Template Structure**: Preserves template formatting and order
- **Atomic Operations**: File operations are atomic where possible
- **Error Handling**: Comprehensive error reporting

### Example Saved Configuration

```yaml
# ~/.moves/settings.yaml
model: gpt-4
key: sk-1234567890abcdef...
```

## Validation and Error Handling

### Key Validation

```python
def set(self, key: str, value: str) -> bool:
    if key not in self.template_data:
        return False  # Invalid key
    # Proceed with setting
```

The SettingsEditor validates all setting keys against the template schema, preventing invalid configurations.

### Error Recovery

```python
def __init__(self):
    try:
        self.template_data = yaml.load(self.template.read_text()) or {}
    except Exception:
        # Graceful fallback to empty template
        self.template_data = {}

    try:
        user_data = yaml.load(data_handler.read(self.settings)) or {}
    except Exception:
        # Handle missing or corrupted user settings
        user_data = {}
```

**Recovery Strategies**:

- **Template Fallback**: Continue with empty template if loading fails
- **User Settings Fallback**: Use defaults if user settings corrupted
- **Graceful Degradation**: System remains functional with minimal configuration

### Error Propagation

```python
def set(self, key: str, value: str) -> bool:
    try:
        self._save()
        return True
    except Exception as e:
        # Provide context-aware error messages
        raise RuntimeError(f"Failed to set key '{key}': {e}") from e
```

## Usage Examples

### Basic Configuration Operations

```python
# Initialize settings editor
settings_editor = SettingsEditor()

# Check current settings
settings = settings_editor.list()
print(f"Model: {settings.model}")
print(f"API Key: {settings.key}")

# Update LLM model
success = settings_editor.set("model", "gpt-4")
if success:
    print("Model updated successfully")

# Update API key
settings_editor.set("key", "sk-1234567890abcdef...")

# Reset to defaults
settings_editor.unset("model")  # Back to gemini/gemini-2.0-flash
```

### CLI Integration

```python
@settings_app.command("set")
def settings_set(key: str, value: str):
    try:
        settings_editor = SettingsEditor()

        # Validate key
        valid_keys = ["model", "key"]
        if key not in valid_keys:
            typer.echo(f"Error: Invalid setting key '{key}'", err=True)
            typer.echo(f"Valid keys: {', '.join(valid_keys)}", err=True)
            raise typer.Exit(1)

        # Update setting
        success = settings_editor.set(key, value)
        if success:
            typer.echo(f"Setting '{key}' updated.")
            typer.echo(f"    New Value -> {value}")
        else:
            typer.echo(f"Could not update setting '{key}'.", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)
```

### Settings Display

```python
@settings_app.command("list")
def settings_list():
    try:
        settings_editor = SettingsEditor()
        settings = settings_editor.list()

        typer.echo("Application Settings.")

        # Display with formatting
        model_value = settings.model if settings.model else "Not configured"
        typer.echo(f"    model (LLM Model) -> {model_value}")

        if settings.key:
            typer.echo(f"    key (API Key) -> {settings.key}")
        else:
            typer.echo("    key (API Key) -> Not configured")

    except Exception as e:
        typer.echo(f"Error accessing settings: {str(e)}", err=True)
        raise typer.Exit(1)
```

### Configuration Validation

```python
def validate_settings(settings_editor: SettingsEditor) -> tuple[bool, list[str]]:
    """Validate current settings for completeness"""
    settings = settings_editor.list()
    issues = []

    if not settings.model:
        issues.append("LLM model not configured")

    if not settings.key:
        issues.append("API key not configured")

    return len(issues) == 0, issues

# Usage in processing workflow
settings_editor = SettingsEditor()
valid, issues = validate_settings(settings_editor)

if not valid:
    for issue in issues:
        print(f"Configuration issue: {issue}")
    print("Please configure settings before processing speakers.")
```

### Advanced Template Management

```python
# Access template information
settings_editor = SettingsEditor()
template_keys = list(settings_editor.template_data.keys())
print(f"Available settings: {template_keys}")

# Check if setting has default
for key in template_keys:
    default_value = settings_editor.template_data[key]
    current_value = settings_editor._data[key]

    if default_value != current_value:
        print(f"{key}: {default_value} -> {current_value} (customized)")
    else:
        print(f"{key}: {current_value} (default)")
```

### Error Handling Examples

```python
try:
    settings_editor = SettingsEditor()

    # Attempt invalid key
    success = settings_editor.set("invalid_key", "value")
    if not success:
        print("Invalid configuration key")

    # Valid operation
    settings_editor.set("model", "claude-3-opus")

except RuntimeError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

The SettingsEditor provides a robust, user-friendly configuration management system that balances flexibility with reliability. Its template-based approach ensures the system always has sensible defaults while allowing full customization of user preferences.
