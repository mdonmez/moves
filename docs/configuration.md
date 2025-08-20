# Configuration Guide

## Overview

Moves provides a flexible configuration system that allows customization of LLM providers, processing parameters, and system behavior. This guide covers all configuration options, from basic setup to advanced customization.

## Configuration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Configuration System                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────────────────────┐  │
│  │  CLI Commands   │    │                Settings Storage                     │  │
│  │                 │    │                                                     │  │
│  │ • settings set  │───▶│  ~/.moves/                                          │  │
│  │ • settings list │    │  ├── settings.yaml      # User configuration       │  │
│  │ • settings unset│    │  └── speakers/          # Speaker-specific data    │  │
│  └─────────────────┘    │      └── {id}/                                     │  │
│                         │          ├── speaker.json                          │  │
│                         │          └── sections.json                         │  │
│                         └─────────────────────────────────────────────────────┘  │
│                                           ▲                                     │
│                         ┌─────────────────┴─────────────────────────────────────┐  │
│                         │              Template System                        │  │
│                         │                                                     │  │
│                         │  src/data/settings_template.yaml                   │  │
│                         │  ├── model: "gemini/gemini-2.0-flash"             │  │
│                         │  └── key: null                                     │  │
│                         └─────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Basic Configuration

### Initial Setup

After installation, configure your LLM provider and API key:

```bash
# View current configuration
python app.py settings list

# Set your preferred model
python app.py settings set model "openai/gpt-4"

# Set your API key
python app.py settings set key "your-api-key-here"
```

### Configuration Files

#### Settings Template (`src/data/settings_template.yaml`)
```yaml
# Default configuration template
model: "gemini/gemini-2.0-flash"
key: null
```

#### User Settings (`~/.moves/settings.yaml`)
```yaml
# User's actual configuration (created automatically)
model: "openai/gpt-4"
key: "sk-your-openai-api-key"
```

### Settings Management

#### SettingsEditor Class
```python
class SettingsEditor:
    def __init__(self):
        # Load template defaults
        self.template = Path("src/data/settings_template.yaml")
        self.settings = DATA_FOLDER / "settings.yaml"
        
        # Merge template with user settings
        self._data = {**template_data, **user_data}
    
    def set(self, key: str, value: str) -> bool:
        """Update a setting value"""
        
    def unset(self, key: str) -> bool:
        """Reset setting to template default"""
        
    def list(self) -> Settings:
        """Get current settings as Settings object"""
```

## LLM Provider Configuration

### Supported Providers

#### OpenAI Configuration
```bash
# GPT-4 (recommended for quality)
python app.py settings set model "openai/gpt-4"
python app.py settings set key "sk-your-openai-api-key"

# GPT-3.5 Turbo (cost-effective)  
python app.py settings set model "openai/gpt-3.5-turbo"
python app.py settings set key "sk-your-openai-api-key"
```

**OpenAI API Key Setup:**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy key and configure with Moves

#### Anthropic Configuration
```bash
# Claude 3 Sonnet (balanced quality/cost)
python app.py settings set model "anthropic/claude-3-sonnet"
python app.py settings set key "your-anthropic-api-key"

# Claude 3 Haiku (fastest, cheapest)
python app.py settings set model "anthropic/claude-3-haiku"  
python app.py settings set key "your-anthropic-api-key"
```

**Anthropic API Key Setup:**
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Generate API key in settings
3. Configure with Moves

#### Google Gemini Configuration
```bash
# Gemini 2.0 Flash (default, cost-effective)
python app.py settings set model "gemini/gemini-2.0-flash"
python app.py settings set key "your-google-api-key"

# Gemini Pro (higher capability)
python app.py settings set model "gemini/gemini-pro"
python app.py settings set key "your-google-api-key"
```

**Google API Key Setup:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create API key
3. Configure with Moves

