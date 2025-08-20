# Core Components

## Overview

The Moves system is built around several core components that work together to provide voice-controlled presentation navigation. This document provides a detailed technical overview of each major component, their responsibilities, interfaces, and interactions.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Core Components                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐  │
│  │ SpeakerManager  │    │      PresentationController        │  │
│  │                 │    │                                     │  │
│  │ • Lifecycle     │    │ • Real-time Control                │  │
│  │ • Storage       │◄───┤ • Audio Processing                 │  │
│  │ • Validation    │    │ • Navigation Logic                 │  │
│  └─────────────────┘    └─────────────────────────────────────┘  │
│           │                               │                     │
│           ▼                               ▼                     │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐  │
│  │ SectionProducer │    │      SimilarityCalculator          │  │
│  │                 │    │                                     │  │
│  │ • PDF Extract   │    │ • Content Matching                 │  │
│  │ • LLM Process   │    │ • Multi-modal Similarity           │  │
│  │ • Section Gen   │    │ • Score Normalization              │  │
│  └─────────────────┘    └─────────────────────────────────────┘  │
│                                           │                     │
│                                           ▼                     │
│                          ┌─────────────────────────────────────┐  │
│                          │           ChunkProducer            │  │
│                          │                                     │  │
│                          │ • Text Windowing                   │  │
│                          │ • Candidate Generation             │  │
│                          │ • Context Management               │  │
│                          └─────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## SpeakerManager

The `SpeakerManager` is responsible for the complete lifecycle management of speaker profiles and their associated data.

### Responsibilities

- **Profile Management**: Create, update, delete, and list speaker profiles
- **File Management**: Handle presentation and transcript file storage
- **Processing Coordination**: Orchestrate the content processing pipeline
- **Data Persistence**: Manage JSON serialization and file system operations

### Class Interface

```python
class SpeakerManager:
    def __init__(self):
        self.SPEAKERS_PATH: Path  # ~/.moves/speakers/
    
    # Core CRUD operations
    def add(self, name: str, source_presentation: Path, 
            source_transcript: Path) -> Speaker
    def edit(self, speaker: Speaker, source_presentation: Path | None = None,
             source_transcript: Path | None = None) -> Speaker
    def delete(self, speaker: Speaker) -> bool
    def list(self) -> list[Speaker]
    def resolve(self, speaker_pattern: str) -> Speaker
    
    # Content processing
    def process(self, speakers: list[Speaker], llm_model: str, 
                llm_api_key: str) -> list[ProcessResult]
```

### Key Methods

#### `add()` - Speaker Creation
```python
def add(self, name: str, source_presentation: Path, source_transcript: Path) -> Speaker:
    # Validates input files exist
    # Generates unique speaker ID using name
    # Creates speaker directory structure
    # Persists speaker metadata as JSON
    # Returns Speaker object
```

**Validation Logic:**
- Ensures presentation and transcript files exist
- Prevents duplicate names that conflict with existing speaker IDs
- Creates unique ID using `id_generator.generate_speaker_id(name)`

#### `resolve()` - Speaker Lookup
```python  
def resolve(self, speaker_pattern: str) -> Speaker:
    # Supports lookup by ID (exact match)
    # Supports lookup by name (with disambiguation)
    # Handles multiple matches gracefully
    # Raises descriptive errors for no matches
```

**Resolution Strategy:**
1. **Exact ID Match**: Return immediately if pattern matches speaker ID
2. **Name Match**: Search by speaker name
3. **Disambiguation**: Handle multiple name matches with clear error messages

#### `process()` - Asynchronous Processing
```python
async def process(self, speakers: list[Speaker], llm_model: str, 
                  llm_api_key: str) -> list[ProcessResult]:
    # Validates all speaker files exist (source or local copies)
    # Copies files to local speaker directories  
    # Processes speakers concurrently using asyncio
    # Generates sections using SectionProducer
    # Stores results as sections.json
    # Returns processing statistics
```

**File Management Strategy:**
- **Source Priority**: Uses original source files if available
- **Local Fallback**: Falls back to local copies if source unavailable  
- **Atomic Operations**: Ensures file operations are atomic
- **Error Recovery**: Graceful handling of file system errors

### Storage Schema

Each speaker creates this directory structure:
```
~/.moves/speakers/{speaker_id}/
├── speaker.json          # Speaker metadata
├── presentation.pdf      # Local copy of presentation
├── transcript.pdf        # Local copy of transcript  
└── sections.json         # Generated sections (after processing)
```

