# moves Documentation

**moves** is an AI-powered presentation control system that enables seamless voice-controlled slide navigation during live presentations. The system uses advanced speech recognition, natural language processing, and machine learning to automatically navigate presentation slides based on what the speaker is saying.

## Table of Contents

- [Getting Started](./getting-started.md) - Installation, setup, and first steps
- [Architecture Overview](./architecture.md) - System design, components, and data flow
- [Core Components](./components/) - Detailed documentation of system components
  - [Presentation Controller](./components/presentation-controller.md) - Real-time voice navigation engine
  - [Speaker Manager](./components/speaker-manager.md) - Speaker profile and data management
  - [Settings Editor](./components/settings-editor.md) - Configuration management
  - [Section Producer](./components/section-producer.md) - AI-powered content generation
  - [Similarity Calculator](./components/similarity-calculator.md) - Speech matching algorithms
  - [Chunk Producer](./components/chunk-producer.md) - Text segmentation and processing
- [Data Models](./data-models.md) - Core data structures and types
- [Command Line Interface](./cli.md) - Complete CLI reference and usage examples
- [Configuration](./configuration.md) - Settings, templates, and environment setup
- [Machine Learning Models](./ml-models.md) - Embedding models, STT, and AI integration
- [Utilities](./utilities.md) - Supporting modules and helper functions
- [Development Guide](./development.md) - Contributing, testing, and extending the system
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions
- [API Reference](./api-reference.md) - Internal API documentation

## Quick Start

```bash
# Install dependencies
uv sync

# Add a speaker profile
uv run python app.py speaker add "John Doe" presentation.pdf transcript.pdf

# Configure LLM settings
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-api-key"

# Process speaker data for AI navigation
uv run python app.py speaker process "John Doe"

# Start live voice-controlled presentation
uv run python app.py presentation control "John Doe"
```

## Key Features

- **Voice-Controlled Navigation**: Real-time slide navigation based on speech recognition
- **AI-Powered Content Matching**: Intelligent alignment of speech to presentation content
- **Multi-Modal Similarity**: Combines semantic and phonetic matching for accurate navigation
- **Flexible Speaker Management**: Support for multiple speakers and presentations
- **Real-Time Audio Processing**: Low-latency speech recognition and processing
- **Hybrid Similarity Scoring**: Advanced algorithms for robust speech-to-content matching
- **CLI Interface**: Comprehensive command-line tools for system management

## Architecture Highlights

- **Modular Design**: Clean separation of concerns with dedicated components
- **Real-Time Processing**: Multi-threaded architecture for responsive performance
- **Machine Learning Integration**: Local STT models and cloud-based LLM services
- **Configurable Pipeline**: Flexible settings and customizable processing parameters
- **Data Persistence**: Structured data storage for speakers, sections, and configurations

## System Requirements

- **Python**: 3.13+
- **Dependencies**: See [pyproject.toml](../pyproject.toml) for complete list
- **Audio**: Microphone input for speech recognition
- **Storage**: Local file system for data and model storage
- **Network**: Internet connection for LLM API calls during processing

## Project Structure

```
moves/
├── app.py                           # Main CLI application
├── pyproject.toml                   # Project configuration and dependencies
├── src/
│   ├── core/                        # Core system components
│   │   ├── presentation_controller.py  # Voice navigation engine
│   │   ├── speaker_manager.py         # Speaker data management
│   │   ├── settings_editor.py         # Configuration management
│   │   └── components/                 # Processing components
│   │       ├── section_producer.py       # AI content generation
│   │       ├── similarity_calculator.py  # Speech matching
│   │       ├── chunk_producer.py         # Text segmentation
│   │       ├── ml_models/                # Pre-trained models
│   │       └── similarity_units/         # Matching algorithms
│   ├── data/                        # Data models and templates
│   │   ├── models.py                   # Core data structures
│   │   ├── settings_template.yaml     # Default configuration
│   │   └── llm_instruction.md         # AI processing instructions
│   └── utils/                       # Utility modules
│       ├── data_handler.py            # File system operations
│       ├── text_normalizer.py         # Text preprocessing
│       ├── logger.py                  # Logging utilities
│       └── id_generator.py           # Unique ID generation
└── docs/                           # Documentation (this directory)
```

## Use Cases

- **Live Presentations**: Professional presentations with hands-free navigation
- **Educational Settings**: Lectures and teaching scenarios
- **Conference Speaking**: Public speaking with seamless slide control
- **Training Sessions**: Corporate and educational training delivery
- **Remote Presentations**: Virtual meetings and webinars

## Documentation Status

This documentation set is now complete and provides comprehensive coverage of the moves application:

- ✅ **Index** - This overview document
- ✅ **Getting Started** - Installation and basic usage
- ✅ **Architecture** - System design and component overview
- ✅ **Component Documentation** - Detailed component documentation
  - ✅ PresentationController - Voice-controlled navigation
  - ✅ SpeakerManager - Speaker and presentation management
  - ✅ SettingsEditor - Configuration management
  - ✅ SectionProducer - AI-powered content processing
  - ✅ SimilarityCalculator - Hybrid similarity matching
  - ✅ ChunkProducer - Content segmentation
- ✅ **Data Models** - Core data structures and relationships
- ✅ **CLI Reference** - Complete command-line interface documentation
- ✅ **Configuration** - Settings and configuration guide
- ✅ **Utilities** - Supporting modules and helper functions
- ✅ **ML Models** - Machine learning integration and model management
- ✅ **API Reference** - Complete API documentation
- ✅ **Development** - Developer contribution guide
- ✅ **Troubleshooting** - Common issues and solutions

## Next Steps

1. **New Users**: Start with the [Getting Started Guide](./getting-started.md)
2. **Developers**: Review the [Architecture Overview](./architecture.md)
3. **Contributors**: See the [Development Guide](./development.md)
4. **Integration**: Check the [API Reference](./api-reference.md)
