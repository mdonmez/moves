# Configuration

Moves uses a template-based configuration system that provides sensible defaults while allowing full customization. Configuration covers LLM settings, system parameters, and runtime behavior.

## Table of Contents

- [Overview](#overview)
- [Configuration Files](#configuration-files)
- [Settings Template](#settings-template)
- [LLM Configuration](#llm-configuration)
- [System Parameters](#system-parameters)
- [Runtime Configuration](#runtime-configuration)
- [Environment Variables](#environment-variables)
- [Configuration Management](#configuration-management)

## Overview

Moves configuration follows a hierarchical approach:

1. **Template Defaults**: Base configuration with sensible defaults
2. **User Settings**: User overrides stored in `~/.moves/settings.yaml`
3. **Runtime Parameters**: Command-line arguments and code-level configuration

This layered approach ensures the system always has working defaults while allowing complete customization.

## Configuration Files

### Settings Template

**Location**: `src/data/settings_template.yaml`

```yaml
# LLM to be used for section generation based on transcript and presentation
# Available providers and models: https://models.litellm.ai/
model: gemini/gemini-2.0-flash

# API key for the LLM provider.
key: null
```

**Purpose**:

- Defines available configuration options
- Provides default values for all settings
- Serves as documentation for configuration options
- Used for validation and schema enforcement

### User Settings File

**Location**: `~/.moves/settings.yaml`

```yaml
model: gpt-4
key: sk-1234567890abcdef...
```

**Characteristics**:

- Automatically created when settings are modified
- Only contains user-customized values
- Merged with template defaults at runtime
- Human-readable YAML format for easy editing

### Data Directory Structure

```
~/.moves/                           # User data directory
├── settings.yaml                   # User configuration overrides
├── logs/                          # Application logs
│   ├── speaker_manager.log
│   ├── presentation_controller.log
│   └── ...
└── speakers/                      # Speaker data
    └── {speaker-id}/              # Individual speaker directory
        ├── speaker.json           # Speaker metadata
        ├── presentation.pdf       # Local presentation copy
        ├── transcript.pdf         # Local transcript copy
        └── sections.json          # Generated navigation sections
```

## Settings Template

### Template Structure and Documentation

```yaml
# LLM Model Configuration
# Specifies which Large Language Model to use for processing
# Format: provider/model-name
# Examples: gemini/gemini-2.0-flash, openai/gpt-4, anthropic/claude-3-opus
# Full list: https://models.litellm.ai/
model: gemini/gemini-2.0-flash

# API Key Configuration
# API key for the specified LLM provider
# Set to null by default (must be configured by user)
# Obtain from your LLM provider's dashboard
key: null
```

### Configuration Validation

The template serves as a schema for validation:

```python
# Only template keys are allowed
valid_keys = ["model", "key"]

def set(self, key: str, value: str) -> bool:
    if key not in self.template_data:
        return False  # Invalid key rejected

    self._data[key] = value
    self._save()
    return True
```

**Validation Benefits**:

- Prevents typos in configuration keys
- Ensures consistent configuration structure
- Provides clear error messages for invalid settings
- Maintains compatibility across system updates

## LLM Configuration

### Supported Models and Providers

#### Gemini (Google)

```yaml
# Recommended models
model: gemini/gemini-2.0-flash    # Fast, cost-effective (default)
model: gemini/gemini-pro          # Higher quality
model: gemini/gemini-1.5-pro      # Advanced capabilities
```

**API Key**: Obtain from [Google AI Studio](https://aistudio.google.com/)

#### OpenAI

```yaml
model: gpt-4                      # High quality, higher cost
model: gpt-4-turbo               # Latest GPT-4 variant
model: gpt-3.5-turbo             # Cost-effective option
```

**API Key**: Obtain from [OpenAI Dashboard](https://platform.openai.com/)

#### Anthropic

```yaml
model: claude-3-opus             # Highest quality
model: claude-3-sonnet           # Balanced performance
model: claude-3-haiku            # Fastest, most economical
```

**API Key**: Obtain from [Anthropic Console](https://console.anthropic.com/)

#### Other Providers

Moves supports any LiteLLM-compatible provider:

```yaml
# Cohere
model: cohere/command-r-plus

# Mistral AI
model: mistral/mistral-large

# Azure OpenAI
model: azure/gpt-4

# Hugging Face
model: huggingface/microsoft/DialoGPT-medium
```

### Model Selection Criteria

**For Development/Testing**:

```yaml
model: gemini/gemini-2.0-flash # Fast, free tier available
```

**For Production Use**:

```yaml
model: gpt-4 # Consistent, high-quality results
```

**For Budget-Conscious Use**:

```yaml
model: gpt-3.5-turbo # Good quality, lower cost
```

**For Privacy-Focused Use**:

```yaml
# Consider local models via Ollama integration
model: ollama/llama2 # Self-hosted option
```

## System Parameters

### Audio Processing Configuration

These parameters are currently hardcoded but can be modified in the source:

```python
# In PresentationController.__init__()
self.frame_duration = 0.1          # 100ms frames
self.sample_rate = 16000           # 16kHz audio sampling
self.window_size = window_size     # 12 words by default
```

**Tuning Guidelines**:

- **frame_duration**: Lower values = more responsive, higher CPU usage
- **sample_rate**: 16kHz optimal for speech recognition
- **window_size**: Larger values = more context, slower response

### Speech Recognition Configuration

```python
# In PresentationController.__init__()
self.recognizer = OnlineRecognizer.from_transducer(
    tokens="src/core/components/ml_models/stt/tokens.txt",
    encoder="src/core/components/ml_models/stt/encoder.int8.onnx",
    decoder="src/core/components/ml_models/stt/decoder.int8.onnx",
    joiner="src/core/components/ml_models/stt/joiner.int8.onnx",
    num_threads=8,                 # Adjust based on CPU cores
    decoding_method="greedy_search"
)
```

### Similarity Calculation Configuration

```python
# In SimilarityCalculator.__init__()
self.semantic_weight = 0.4         # 40% semantic similarity
self.phonetic_weight = 0.6         # 60% phonetic similarity
```

**Weight Adjustment**:

- Increase `semantic_weight` for better meaning-based matching
- Increase `phonetic_weight` for better speech recognition error tolerance

## Runtime Configuration

### Presentation Controller Parameters

```python
def __init__(
    self,
    sections: list[Section],
    start_section: Section,
    window_size: int = 12,         # Configurable speech window
):
```

**Window Size Guidelines**:

- **8-10**: Faster response, less context
- **12-15**: Balanced (recommended)
- **16-20**: More context, slower response

### Chunk Producer Configuration

```python
def generate_chunks(sections: list[Section], window_size: int = 12):
    # Window size should match PresentationController
```

### Similarity Calculator Configuration

```python
def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
    # Weights must sum to 1.0
```

## Environment Variables

### Development Environment

```bash
# Optional: Override default data directory
export MOVES_DATA_DIR="/custom/path/to/moves/data"

# Optional: Debug logging
export MOVES_DEBUG=1

# Optional: Custom model cache location
export MOVES_MODEL_CACHE="/path/to/model/cache"
```

### Production Environment

```bash
# Recommended: Set data directory
export MOVES_DATA_DIR="/var/lib/moves"

# Recommended: Log level
export MOVES_LOG_LEVEL="INFO"

# Security: Restrict file permissions
umask 077
```

## Configuration Management

### CLI Configuration Commands

```bash
# View current settings
uv run python app.py settings list

# Update LLM model
uv run python app.py settings set model "gpt-4"

# Update API key
uv run python app.py settings set key "your-api-key"

# Reset to defaults
uv run python app.py settings unset model
uv run python app.py settings unset key
```

### Programmatic Configuration

```python
from src.core.settings_editor import SettingsEditor

# Initialize settings manager
settings_editor = SettingsEditor()

# Get current settings
settings = settings_editor.list()
print(f"Current model: {settings.model}")
print(f"API key configured: {'Yes' if settings.key else 'No'}")

# Update settings
settings_editor.set("model", "claude-3-opus")
settings_editor.set("key", "your-api-key")

# Reset settings
settings_editor.unset("model")  # Back to template default
```

### Configuration Validation

```python
def validate_configuration(settings_editor: SettingsEditor) -> tuple[bool, list[str]]:
    """Validate current configuration for completeness"""
    settings = settings_editor.list()
    issues = []

    # Check required settings
    if not settings.model:
        issues.append("LLM model not configured")

    if not settings.key:
        issues.append("API key not configured")

    # Validate model format
    if settings.model and "/" not in settings.model:
        issues.append("Model should be in format 'provider/model'")

    # Check API key format (basic validation)
    if settings.key and len(settings.key) < 10:
        issues.append("API key appears too short")

    return len(issues) == 0, issues
```

### Configuration Backup and Migration

```python
import shutil
from datetime import datetime

def backup_configuration():
    """Create backup of current configuration"""
    settings_file = data_handler.DATA_FOLDER / "settings.yaml"
    if settings_file.exists():
        backup_name = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        backup_path = data_handler.DATA_FOLDER / backup_name
        shutil.copy2(settings_file, backup_path)
        print(f"Configuration backed up to {backup_path}")

def restore_configuration(backup_path: Path):
    """Restore configuration from backup"""
    settings_file = data_handler.DATA_FOLDER / "settings.yaml"
    shutil.copy2(backup_path, settings_file)
    print(f"Configuration restored from {backup_path}")
```

### Configuration Examples

#### Basic Setup

```bash
# Minimal configuration for getting started
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-gemini-api-key"
```

#### Production Setup

```bash
# High-quality model for production use
uv run python app.py settings set model "gpt-4"
uv run python app.py settings set key "sk-your-openai-api-key"
```

#### Development Setup

```bash
# Fast model for development and testing
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-development-api-key"
```

#### Cost-Optimized Setup

```bash
# Budget-friendly model configuration
uv run python app.py settings set model "gpt-3.5-turbo"
uv run python app.py settings set key "sk-your-openai-api-key"
```

### Advanced Configuration

#### Custom Model Weights

```python
# Create custom similarity calculator with adjusted weights
from src.core.components.similarity_calculator import SimilarityCalculator

# Favor semantic understanding over phonetic matching
custom_calculator = SimilarityCalculator(
    semantic_weight=0.7,  # Emphasize meaning
    phonetic_weight=0.3   # Reduce phonetic influence
)

# Use in presentation controller
controller = PresentationController(
    sections=sections,
    start_section=start_section,
    window_size=10  # Smaller window for faster response
)
controller.similarity_calculator = custom_calculator
```

#### Performance Tuning

```python
# Tune for different hardware configurations

# High-end system: More threads, larger windows
recognizer_config = {
    "num_threads": 16,
    "window_size": 16
}

# Low-end system: Fewer threads, smaller windows
recognizer_config = {
    "num_threads": 4,
    "window_size": 8
}

# Battery-optimized: Reduce processing intensity
recognizer_config = {
    "num_threads": 2,
    "frame_duration": 0.2,  # Less frequent processing
    "window_size": 8
}
```

The configuration system provides flexibility for different use cases while maintaining simplicity for basic usage. The template-based approach ensures reliability and provides clear guidance for customization.