**speaker.json Format:**
```json
{
    "name": "John Smith",
    "speaker_id": "john_smith_a1b2", 
    "source_presentation": "/path/to/original/presentation.pdf",
    "source_transcript": "/path/to/original/transcript.pdf"
}
```

## PresentationController

The `PresentationController` is the central orchestrator for real-time presentation control, managing audio input, speech recognition, similarity matching, and slide navigation.

### Responsibilities

- **Audio Processing**: Real-time microphone input and speech recognition
- **Content Matching**: Compare spoken words against expected content
- **Navigation Control**: Trigger slide transitions based on voice input
- **Manual Override**: Handle keyboard controls for manual navigation
- **Threading Coordination**: Manage multiple concurrent processing threads

### Class Interface

```python
class PresentationController:
    def __init__(self, sections: list[Section], start_section: Section, 
                 window_size: int = 12):
        # Configuration
        self.sections: list[Section]
        self.current_section: Section
        self.window_size: int
        
        # Processing components
        self.similarity_calculator: SimilarityCalculator
        self.chunks: list[Chunk]
        self.recent_words: deque[str]
        
        # Audio and recognition
        self.recognizer: OnlineRecognizer
        self.stream: OnlineStream
        self.audio_queue: deque
        
        # Threading and control
        self.shutdown_flag: threading.Event
        self.navigator_working: bool
        self.paused: bool
    
    def control(self) -> None         # Main control loop
    def process_audio(self) -> None   # Audio processing thread
    def navigate_presentation(self) -> None  # Navigation thread
```

### Threading Architecture

The controller uses a multi-threaded architecture for real-time performance:

#### Thread Responsibilities

1. **Main Thread**: Audio input stream management and coordination
2. **Audio Processing Thread**: Speech recognition and word buffer management  
3. **Navigation Thread**: Similarity calculation and slide navigation
4. **Keyboard Listener Thread**: Manual control input handling

#### Thread Communication

```python
# Shared data structures
self.audio_queue: deque[np.ndarray]      # Audio frames (thread-safe)
self.recent_words: deque[str]            # Recognized words (thread-safe)
self.shutdown_flag: threading.Event      # Coordination signal
```

### Key Methods

#### `control()` - Main Control Loop
```python
def control(self):
    # Starts all processing threads
    # Sets up audio input stream with sounddevice
    # Manages main event loop
    # Handles graceful shutdown and cleanup
```

**Audio Stream Configuration:**
- **Sample Rate**: 16kHz (optimized for speech recognition)
- **Frame Duration**: 100ms (low latency)
- **Channels**: Mono (single microphone input)
- **Buffer**: Circular queue with maxlen=5

#### `process_audio()` - Speech Recognition
```python
def process_audio(self):
    # Continuously processes audio frames from queue
    # Feeds audio to Sherpa-ONNX recognition stream
    # Extracts recognized words and updates word buffer
    # Handles recognition errors gracefully
```

**Recognition Pipeline:**
1. **Audio Frame Processing**: Convert sounddevice input to recognizer format
2. **Stream Processing**: Feed frames to Sherpa-ONNX stream
3. **Word Extraction**: Extract complete words from recognition results
4. **Buffer Management**: Maintain sliding window of recent words

#### `navigate_presentation()` - Content Matching
```python
def navigate_presentation(self):
    # Monitors word buffer for changes
    # Generates candidate chunks for current section
    # Calculates similarity scores for recent speech
    # Triggers navigation when confidence threshold met
```

**Navigation Logic:**
1. **Change Detection**: Monitor word buffer for new content
2. **Candidate Generation**: Create text chunks around current section
3. **Similarity Calculation**: Compare speech against candidates
4. **Threshold Evaluation**: Navigate when similarity exceeds threshold
5. **State Management**: Update current section and handle transitions

### Keyboard Controls

Manual override system using pynput:

```python
self.keyboard_listener = Listener(on_press=self._on_key_press)

def _on_key_press(self, key):
    if key == Key.right:      # Next section
        self._next_section()
    elif key == Key.left:     # Previous section  
        self._prev_section()
    elif key == Key.insert:   # Pause/Resume
        self._toggle_pause()
```

## SectionProducer

The `SectionProducer` handles the conversion of raw presentation and transcript PDFs into synchronized content sections using Large Language Model processing.

### Responsibilities

- **PDF Text Extraction**: Extract clean text from presentation and transcript files
- **LLM Integration**: Send content to language model for processing
- **Section Generation**: Create synchronized sections matching slides to transcript
- **Data Serialization**: Convert between Section objects and JSON storage format