#### Azure OpenAI Configuration
```bash
# Azure-hosted OpenAI models
python app.py settings set model "azure/gpt-4"
python app.py settings set key "your-azure-api-key"

# Configure additional Azure parameters (in code)
AZURE_CONFIG = {
    "api_base": "https://your-resource.openai.azure.com/",
    "api_version": "2023-12-01-preview",
    "deployment_name": "your-deployment-name"
}
```

#### AWS Bedrock Configuration
```bash
# Claude on AWS Bedrock
python app.py settings set model "bedrock/claude-3-sonnet"
python app.py settings set key "your-aws-access-key"

# Additional AWS configuration needed
AWS_CONFIG = {
    "region_name": "us-east-1", 
    "aws_secret_access_key": "your-secret-key"
}
```

### Model Selection Guide

#### Quality vs Cost Comparison

| Provider | Model | Quality | Speed | Cost/1K Tokens | Best For |
|----------|--------|---------|--------|----------------|----------|
| OpenAI | GPT-4 | Excellent | Medium | $0.03/$0.06 | Complex presentations |
| OpenAI | GPT-3.5-turbo | Very Good | Fast | $0.0015/$0.002 | General use |
| Anthropic | Claude-3-sonnet | Excellent | Medium | $0.003/$0.015 | Long presentations |
| Anthropic | Claude-3-haiku | Good | Very Fast | $0.00025/$0.00125 | Simple presentations |
| Google | Gemini-2.0-flash | Very Good | Very Fast | $0.000075/$0.0003 | Cost optimization |
| Google | Gemini-pro | Good | Fast | $0.0005/$0.0015 | Balanced option |

#### Recommendation Matrix

**For Technical Presentations:**
- **Best**: OpenAI GPT-4 or Anthropic Claude-3-sonnet
- **Reason**: Better handling of technical terminology and complex concepts

**For Cost Optimization:**
- **Best**: Google Gemini-2.0-flash or Anthropic Claude-3-haiku  
- **Reason**: Lowest cost per token while maintaining quality

**For Long Presentations (>20 slides):**
- **Best**: Anthropic Claude-3-sonnet or Google Gemini models
- **Reason**: Large context windows handle long content better

**For Multi-language Content:**
- **Best**: OpenAI GPT-4 or Google Gemini models
- **Reason**: Better multilingual capabilities

## Advanced Configuration

### System Parameters

#### Window Size Configuration
```python
# In presentation_controller_instance() function (app.py)
def presentation_controller_instance(sections: list[Section], start_section: Section):
    return PresentationController(
        sections=sections,
        start_section=start_section,
        window_size=12,  # Adjust this value
    )
```

**Window Size Guidelines:**
- **Small (8 words)**: More responsive, less context
- **Default (12 words)**: Balanced performance
- **Large (16 words)**: More context, less responsive

#### Similarity Weights Configuration  
```python
# In similarity_calculator.py
class SimilarityCalculator:
    def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
        # Adjust these weights based on your needs
        self.semantic_weight = semantic_weight
        self.phonetic_weight = phonetic_weight
```

**Weight Adjustment Guide:**
- **Technical Content**: Increase semantic weight to 0.6
- **Noisy Environment**: Increase phonetic weight to 0.7  
- **Non-native Speakers**: Balance at 0.5/0.5

#### Audio Processing Configuration
```python
# In presentation_controller.py
class PresentationController:
    def __init__(self, ...):
        self.frame_duration = 0.1      # 100ms frames (adjust for latency)
        self.sample_rate = 16000       # 16kHz (optimal for speech)
        self.audio_queue = deque(maxlen=5)  # 500ms buffer
```

**Audio Parameter Tuning:**
- **Low Latency**: `frame_duration = 0.05` (50ms)
- **High Stability**: `frame_duration = 0.2` (200ms)  
- **Buffer Size**: Adjust `maxlen` for stability vs memory usage

### Environment Variables

#### API Configuration
```bash
# Alternative to CLI configuration
export MOVES_LLM_MODEL="openai/gpt-4"
export MOVES_API_KEY="your-api-key"

# Model-specific configuration
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  
export GOOGLE_API_KEY="your-google-key"

# Advanced settings
export MOVES_DATA_DIR="$HOME/.moves"
export MOVES_MODELS_DIR="/custom/model/path"
```

