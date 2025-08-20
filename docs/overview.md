# Moves - Technical Overview

Moves is a sophisticated AI-powered presentation control system that enables voice-controlled navigation through presentations using advanced natural language processing, speech recognition, and semantic similarity matching. The system implements a multi-layered architecture combining PDF processing, large language model integration, real-time speech-to-text conversion, and intelligent content matching algorithms.

## System Architecture

Moves employs a modular, event-driven architecture with three primary operational domains:

- **Speaker Management Pipeline**: AI-powered content processing and data ingestion
- **Real-time Presentation Control**: Voice-controlled navigation with ML-based matching
- **Configuration Management**: Template-driven settings with YAML persistence

```mermaid
graph TB
    subgraph "Input Layer"
        A[PDF Presentations] 
        B[Transcript Files]
        C[Voice Input]
        D[User Commands]
    end
    
    subgraph "Processing Layer"
        E[PDF Extraction Engine]
        F[LLM Section Producer]
        G[STT Processing Pipeline]
        H[Similarity Calculator]
    end
    
    subgraph "Core Components"
        I[Speaker Manager]
        J[Presentation Controller] 
        K[Settings Editor]
        L[Data Handler]
    end
    
    subgraph "Storage Layer"
        M[File System Cache]
        N[Speaker Profiles]
        O[Section Database]
        P[Configuration Store]
    end
    
    A --> E
    B --> E
    C --> G
    D --> I
    D --> J
    D --> K
    E --> F
    F --> I
    G --> H
    H --> J
    I --> L
    J --> L
    K --> L
    L --> M
    L --> N
    L --> O
    L --> P
```

---

## Speaker Management Pipeline

The speaker management subsystem orchestrates the ingestion, processing, and structuring of presentation content through a sophisticated AI-powered pipeline that transforms raw PDF documents into semantically-aware, navigable content sections.

**Core Operations:**
- **Multi-format PDF text extraction** with PyMuPDF-based content parsing
- **Asynchronous LLM processing** using instructor-enhanced structured output generation
- **Content segmentation** with slide-to-transcript alignment algorithms
- **Persistent storage management** with JSON-serialized speaker profiles
- **Concurrent processing** with asyncio-based parallel execution

**Data Flow Architecture:**
- PDF documents undergo OCR-enhanced text extraction with noise filtering
- Structured prompts guide LLM-based content segmentation using temperature-controlled generation
- Generated sections are validated against presentation slide count constraints
- Speaker profiles are persisted with source file tracking and processing metadata

```mermaid
sequenceDiagram
    participant CLI as CLI Interface
    participant SM as Speaker Manager
    participant SP as Section Producer  
    participant LLM as LLM Service
    participant FS as File System
    
    CLI->>SM: add_speaker(name, files)
    SM->>FS: create_speaker_directory()
    SM->>FS: store_speaker_metadata()
    
    CLI->>SM: process_speaker()
    SM->>SP: generate_sections()
    SP->>SP: extract_pdf_content()
    SP->>LLM: structured_completion()
    LLM-->>SP: section_objects[]
    SP-->>SM: processed_sections[]
    SM->>FS: persist_sections()
    SM-->>CLI: ProcessResult
```

---

## Real-time Presentation Control

The presentation control engine implements a real-time, multi-threaded system that processes continuous audio streams, performs speech-to-text conversion, and executes intelligent content matching to enable seamless voice-controlled presentation navigation.

**Technical Components:**
- **Sherpa-ONNX STT Engine**: High-performance, low-latency speech recognition with transducer architecture
- **Hybrid Similarity Matching**: Weighted combination of semantic embeddings and phonetic similarity scoring
- **Audio Processing Pipeline**: Circular buffer management with configurable frame rates and sample rates
- **Keyboard Automation**: System-level keystroke injection for presentation software control
- **Context-aware Chunking**: Sliding window text segmentation with section boundary optimization

**Processing Architecture:**
- Audio streams are captured at 16kHz with 0.1s frame duration for optimal latency-accuracy balance
- Speech recognition utilizes ONNX-quantized models with greedy search decoding for real-time performance
- Text normalization applies Unicode NFC normalization, emoji removal, and number-to-word conversion
- Similarity calculation combines sentence transformer embeddings (40% weight) with metaphone-based phonetic matching (60% weight)

```mermaid
graph LR
    subgraph "Audio Processing"
        A1[Microphone Input] --> A2[Audio Queue]
        A2 --> A3[STT Engine]
        A3 --> A4[Text Normalization]
    end
    
    subgraph "Content Matching"
        B1[Chunk Producer] --> B2[Candidate Selection]
        B2 --> B3[Similarity Calculator]
        B3 --> B4[Score Normalization]
    end
    
    subgraph "Navigation Control"
        C1[Section Matching] --> C2[Keyboard Controller]
        C2 --> C3[Presentation Software]
    end
    
    A4 --> B2
    B4 --> C1
```

---

## Configuration Management

The settings subsystem implements a hierarchical configuration architecture with template-driven defaults and user-specific overrides, supporting dynamic reconfiguration of LLM endpoints, API credentials, and system parameters.

**Configuration Hierarchy:**
- **Template Layer**: Default settings with type validation and constraint definition
- **User Layer**: Persistent overrides with YAML serialization and atomic updates  
- **Runtime Layer**: In-memory configuration cache with lazy loading optimization

**Managed Settings:**
- **LLM Configuration**: Model selection, API endpoint configuration, temperature parameters
- **API Credentials**: Secure key management with environment variable fallback
- **Processing Parameters**: Chunk window sizes, similarity thresholds, audio settings

```mermaid
flowchart TD
    A[Settings Request] --> B{Settings Exist?}
    B -->|No| C[Load Template]
    B -->|Yes| D[Load User Config]
    C --> E[Merge with Defaults]
    D --> E
    E --> F[Validate Configuration]
    F --> G[Runtime Settings Cache]
    G --> H[Application Components]
    
    I[Settings Update] --> J[Validate Input]
    J --> K[Update User Config] 
    K --> L[Atomic YAML Write]
    L --> M[Refresh Cache]
    M --> G
```

---

## Advanced AI/ML Integration

### Large Language Model Pipeline

The LLM integration employs instructor-enhanced structured output generation with Pydantic model validation for reliable content segmentation:

**Implementation Details:**
- **LiteLLM Integration**: Multi-provider LLM support with unified API interface
- **Structured Output**: Instructor-based response parsing with JSON mode validation
- **Content Alignment**: Slide-to-transcript mapping with semantic coherence constraints
- **Error Handling**: Comprehensive retry logic with exponential backoff and circuit breaker patterns

### Semantic Similarity Engine  

The similarity calculation system combines multiple similarity metrics through a weighted scoring architecture:

**Semantic Component (40% weight):**
- Sentence transformer embeddings with normalized cosine similarity
- Pre-trained multilingual models for cross-language support
- Batch processing optimization for candidate comparison

**Phonetic Component (60% weight):**
- Metaphone phonetic encoding with fuzzy string matching
- RapidFuzz-based edit distance calculation with configurable thresholds
- LRU caching for phonetic code optimization

### Speech-to-Text Processing

**Sherpa-ONNX Architecture:**
- Transducer-based neural network architecture with encoder-decoder-joiner components
- INT8 quantization for optimal inference performance
- Streaming recognition with configurable beam search parameters
- Multi-threaded processing with lock-free audio queue management
