# Installation Guide

## System Requirements

### Operating System
- **Windows**: Windows 10 or later (64-bit)
- **macOS**: macOS 10.14 (Mojave) or later
- **Linux**: Ubuntu 18.04+ / CentOS 7+ / Other modern distributions

### Python Environment
- **Python Version**: 3.13 or higher (required)
- **Package Manager**: pip (comes with Python)
- **Virtual Environment**: Recommended but not required

### Hardware Requirements

#### Minimum Requirements
- **CPU**: Dual-core processor (Intel i3 / AMD equivalent)
- **Memory**: 4GB RAM
- **Storage**: 2GB free disk space
- **Audio**: Microphone input device
- **Network**: Internet connection for LLM API calls

#### Recommended Requirements
- **CPU**: Quad-core processor (Intel i5 / AMD equivalent)
- **Memory**: 8GB RAM or higher
- **Storage**: 5GB free disk space (for ML models and data)
- **Audio**: High-quality microphone for better recognition
- **Network**: Stable broadband connection

### External Dependencies

#### Machine Learning Models
The system automatically downloads required models:
- **Speech Recognition Models**: ~200MB (Sherpa-ONNX ONNX models)
- **Embedding Models**: ~500MB (sentence-transformers models)

#### API Access
You'll need an API key from one of these providers:
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude)
- **Google** (Gemini)
- **Other LiteLLM-supported providers**

## Installation Methods

### Method 1: Source Installation (Recommended)

#### Step 1: Clone Repository
```bash
# Clone the repository
git clone https://github.com/mdonmez/moves.git
cd moves
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv moves-env

# Activate virtual environment
# On Windows:
moves-env\Scripts\activate
# On macOS/Linux:
source moves-env/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individual dependencies:
pip install instructor>=1.10.0
pip install jellyfish>=1.2.0  
pip install litellm>=1.75.8
pip install num2words>=0.5.14
pip install pymupdf>=1.26.3
pip install pynput>=1.8.1
pip install rapidfuzz>=3.13.0
pip install ruamel-yaml>=0.18.14
pip install sentence-transformers>=5.1.0
pip install sherpa-onnx>=1.12.9
pip install sounddevice>=0.5.2
pip install typer>=0.9.0
```

#### Step 4: Verify Installation
```bash
# Test the CLI
python app.py --help

# Should output the main help menu
```

### Method 2: Development Installation

If you plan to contribute or modify the code:

```bash
# Clone with development branch
git clone https://github.com/mdonmez/moves.git
cd moves

# Install in development mode
pip install -e .

# Install additional development dependencies
pip install pytest black isort mypy

# Run tests (if available)
pytest tests/
```

## Initial Configuration

### Step 1: Configure LLM Provider

Choose and configure your LLM provider:

#### OpenAI Configuration
```bash
# Set OpenAI as your provider
python app.py settings set model "openai/gpt-4"

# Set your OpenAI API key  
python app.py settings set key "sk-your-openai-api-key-here"
```

#### Anthropic Configuration
```bash
# Set Claude as your provider
python app.py settings set model "anthropic/claude-3-sonnet"

# Set your Anthropic API key
python app.py settings set key "your-anthropic-api-key-here"
```

#### Google Gemini Configuration
```bash
# Set Gemini as your provider
python app.py settings set model "gemini/gemini-2.0-flash"

# Set your Google API key
python app.py settings set key "your-google-api-key-here"
```

### Step 2: Verify Configuration
```bash
# Check your settings
python app.py settings list

# Should show:
# Application Settings.
#     model (LLM Model) -> your-chosen-model
#     key (API Key) -> your-api-key
```

### Step 3: Test Audio System
```bash
# Check available audio devices
python -c "
import sounddevice as sd
print('Available audio devices:')
print(sd.query_devices())
"
```

## Model Downloads

### Automatic Model Download
Models are downloaded automatically on first use:

```bash
# First run will trigger model downloads
python app.py speaker add "Test Speaker" presentation.pdf transcript.pdf

# This will download:
# - Sherpa-ONNX speech recognition models (~200MB)
# - sentence-transformers embedding models (~500MB)
```

### Manual Model Download (Optional)
To pre-download models:

