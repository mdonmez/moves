# Architecture Overview

moves is designed as a modular, real-time system that combines speech recognition, natural language processing, and machine learning to provide intelligent presentation navigation. This document provides a comprehensive overview of the system architecture, design patterns, and component interactions.

## Table of Contents

- [System Architecture](#system-architecture)
- [Design Principles](#design-principles)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Processing Pipeline](#processing-pipeline)
- [Real-Time Operations](#real-time-operations)
- [Machine Learning Integration](#machine-learning-integration)
- [Data Storage](#data-storage)
- [Threading Model](#threading-model)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)

## System Architecture

moves follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface Layer                      │
│                      (app.py)                              │
├─────────────────────────────────────────────────────────────┤
│                   Core Business Logic                       │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Presentation    │ │ Speaker          │ │ Settings     │ │
│  │ Controller      │ │ Manager          │ │ Editor       │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Processing Components                     │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Section         │ │ Similarity       │ │ Chunk        │ │
│  │ Producer        │ │ Calculator       │ │ Producer     │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    ML/AI Integration                        │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Speech-to-Text  │ │ Embedding        │ │ LLM          │ │
│  │ (Local ONNX)    │ │ Models           │ │ (Cloud API)  │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     Utility Layer                          │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Data Handler    │ │ Text             │ │ Logger       │ │
│  │                 │ │ Normalizer       │ │              │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    External Interfaces                     │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Audio Input     │ │ File System      │ │ LLM APIs     │ │
│  │ (Microphone)    │ │ (Local Storage)  │ │ (Network)    │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Modular Architecture

- **Single Responsibility**: Each component has one clear purpose
- **Loose Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together

### 2. Real-Time Processing

- **Multi-Threading**: Separate threads for audio, processing, and navigation
- **Non-Blocking Operations**: Asynchronous processing where possible
- **Low Latency**: Optimized for responsive user experience

### 3. Configurability

- **Settings Management**: Centralized configuration system
- **Model Flexibility**: Support for multiple AI models and providers
- **Extensibility**: Easy to add new similarity algorithms and processors

### 4. Data Persistence

- **Structured Storage**: Organized data hierarchy for speakers and sessions
- **JSON Serialization**: Human-readable data formats
- **File System Integration**: Efficient file handling and management

## Core Components

### 1. Presentation Controller

**Location**: `src/core/presentation_controller.py`

The heart of the real-time navigation system:

```python
class PresentationController:
    def __init__(self, sections, start_section, window_size=12):
        # Real-time audio processing
        self.recognizer = OnlineRecognizer.from_transducer(...)
        self.similarity_calculator = SimilarityCalculator()

        # Navigation state
        self.current_section = start_section
        self.recent_words = deque(maxlen=window_size)

        # Threading coordination
        self.shutdown_flag = threading.Event()
        self.navigator_working = False
```

**Key Responsibilities**:

- Real-time audio capture and speech recognition
- Continuous similarity calculation against presentation content
- Automatic slide navigation based on speech matches
- Manual keyboard override support
- Thread coordination and lifecycle management

### 2. Speaker Manager

**Location**: `src/core/speaker_manager.py`

Manages speaker profiles and data processing:

```python
class SpeakerManager:
    def add(self, name, source_presentation, source_transcript):
        # Create speaker profile with unique ID

    def process(self, speakers, llm_model, llm_api_key):
        # AI-powered section generation

    def resolve(self, speaker_pattern):
        # Flexible speaker lookup by name or ID
```

**Key Responsibilities**:

- Speaker profile lifecycle (CRUD operations)
- File management for presentations and transcripts
- AI processing coordination for content generation
- Data validation and error handling

### 3. Settings Editor

**Location**: `src/core/settings_editor.py`

Configuration management with template-based approach:

```python
class SettingsEditor:
    def __init__(self):
        # Load template defaults
        self.template_data = yaml.load(self.template)

        # Merge with user settings
        self._data = {**self.template_data, **user_data}
```

**Key Features**:

- Template-based configuration with defaults
- YAML format for human-readable settings
- Validation against template schema
- Automatic fallback to defaults

## Data Flow

### 1. Setup Phase

```
User Input → Speaker Manager → File System → AI Processing → Stored Sections
     ↓              ↓              ↓              ↓              ↓
  CLI Command → PDF Extraction → LLM Analysis → Section Data → JSON Storage
```

### 2. Real-Time Navigation Phase

```
Audio Input → Speech Recognition → Text Processing → Similarity Matching → Navigation
     ↓               ↓                    ↓               ↓               ↓
  Microphone → Transcribed Text → Normalized Words → Chunk Matching → Slide Navigation
```

### 3. Data Processing Flow

```
Presentation PDF + Transcript PDF
            ↓
    Section Producer (AI)
            ↓
    Generated Sections
            ↓
    Chunk Producer
            ↓
    Navigable Chunks
            ↓
    Similarity Calculator
            ↓
    Real-time Navigation
```

## Processing Pipeline

### 1. Content Preparation Pipeline

```python
# PDF Processing
presentation_data = _extract_pdf(presentation_path, "presentation")
transcript_data = _extract_pdf(transcript_path, "transcript")

# AI Section Generation
sections = _call_llm(presentation_data, transcript_data, llm_model, llm_api_key)

# Chunk Generation for Navigation
chunks = chunk_producer.generate_chunks(sections, window_size)
```

**Steps**:

1. **PDF Extraction**: Extract text content from presentation and transcript files
2. **AI Analysis**: Use LLM to align transcript content with presentation slides
3. **Section Creation**: Generate structured sections with content and indices
4. **Chunk Generation**: Create sliding window chunks for real-time matching

### 2. Real-Time Navigation Pipeline

```python
# Audio Processing Thread
audio_data → STT Model → recognized_text → text_normalizer → normalized_words

# Navigation Thread
normalized_words → chunk_matching → similarity_scoring → navigation_decision → keyboard_control
```

**Steps**:

1. **Audio Capture**: Continuous microphone input with low latency
2. **Speech Recognition**: Local ONNX model for real-time STT
3. **Text Normalization**: Clean and standardize recognized text
4. **Similarity Matching**: Compare speech against presentation chunks
5. **Navigation Decision**: Determine optimal slide movement
6. **Keyboard Control**: Simulate arrow key presses for slide navigation

## Real-Time Operations

### Threading Model

moves uses a multi-threaded architecture for real-time performance:

```python
# Main Threads
audio_thread = threading.Thread(target=self.process_audio, daemon=True)
navigator_thread = threading.Thread(target=self.navigate_presentation, daemon=True)
keyboard_thread = Listener(on_press=self._on_key_press)

# Coordination
self.shutdown_flag = threading.Event()  # Global shutdown coordination
self.navigator_working = False          # Navigation state protection
```

**Thread Responsibilities**:

1. **Audio Thread**:

   - Continuous audio capture from microphone
   - Speech recognition using ONNX models
   - Word queue management

2. **Navigator Thread**:

   - Similarity calculation against presentation content
   - Navigation decision making
   - Keyboard simulation for slide control

3. **Keyboard Thread**:

   - Manual override controls (arrow keys, pause)
   - Integration with automatic navigation

4. **Main Thread**:
   - Audio stream management
   - Thread lifecycle coordination
   - User interface and feedback

### Performance Optimizations

#### 1. Audio Processing

- **Low Latency**: 0.1s frame duration for responsive recognition
- **Buffer Management**: Bounded queues prevent memory buildup
- **Device Optimization**: Automatic microphone selection and configuration

#### 2. Speech Recognition

- **Local Processing**: ONNX models eliminate network latency
- **Optimized Models**: INT8 quantization for faster inference
- **Thread Safety**: Isolated recognition streams per session

#### 3. Similarity Calculation

- **Caching**: LRU cache for phonetic code generation
- **Vectorization**: NumPy operations for semantic similarity
- **Early Exit**: Skip processing when navigation is in progress

## Machine Learning Integration

### 1. Speech-to-Text (STT)

**Technology**: Sherpa-ONNX with local models
**Location**: `src/core/components/ml_models/stt/`

```python
self.recognizer = OnlineRecognizer.from_transducer(
    tokens="stt/tokens.txt",
    encoder="stt/encoder.int8.onnx",
    decoder="stt/decoder.int8.onnx",
    joiner="stt/joiner.int8.onnx",
    num_threads=8,
    decoding_method="greedy_search"
)
```

**Advantages**:

- No network dependency during presentations
- Consistent latency and performance
- Privacy-preserving (no audio sent externally)
- Optimized INT8 models for speed

### 2. Semantic Embeddings

**Technology**: Sentence Transformers
**Location**: `src/core/components/ml_models/embedding/`

```python
self.model = SentenceTransformer("src/core/components/ml_models/embedding")
embeddings = self.model.encode(texts, normalize_embeddings=True)
cosine_scores = np.dot(candidate_embeddings, input_embedding)
```

**Features**:

- Local embedding model for privacy
- Normalized embeddings for consistent scoring
- Batch processing for efficiency
- Cosine similarity for semantic matching

### 3. Large Language Model (LLM)

**Technology**: LiteLLM with multiple provider support
**Purpose**: Content generation and alignment

```python
client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)
response = client.chat.completions.create(
    model=llm_model,
    messages=[system_prompt, user_content],
    response_model=SectionsOutputModel
)
```

**Capabilities**:

- Multi-provider support (Gemini, OpenAI, Anthropic)
- Structured output with Pydantic models
- Intelligent content alignment between transcripts and slides
- Configurable model selection per user preference

## Data Storage

### Directory Structure

```
~/.moves/                           # User data directory
├── settings.yaml                   # User configuration
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

### Data Models

**Location**: `src/data/models.py`

```python
@dataclass(frozen=True)
class Section:
    content: str           # Aligned speech content for slide
    section_index: int     # Zero-based slide index

@dataclass(frozen=True)
class Chunk:
    partial_content: str           # Sliding window text content
    source_sections: list[Section] # Contributing sections

@dataclass
class Speaker:
    name: str                    # Human-readable name
    speaker_id: SpeakerId       # Unique identifier
    source_presentation: Path   # Original presentation file
    source_transcript: Path     # Original transcript file
```

**Design Features**:

- **Immutable Sections/Chunks**: Prevent accidental modification during navigation
- **Type Safety**: Strong typing with custom type aliases
- **Serialization Support**: JSON-compatible for data persistence

## Error Handling

### 1. Graceful Degradation

```python
try:
    # Critical operation
    result = process_audio()
except Exception as e:
    logger.error(f"Audio processing failed: {e}")
    # Continue with degraded functionality
    self.shutdown_flag.set()
```

### 2. Resource Management

```python
try:
    with sd.InputStream(...) as stream:
        # Audio processing
        pass
finally:
    # Cleanup threads and resources
    self.shutdown_flag.set()
    audio_thread.join(timeout=1.0)
```

### 3. User-Friendly Messages

```python
# CLI error handling
except Exception as e:
    typer.echo(f"Could not add speaker '{name}'.", err=True)
    typer.echo(f"    {str(e)}", err=True)
    raise typer.Exit(1)
```

**Error Handling Principles**:

- **Fail Fast**: Detect errors early in processing pipeline
- **Resource Cleanup**: Ensure threads and files are properly closed
- **User Communication**: Provide actionable error messages
- **Logging**: Comprehensive logging for debugging and monitoring

## Performance Considerations

### 1. Memory Management

- **Bounded Queues**: Prevent unbounded memory growth in audio processing
- **LRU Caching**: Cache expensive computations (phonetic codes, embeddings)
- **Efficient Data Structures**: Use appropriate containers for different use cases

### 2. CPU Optimization

- **Multi-threading**: Parallel processing for audio, navigation, and UI
- **Model Optimization**: INT8 quantized models for faster inference
- **Batch Processing**: Group operations where possible

### 3. I/O Optimization

- **Asynchronous Operations**: Non-blocking file and network operations
- **Local Models**: Reduce network dependency during presentations
- **Efficient Serialization**: JSON for human-readable, efficient data storage

### 4. Real-Time Constraints

- **Target Latency**: < 500ms from speech to navigation
- **Frame Rate**: 100ms audio frames for responsive recognition
- **Thread Priorities**: Audio processing gets highest priority

This architecture enables moves to provide reliable, real-time presentation navigation while maintaining modularity and extensibility for future enhancements.