#### System Configuration
```bash
# Performance tuning
export MOVES_RECOGNITION_THREADS="8"
export MOVES_MAX_AUDIO_LATENCY="0.1"
export MOVES_SIMILARITY_CACHE_SIZE="350"

# Debug settings
export MOVES_DEBUG="true"
export MOVES_LOG_LEVEL="INFO"
```

### Custom Configuration Files

#### Speaker-Specific Configuration
```json
// ~/.moves/speakers/{speaker_id}/config.json (future feature)
{
    "window_size": 14,
    "semantic_weight": 0.5,
    "phonetic_weight": 0.5,
    "navigation_threshold": 0.75,
    "audio_sensitivity": "high"
}
```

#### Presentation-Type Profiles
```yaml
# ~/.moves/profiles/technical.yaml (future feature)  
name: "Technical Presentations"
settings:
  semantic_weight: 0.6
  phonetic_weight: 0.4
  window_size: 16
  llm_temperature: 0.1

# ~/.moves/profiles/general.yaml
name: "General Presentations"  
settings:
  semantic_weight: 0.4
  phonetic_weight: 0.6
  window_size: 12
  llm_temperature: 0.2
```

## Configuration Validation

### Settings Validation
```python
def validate_settings(settings: Settings) -> list[str]:
    """
    Validate configuration and return list of issues
    """
    issues = []
    
    # Validate model format
    if not settings.model or "/" not in settings.model:
        issues.append("Invalid model format. Expected: 'provider/model-name'")
    
    # Validate API key presence
    if not settings.key or len(settings.key.strip()) < 10:
        issues.append("API key missing or too short")
    
    # Validate model-key compatibility
    provider = settings.model.split("/")[0]
    if provider == "openai" and not settings.key.startswith("sk-"):
        issues.append("OpenAI API key should start with 'sk-'")
    
    return issues
```

### Connection Testing
```bash
# Test your configuration before processing
python -c "
from src.core.settings_editor import SettingsEditor
from src.core.components.section_producer import _call_llm

editor = SettingsEditor()
settings = editor.list()

try:
    # Test with minimal content
    result = _call_llm(
        presentation_data='# Slide Page 0\nTest slide content',
        transcript_data='This is a test transcript for configuration validation.',
        llm_model=settings.model,
        llm_api_key=settings.key
    )
    print('✓ Configuration valid - LLM connection successful')
except Exception as e:
    print(f'✗ Configuration error: {e}')
"
```

## Performance Tuning

### Memory Optimization

#### Model Memory Management
```python
# Optimize embedding model memory usage
EMBEDDING_MODEL_CONFIG = {
    "device": "cpu",           # Use CPU to save GPU memory
    "cache_folder": "/tmp/models",  # Custom cache location
    "trust_remote_code": False,     # Security setting
}
```

#### Audio Buffer Optimization
```python
# Adjust based on available memory
AUDIO_CONFIG = {
    "queue_size": 3,           # Smaller queue for limited memory
    "frame_duration": 0.15,    # Larger frames for efficiency
    "sample_rate": 16000,      # Don't increase for speech
}
```

### Processing Speed Optimization

#### Concurrent Processing
```python
# Optimize for multiple speaker processing
PROCESSING_CONFIG = {
    "max_concurrent_llm_calls": 2,   # Limit concurrent API calls
    "batch_delay": 1.0,              # Delay between batches  
    "timeout_seconds": 120,          # Request timeout
}
```

#### Caching Configuration
```python
# Optimize similarity calculation caching
CACHE_CONFIG = {
    "phonetic_cache_size": 350,      # LRU cache for phonetic codes
    "embedding_cache": False,        # Don't cache embeddings (memory)
    "chunk_cache": True,             # Cache generated chunks
}
```

## Security Configuration

### API Key Management