```python
# Download speech recognition models
from sherpa_onnx import OnlineRecognizer
recognizer = OnlineRecognizer.from_transducer(
    tokens="src/core/components/ml_models/stt/tokens.txt",
    encoder="src/core/components/ml_models/stt/encoder.int8.onnx", 
    decoder="src/core/components/ml_models/stt/decoder.int8.onnx",
    joiner="src/core/components/ml_models/stt/joiner.int8.onnx",
    num_threads=8,
    decoding_method="greedy_search",
)

# Download embedding models
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("src/core/components/ml_models/embedding")
```

## Directory Structure

After installation, your project structure should look like:

```
moves/
├── app.py                          # Main CLI entry point
├── src/                           # Source code
│   ├── core/                      # Core components
│   │   ├── components/            # Individual components
│   │   │   ├── ml_models/         # ML model storage
│   │   │   │   ├── stt/          # Speech-to-text models
│   │   │   │   └── embedding/     # Embedding models
│   │   │   ├── similarity_units/  # Similarity engines
│   │   │   ├── chunk_producer.py
│   │   │   ├── section_producer.py
│   │   │   └── similarity_calculator.py
│   │   ├── presentation_controller.py
│   │   ├── settings_editor.py
│   │   └── speaker_manager.py
│   ├── data/                      # Data models and templates
│   │   ├── llm_instruction.md
│   │   ├── models.py
│   │   └── settings_template.yaml
│   └── utils/                     # Utility functions
├── docs/                          # Documentation
├── pyproject.toml                 # Project configuration
└── requirements.txt               # Dependencies
```

## Data Directory

The system creates a data directory in your home folder:

```
~/.moves/                          # User data directory
├── settings.yaml                  # Global configuration
└── speakers/                      # Speaker profiles
    └── {speaker-id}/              # Individual speaker data
        ├── speaker.json           # Speaker metadata
        ├── presentation.pdf       # Presentation file
        ├── transcript.pdf         # Transcript file
        └── sections.json          # Generated sections
```

## Troubleshooting Installation

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# If too old, install Python 3.13+
# Windows: Download from python.org
# macOS: brew install python@3.13
# Ubuntu: sudo apt install python3.13
```

#### Permission Errors
```bash
# On Linux/macOS, use --user flag
pip install --user -r requirements.txt

# Or fix permissions
sudo chown -R $USER ~/.cache/pip
```

#### Audio Device Issues
```bash
# Test microphone access
python -c "
import sounddevice as sd
import numpy as np
print('Testing microphone...')
recording = sd.rec(int(2 * 16000), samplerate=16000, channels=1)
sd.wait()
print('Recording completed successfully!')
"
```

#### Model Download Issues
```bash
# Manual model download location setup
export HF_HOME=/path/to/models  # For transformers
export SHERPA_ONNX_MODEL_PATH=/path/to/sherpa/models
```

#### Network/Firewall Issues
Ensure these domains are accessible:
- `api.openai.com` (if using OpenAI)
- `api.anthropic.com` (if using Anthropic)  
- `generativelanguage.googleapis.com` (if using Google)
- `huggingface.co` (for model downloads)

### Platform-Specific Issues

#### Windows
- Install Visual C++ Build Tools if compilation fails
- Ensure Windows Defender doesn't block downloads
- Check microphone privacy settings

#### macOS
- Grant microphone permissions in System Preferences
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for dependencies if needed

#### Linux
- Install system audio libraries: `sudo apt install portaudio19-dev python3-dev`
- Check ALSA/PulseAudio configuration
- Ensure user is in audio group: `sudo usermod -a -G audio $USER`

### Getting Help

If you encounter issues:

1. **Check System Requirements**: Verify Python version and dependencies
2. **Review Error Messages**: Look for specific error details
3. **Check Logs**: Examine any error output carefully
4. **Search Documentation**: Review [Troubleshooting Guide](./troubleshooting.md)
5. **GitHub Issues**: Search existing issues or create new one
6. **Community Support**: Join discussions in repository

## Next Steps

After successful installation:

1. **Read the [User Guide](./user-guide.md)** for usage instructions
2. **Review [Configuration](./configuration.md)** for advanced settings  
3. **Explore [Core Components](./core-components.md)** to understand the system
4. **Check [API Reference](./api-reference.md)** for detailed documentation

Your Moves installation is now ready for use!