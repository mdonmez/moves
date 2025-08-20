# Moves - AI-Powered Presentation Control System

## Overview

**Moves** is an intelligent presentation control system that enables seamless slide navigation through voice commands. Using advanced AI technologies including speech recognition, semantic understanding, and phonetic matching, Moves automatically detects what you're saying during a presentation and navigates to the appropriate slides in real-time.

## Key Features

- **Voice-Controlled Navigation**: Automatically advance slides based on your spoken content
- **AI-Powered Section Generation**: Process presentations and transcripts to create synchronized content sections
- **Dual Similarity Matching**: Combines semantic and phonetic similarity for robust voice recognition
- **Real-time Audio Processing**: Low-latency speech recognition optimized for live presentations
- **Speaker Profile Management**: Manage multiple speakers and their presentation materials
- **Flexible Configuration**: Support for various LLM providers and customizable settings

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/mdonmez/moves.git
cd moves

# Install dependencies (requires Python 3.13+)
pip install -r requirements.txt
```

### 2. Configure the System

```bash
# Set your LLM model (supports OpenAI, Anthropic, Google, etc.)
python app.py settings set model "openai/gpt-4"

# Set your API key
python app.py settings set key "your-api-key-here"
```

### 3. Add a Speaker

```bash
# Add a new speaker with presentation and transcript files
python app.py speaker add "John Doe" presentation.pdf transcript.pdf
```

### 4. Process Speaker Data

```bash
# Generate synchronized sections using AI
python app.py speaker process "John Doe"
```

### 5. Start Live Control

```bash
# Begin voice-controlled presentation
python app.py presentation control "John Doe"
```

## How It Works

1. **Content Processing**: Upload your presentation slides (PDF) and transcript (PDF)
2. **AI Section Generation**: The system uses LLM to align slide content with transcript segments
3. **Voice Recognition**: Real-time speech-to-text converts your spoken words
4. **Similarity Matching**: Compares spoken content against expected sections using both semantic and phonetic analysis
5. **Automatic Navigation**: Triggers slide transitions when content matches

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Speech Input  │───▶│ Presentation     │───▶│  Slide Output   │
│   (Microphone)  │    │ Controller       │    │  (Navigation)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │                 │
            ┌──────────▼────────┐ ┌──────▼──────────┐
            │ Speech Recognition│ │ Similarity      │
            │ (Sherpa-ONNX)     │ │ Calculator      │
            └───────────────────┘ └─────────────────┘
                                          │
                                 ┌────────┴────────┐
                                 │                 │
                      ┌──────────▼────────┐ ┌──────▼────────┐
                      │ Semantic Engine   │ │ Phonetic      │
                      │ (Transformers)    │ │ Engine        │
                      └───────────────────┘ └───────────────┘
```

## Core Components

- **[PresentationController](./core-components.md#presentationcontroller)**: Main orchestrator for live presentation control
- **[SpeakerManager](./core-components.md#speakermanager)**: Handles speaker profiles and data management
- **[SectionProducer](./llm-integration.md#sectionproducer)**: AI-powered content synchronization
- **[SimilarityCalculator](./similarity-system.md#similaritycalculator)**: Multi-modal content matching
- **[Speech Processing](./speech-processing.md)**: Real-time audio analysis and recognition

## Documentation Index

- **[Installation Guide](./installation.md)** - Detailed setup instructions and requirements
- **[User Guide](./user-guide.md)** - Complete usage instructions and workflows
- **[Architecture Overview](./architecture.md)** - System design and component interactions
- **[Core Components](./core-components.md)** - Deep dive into main system components
- **[Similarity System](./similarity-system.md)** - How content matching works
- **[Speech Processing](./speech-processing.md)** - Audio processing and recognition
- **[LLM Integration](./llm-integration.md)** - AI content processing and section generation
- **[Configuration](./configuration.md)** - Settings and customization options
- **[API Reference](./api-reference.md)** - Detailed API documentation
- **[Troubleshooting](./troubleshooting.md)** - Common issues and solutions
- **[Development Guide](./development.md)** - Contributing and extending the system

## System Requirements

- **Python**: 3.13 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Audio**: Microphone input device
- **Network**: Internet connection for LLM API calls

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, feature requests, or bug reports, please visit the [GitHub repository](https://github.com/mdonmez/moves) or open an issue.