### Class Interface

```python
# Core functions (module-level)
def generate_sections(presentation_path: Path, transcript_path: Path, 
                     llm_model: str, llm_api_key: str) -> list[Section]

def convert_to_list(section_objects: list[Section]) -> list[dict[str, str | int]]
def convert_to_objects(section_list: list[dict[str, str | int]]) -> list[Section]

# Internal functions
def _extract_pdf(pdf_path: Path, extraction_type: Literal["transcript", "presentation"]) -> str
def _call_llm(presentation_data: str, transcript_data: str, 
              llm_model: str, llm_api_key: str) -> list[str]
```

### PDF Extraction Process

#### Presentation Extraction
```python
def _extract_pdf(pdf_path: Path, extraction_type: "presentation") -> str:
    # Processes each page as separate slide
    # Creates markdown-formatted output
    # Generates "# Slide Page {n}" headers
    # Returns concatenated slide content
```

**Output Format:**
```markdown
# Slide Page 0
Introduction to Machine Learning Overview of concepts...

# Slide Page 1  
What is Machine Learning? Definition and core principles...
```

#### Transcript Extraction
```python
def _extract_pdf(pdf_path: Path, extraction_type: "transcript") -> str:
    # Extracts continuous text from all pages
    # Normalizes whitespace and formatting
    # Returns single string with full transcript
```

### LLM Integration

#### Request Structure
```python
class SectionsOutputModel(BaseModel):
    class SectionItem(BaseModel):
        section_index: int = Field(..., ge=0, description="Index starting from 0")
        content: str = Field(..., description="Content of the section")
    
    sections: list[SectionItem] = Field(
        ..., 
        description="List of section items, one for each slide",
        min_items=len(presentation_data.split("\n\n")),
        max_items=len(presentation_data.split("\n\n"))
    )
```

#### Processing Pipeline
```python
def _call_llm(presentation_data: str, transcript_data: str, 
              llm_model: str, llm_api_key: str) -> list[str]:
    # Loads instruction template from llm_instruction.md
    # Creates structured prompt with presentation and transcript
    # Calls LLM with strict response model validation
    # Extracts content strings from response
    # Returns list of section content
```

**LLM Provider Support:**
- Uses **LiteLLM** for multi-provider support
- Supports OpenAI, Anthropic, Google, Azure, AWS Bedrock, and others
- Handles authentication and rate limiting automatically

### Section Generation Logic

The LLM follows these constraints (from `llm_instruction.md`):

1. **One-to-One Mapping**: Exactly one section per slide
2. **Transcript Authority**: All content sourced from transcript
3. **Language Consistency**: Output matches transcript language
4. **Content Hierarchy**: 
   - Primary: Extract relevant transcript passages
   - Fallback: Synthesize missing content in transcript style

## SimilarityCalculator

The `SimilarityCalculator` combines multiple similarity metrics to robustly match spoken content against expected presentation content.

### Responsibilities

- **Multi-Modal Matching**: Combine semantic and phonetic similarity
- **Score Normalization**: Ensure fair comparison between different metrics
- **Weighted Combination**: Apply configurable weights to different similarity types
- **Performance Optimization**: Cache calculations and optimize for real-time use

### Class Interface

```python
class SimilarityCalculator:
    def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
        self.semantic_weight: float
        self.phonetic_weight: float
        self.semantic: Semantic        # Semantic similarity engine
        self.phonetic: Phonetic        # Phonetic similarity engine
    
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]
    def _normalize_scores_simple(self, results: list[SimilarityResult]) -> dict[int, float]
```

### Similarity Engines

#### Semantic Engine
```python
class Semantic:
    def __init__(self):
        self.model = SentenceTransformer("src/core/components/ml_models/embedding")
    
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        # Generates embeddings for input and all candidates
        # Calculates cosine similarity between embeddings  
        # Returns sorted results by similarity score
```

**Semantic Similarity Features:**
- **Model**: Pre-trained sentence transformer model
- **Embeddings**: High-dimensional vector representations
- **Similarity Metric**: Cosine similarity between normalized embeddings
- **Batch Processing**: Efficient embedding generation for multiple candidates

#### Phonetic Engine  
```python
class Phonetic:
    @staticmethod
    @lru_cache(maxsize=350)
    def _get_phonetic_code(text: str) -> str:
        return metaphone(text).replace(" ", "")
    
    @staticmethod 
    @lru_cache(maxsize=350)
    def _calculate_fuzz_ratio(code1: str, code2: str) -> float:
        return fuzz.ratio(code1, code2) / 100.0
```