#### Secure Storage
```bash
# Use system keyring (future feature)
export MOVES_USE_KEYRING="true"

# Or use encrypted storage
export MOVES_ENCRYPT_CONFIG="true"
export MOVES_CONFIG_PASSWORD="your-encryption-password"
```

#### Key Rotation
```bash
# Regular key rotation practice
python app.py settings set key "new-api-key"

# Backup old configuration
cp ~/.moves/settings.yaml ~/.moves/settings.yaml.backup
```

### Network Security
```bash
# Proxy configuration
export HTTPS_PROXY="https://your-proxy:8080"
export HTTP_PROXY="http://your-proxy:8080"

# SSL verification
export MOVES_VERIFY_SSL="true"
export MOVES_CA_BUNDLE="/path/to/ca-certificates.crt"
```

## Troubleshooting Configuration

### Common Configuration Issues

#### Invalid API Key
```bash
# Symptoms: Authentication errors during processing
# Solution: Verify key format and validity
python app.py settings list
# Check key format matches provider requirements
```

#### Model Not Found
```bash
# Symptoms: "Model not found" errors
# Solution: Check model name format
python app.py settings set model "provider/correct-model-name"
```

#### Network Connectivity
```bash
# Test network connectivity to LLM providers
curl -I https://api.openai.com      # OpenAI
curl -I https://api.anthropic.com   # Anthropic
curl -I https://generativelanguage.googleapis.com  # Google
```

#### Permission Issues
```bash
# Symptoms: Cannot write to ~/.moves/
# Solution: Check permissions
ls -la ~/.moves/
chmod 755 ~/.moves/
chmod 644 ~/.moves/settings.yaml
```

### Diagnostic Commands

#### Configuration Dump
```bash
# View all current settings
python app.py settings list

# Check file locations
python -c "
from src.utils.data_handler import DATA_FOLDER
from src.core.settings_editor import SettingsEditor
print(f'Data folder: {DATA_FOLDER}')
print(f'Settings file: {DATA_FOLDER / \"settings.yaml\"}')
editor = SettingsEditor()
print(f'Template: {editor.template}')
"
```

#### System Information
```bash
# Check system compatibility
python -c "
import sys
import platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.system()} {platform.release()}')
print(f'Architecture: {platform.machine()}')

# Check required modules
try:
    import sounddevice
    print('✓ Audio system available')
except ImportError:
    print('✗ Audio system not available')

try:
    import sherpa_onnx
    print('✓ Speech recognition available')
except ImportError:
    print('✗ Speech recognition not available')
"
```

## Best Practices

### Configuration Management

#### Version Control
```bash
# Track configuration changes
cd ~/.moves
git init
git add settings.yaml
git commit -m "Initial configuration"

# After changes
git add -A
git commit -m "Updated LLM model to GPT-4"
```

#### Backup Strategy
```bash
# Regular backups
cp ~/.moves/settings.yaml ~/backups/moves-settings-$(date +%Y%m%d).yaml

# Backup speaker data
tar -czf ~/backups/moves-speakers-$(date +%Y%m%d).tar.gz ~/.moves/speakers/
```

#### Environment Separation
```bash
# Development environment
export MOVES_DATA_DIR="$HOME/.moves-dev"
export MOVES_LLM_MODEL="anthropic/claude-3-haiku"  # Cheaper for testing

# Production environment  
export MOVES_DATA_DIR="$HOME/.moves"
export MOVES_LLM_MODEL="openai/gpt-4"  # Higher quality
```

### Performance Monitoring

#### Usage Tracking
```python
# Monitor API usage and costs (future feature)
def track_api_usage(model: str, input_tokens: int, output_tokens: int):
    usage_log = DATA_FOLDER / "usage.json"
    # Log token usage for cost tracking
```

#### Performance Metrics
```python
# Monitor system performance
def log_performance_metrics(processing_time: float, accuracy_score: float):
    metrics_log = DATA_FOLDER / "metrics.json"
    # Track processing time and accuracy
```

This comprehensive configuration guide covers all aspects of customizing Moves for your specific needs, from basic LLM setup to advanced performance tuning and security considerations.