**Phonetic Similarity Features:**
- **Algorithm**: Double Metaphone phonetic algorithm
- **Fuzzy Matching**: RapidFuzz ratio for phonetic code comparison
- **Caching**: LRU cache for performance optimization
- **Error Tolerance**: Handles speech recognition errors

### Similarity Combination

#### Score Normalization
```python  
def _normalize_scores_simple(self, results: list[SimilarityResult]) -> dict[int, float]:
    # Simple min-max normalization
    # Ensures scores are comparable across similarity types
    # Returns normalized scores by candidate ID
```

#### Weighted Combination
```python
def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
    # Calculate both semantic and phonetic similarities
    # Normalize scores for fair comparison
    # Apply weighted combination: 
    #   final_score = semantic_weight * sem_score + phonetic_weight * pho_score
    # Return sorted results by combined score
```

**Default Weights:**
- **Semantic Weight**: 0.4 (40%) - Meaning-based matching
- **Phonetic Weight**: 0.6 (60%) - Sound-based matching (handles speech errors)

## ChunkProducer  

The `ChunkProducer` creates sliding windows of text content that enable context-aware similarity matching for presentation navigation.

### Responsibilities

- **Text Windowing**: Create overlapping windows of words from sections
- **Context Preservation**: Maintain section boundary information
- **Candidate Generation**: Produce relevant chunks for current presentation position
- **Performance Optimization**: Generate chunks efficiently for real-time use

### Class Interface

```python
def generate_chunks(sections: list[Section], window_size: int = 12) -> list[Chunk]
def get_candidate_chunks(current_section: Section, all_chunks: list[Chunk]) -> list[Chunk]
```

### Chunk Generation Process

#### Windowing Algorithm
```python
def generate_chunks(sections: list[Section], window_size: int = 12) -> list[Chunk]:
    # 1. Flatten all section words with source tracking
    words_with_sources = [
        (word, section) for section in sections for word in section.content.split()
    ]
    
    # 2. Create sliding windows of specified size
    for i in range(len(words_with_sources) - window_size + 1):
        window_words = words_with_sources[i:i + window_size]
        
        # 3. Generate chunk with normalized content and source references
        chunk = Chunk(
            partial_content=normalize_text(" ".join(word for word, _ in window_words)),
            source_sections=sorted(set(section for _, section in window_words), 
                                  key=lambda s: s.section_index)
        )
```

**Chunking Features:**
- **Overlapping Windows**: Each chunk overlaps with adjacent chunks
- **Source Tracking**: Maintains references to originating sections
- **Text Normalization**: Applies consistent text preprocessing
- **Variable Size**: Configurable window size (default: 12 words)

#### Candidate Selection
```python
def get_candidate_chunks(current_section: Section, all_chunks: list[Chunk]) -> list[Chunk]:
    # Returns chunks that contain or are near the current section
    # Provides context for similarity matching
    # Optimizes by filtering relevant chunks only
```

### Performance Characteristics

- **Time Complexity**: O(n * w) where n = total words, w = window size
- **Space Complexity**: O(n) storage for all generated chunks
- **Cache Friendly**: Chunks generated once and reused throughout presentation
- **Context Aware**: Preserves section boundaries and transitions

## Component Integration

### Data Flow Between Components

1. **SpeakerManager** → **SectionProducer**: Triggers content processing
2. **SectionProducer** → **ChunkProducer**: Provides sections for chunking  
3. **PresentationController** → **ChunkProducer**: Gets candidate chunks
4. **PresentationController** → **SimilarityCalculator**: Performs content matching
5. **SimilarityCalculator** → **Similarity Engines**: Delegates to specialized engines

### Error Handling Strategy

Each component implements robust error handling:

- **Validation**: Input validation with descriptive error messages
- **Graceful Degradation**: Continue operation when non-critical components fail
- **Error Propagation**: Meaningful error messages bubble up through call stack
- **Recovery**: Automatic retry for transient failures where appropriate

### Performance Optimization

- **Caching**: LRU caches in phonetic similarity calculations
- **Lazy Loading**: Models loaded on first use
- **Batch Processing**: Efficient batch operations where possible
- **Resource Management**: Proper cleanup of threads and system resources

This comprehensive overview of core components provides the technical foundation for understanding how Moves achieves robust, real-time presentation control through voice recognition and AI-powered content matching.