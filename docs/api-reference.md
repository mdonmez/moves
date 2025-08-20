# API Reference

## Overview

This document provides comprehensive API documentation for all public interfaces, classes, methods, and functions in the Moves system. It serves as a reference for developers who want to understand, extend, or integrate with the Moves codebase.

## Module Structure

```
src/
├── core/                          # Core system components
│   ├── components/                # Individual processing components
│   │   ├── chunk_producer.py      # Text windowing and chunk generation
│   │   ├── section_producer.py    # LLM-powered section generation
│   │   ├── similarity_calculator.py # Multi-modal similarity matching
│   │   └── similarity_units/      # Similarity engine implementations
│   │       ├── semantic.py        # Semantic similarity using embeddings
│   │       └── phonetic.py        # Phonetic similarity using metaphone
│   ├── presentation_controller.py # Main presentation control orchestrator
│   ├── speaker_manager.py         # Speaker lifecycle and data management
│   └── settings_editor.py         # Configuration management
├── data/
│   └── models.py                  # Data model definitions
└── utils/                         # Utility functions
    ├── data_handler.py            # File system operations
    ├── id_generator.py            # Unique ID generation
    ├── logger.py                  # Logging utilities
    └── text_normalizer.py         # Text preprocessing
```

## Data Models (`src/data/models.py`)

### Section

Represents a single content section aligned with a presentation slide.

```python
@dataclass(frozen=True)
class Section:
    """
    A content section corresponding to a presentation slide
    
    Attributes:
        content: The text content for this section
        section_index: Zero-based index position in presentation
    """
    content: str
    section_index: int
```

**Usage Example:**
```python
section = Section(
    content="Introduction to machine learning concepts and applications",
    section_index=0
)
```

### Chunk

Represents a sliding window of text content with source section references.

```python
@dataclass(frozen=True)
class Chunk:
    """
    A sliding window of text content for similarity matching
    
    Attributes:
        partial_content: The windowed text content (normalized)
        source_sections: List of sections that contribute to this chunk
    """
    partial_content: str
    source_sections: list["Section"]
```

**Usage Example:**
```python
chunk = Chunk(
    partial_content="machine learning algorithms enable systems to learn",
    source_sections=[section1, section2]
)
```

### Speaker

Represents a speaker profile with associated presentation materials.

```python
@dataclass
class Speaker:
    """
    Speaker profile with presentation materials
    
    Attributes:
        name: Display name of the speaker
        speaker_id: Unique identifier (generated from name)
        source_presentation: Path to original presentation PDF
        source_transcript: Path to original transcript PDF
    """
    name: str
    speaker_id: SpeakerId  # Type alias for str
    source_presentation: Path
    source_transcript: Path
```

**Usage Example:**
```python
speaker = Speaker(
    name="John Smith",
    speaker_id="john_smith_a1b2",
    source_presentation=Path("/path/to/presentation.pdf"),
    source_transcript=Path("/path/to/transcript.pdf")
)
```

### SimilarityResult

Represents the result of similarity calculation between input and candidate content.

```python
@dataclass(frozen=True)
class SimilarityResult:
    """
    Result of similarity calculation
    
    Attributes:
        chunk: The candidate chunk that was compared
        score: Similarity score (0.0 to 1.0, higher is more similar)
    """
    chunk: Chunk
    score: float
```

### Settings

Represents system configuration settings.

```python
@dataclass
class Settings:
    """
    System configuration settings
    
    Attributes:
        model: LLM model identifier (e.g., "openai/gpt-4")
        key: API key for the LLM provider
    """
    model: str
    key: str
```

### ProcessResult

Represents the result of speaker content processing.

```python
@dataclass(frozen=True)
class ProcessResult:
    """
    Result of speaker processing operation
    
    Attributes:
        section_count: Number of sections generated
        transcript_from: Source of transcript ("SOURCE" or "LOCAL")
        presentation_from: Source of presentation ("SOURCE" or "LOCAL")
    """
    section_count: int
    transcript_from: Literal["SOURCE", "LOCAL"]
    presentation_from: Literal["SOURCE", "LOCAL"]
```

## Core Components

### SpeakerManager (`src/core/speaker_manager.py`)

Manages the complete lifecycle of speaker profiles and their associated data.

#### Class Definition

```python
class SpeakerManager:
    """
    Manages speaker profiles, processing, and data storage
    """
    
    def __init__(self):
        """
        Initialize SpeakerManager with data directory path
        
        Attributes:
            SPEAKERS_PATH: Path to speakers data directory (~/.moves/speakers/)
        """
```

#### Methods

##### `add(name: str, source_presentation: Path, source_transcript: Path) -> Speaker`

Creates a new speaker profile with presentation materials.

**Parameters:**
- `name`: Display name for the speaker
- `source_presentation`: Path to presentation PDF file
- `source_transcript`: Path to transcript PDF file

**Returns:**
- `Speaker`: Created speaker object

**Raises:**
- `ValueError`: If name conflicts with existing speaker ID or files don't exist
- `RuntimeError`: If file operations fail

**Example:**
```python
manager = SpeakerManager()
speaker = manager.add(
    "Jane Doe",
    Path("presentation.pdf"),
    Path("transcript.pdf")
)
```

##### `edit(speaker: Speaker, source_presentation: Path | None = None, source_transcript: Path | None = None) -> Speaker`

Updates speaker's source files.

**Parameters:**
- `speaker`: Speaker object to update
- `source_presentation`: New presentation file path (optional)
- `source_transcript`: New transcript file path (optional)

**Returns:**
- `Speaker`: Updated speaker object

**Example:**
```python
updated_speaker = manager.edit(
    speaker,
    source_presentation=Path("new_presentation.pdf")
)
```

##### `resolve(speaker_pattern: str) -> Speaker`

Resolves speaker by name or ID with intelligent matching.

**Parameters:**
- `speaker_pattern`: Speaker name or ID to resolve

**Returns:**
- `Speaker`: Matched speaker object

**Raises:**
- `ValueError`: If no match found or multiple ambiguous matches

**Example:**
```python
# By exact ID
speaker = manager.resolve("john_smith_a1b2")

# By name
speaker = manager.resolve("John Smith")
```

##### `process(speakers: list[Speaker], llm_model: str, llm_api_key: str) -> list[ProcessResult]`

Processes speakers concurrently to generate content sections.

**Parameters:**
- `speakers`: List of speakers to process
- `llm_model`: LLM model identifier
- `llm_api_key`: API key for LLM provider

**Returns:**
- `list[ProcessResult]`: Processing results for each speaker

**Raises:**
- `FileNotFoundError`: If required files are missing
- `RuntimeError`: If LLM processing fails

**Example:**
```python
results = manager.process(
    [speaker1, speaker2],
    "openai/gpt-4",
    "sk-api-key"
)
```

##### `delete(speaker: Speaker) -> bool`

Removes speaker and all associated data.

**Parameters:**
- `speaker`: Speaker object to delete

**Returns:**
- `bool`: True if deletion successful

**Example:**
```python
success = manager.delete(speaker)
```

##### `list() -> list[Speaker]`

Lists all registered speakers.

**Returns:**
- `list[Speaker]`: All registered speaker objects

**Example:**
```python
all_speakers = manager.list()
```

### PresentationController (`src/core/presentation_controller.py`)

Main orchestrator for real-time presentation control and voice recognition.

#### Class Definition

```python
class PresentationController:
    """
    Manages real-time presentation control with voice navigation
    """
    
    def __init__(self, sections: list[Section], start_section: Section, window_size: int = 12):
        """
        Initialize presentation controller
        
        Parameters:
            sections: List of presentation sections
            start_section: Initial section to start from
            window_size: Size of sliding word window for matching
        """
```

#### Methods

##### `control() -> None`

Starts the main control loop for voice-controlled presentation.

**Description:**
- Initializes audio processing threads
- Sets up speech recognition
- Manages keyboard listeners
- Handles graceful shutdown

**Example:**
```python
controller = PresentationController(sections, start_section)
controller.control()  # Blocks until stopped
```

##### `process_audio() -> None`

Audio processing thread function (internal method).

**Description:**
- Processes audio frames from microphone
- Performs speech recognition
- Updates word buffer with recognized text

##### `navigate_presentation() -> None`

Navigation thread function (internal method).

**Description:**
- Monitors word buffer for changes
- Calculates similarity with candidate chunks
- Triggers slide navigation based on matches

### SectionProducer (`src/core/components/section_producer.py`)

Handles PDF processing and LLM-powered section generation.

#### Functions

##### `generate_sections(presentation_path: Path, transcript_path: Path, llm_model: str, llm_api_key: str) -> list[Section]`

Generates synchronized presentation sections using AI.

**Parameters:**
- `presentation_path`: Path to presentation PDF
- `transcript_path`: Path to transcript PDF  
- `llm_model`: LLM model identifier
- `llm_api_key`: API key for LLM provider

**Returns:**
- `list[Section]`: Generated section objects

**Raises:**
- `RuntimeError`: If PDF extraction or LLM processing fails

**Example:**
```python
sections = generate_sections(
    Path("slides.pdf"),
    Path("script.pdf"),
    "openai/gpt-4",
    "sk-api-key"
)
```

##### `convert_to_list(section_objects: list[Section]) -> list[dict[str, str | int]]`

Converts Section objects to JSON-serializable format.

**Parameters:**
- `section_objects`: List of Section objects

**Returns:**
- `list[dict]`: JSON-serializable section data

**Example:**
```python
json_data = convert_to_list(sections)
```

##### `convert_to_objects(section_list: list[dict[str, str | int]]) -> list[Section]`

Converts JSON data back to Section objects.

**Parameters:**
- `section_list`: JSON-serializable section data

**Returns:**
- `list[Section]`: Section objects

**Example:**
```python
sections = convert_to_objects(json_data)
```

### SimilarityCalculator (`src/core/components/similarity_calculator.py`)

Multi-modal similarity calculation combining semantic and phonetic matching.

#### Class Definition

```python
class SimilarityCalculator:
    """
    Combines semantic and phonetic similarity for robust content matching
    """
    
    def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
        """
        Initialize similarity calculator with weighted combination
        
        Parameters:
            semantic_weight: Weight for semantic similarity (0.0-1.0)
            phonetic_weight: Weight for phonetic similarity (0.0-1.0)
        """
```

#### Methods

##### `compare(input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]`

Compares input text against candidate chunks using multi-modal similarity.

**Parameters:**
- `input_str`: Input text to match against
- `candidates`: List of candidate chunks to compare

**Returns:**
- `list[SimilarityResult]`: Results sorted by similarity score (descending)

**Raises:**
- `RuntimeError`: If similarity calculation fails

**Example:**
```python
calculator = SimilarityCalculator()
results = calculator.compare("machine learning", candidate_chunks)
best_match = results[0] if results else None
```

### ChunkProducer (`src/core/components/chunk_producer.py`)

Generates sliding window chunks from presentation sections.

#### Functions

##### `generate_chunks(sections: list[Section], window_size: int = 12) -> list[Chunk]`

Creates overlapping text chunks from sections for similarity matching.

**Parameters:**
- `sections`: List of presentation sections
- `window_size`: Number of words per chunk window

**Returns:**
- `list[Chunk]`: Generated chunk objects

**Example:**
```python
chunks = generate_chunks(sections, window_size=12)
```

##### `get_candidate_chunks(current_section: Section, all_chunks: list[Chunk]) -> list[Chunk]`

Filters chunks relevant to current presentation position.

**Parameters:**
- `current_section`: Current presentation section
- `all_chunks`: All available chunks

**Returns:**
- `list[Chunk]`: Relevant candidate chunks

**Example:**
```python
candidates = get_candidate_chunks(current_section, all_chunks)
```

### Similarity Engines

#### Semantic (`src/core/components/similarity_units/semantic.py`)

Semantic similarity using sentence transformers and embeddings.

```python
class Semantic:
    """
    Semantic similarity using pre-trained embedding models
    """
    
    def __init__(self):
        """Initialize with sentence transformer model"""
        
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        """
        Calculate semantic similarity using embeddings
        
        Parameters:
            input_str: Input text to match
            candidates: Candidate chunks to compare against
            
        Returns:
            list[SimilarityResult]: Results sorted by similarity
        """
```

#### Phonetic (`src/core/components/similarity_units/phonetic.py`)

Phonetic similarity using metaphone algorithm and fuzzy matching.

```python
class Phonetic:
    """
    Phonetic similarity using metaphone codes and fuzzy string matching
    """
    
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        """
        Calculate phonetic similarity using metaphone codes
        
        Parameters:
            input_str: Input text to match
            candidates: Candidate chunks to compare against
            
        Returns:
            list[SimilarityResult]: Results sorted by similarity
        """
    
    @staticmethod
    @lru_cache(maxsize=350)
    def _get_phonetic_code(text: str) -> str:
        """
        Get cached phonetic code for text
        
        Parameters:
            text: Input text
            
        Returns:
            str: Metaphone phonetic code
        """
```

## Utility Modules

### DataHandler (`src/utils/data_handler.py`)

File system operations for the Moves data directory.

#### Constants

```python
DATA_FOLDER: Path  # ~/.moves/ directory
```

#### Functions

##### `write(path: Path, data: str) -> bool`

Writes text data to file in data directory.

**Parameters:**
- `path`: Relative path within data directory
- `data`: Text data to write

**Returns:**
- `bool`: True if successful

**Raises:**
- `RuntimeError`: If write operation fails

##### `read(path: Path) -> str`

Reads text data from file in data directory.

**Parameters:**
- `path`: Relative path within data directory

**Returns:**
- `str`: File contents

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `RuntimeError`: If read operation fails

##### `list(path: Path) -> list[Path]`

Lists directory contents.

**Parameters:**
- `path`: Relative directory path

**Returns:**
- `list[Path]`: Directory contents (sorted)

##### `delete(path: Path) -> bool`

Deletes file or directory.

**Parameters:**
- `path`: Relative path to delete

**Returns:**
- `bool`: True if successful

**Raises:**
- `FileNotFoundError`: If path doesn't exist
- `RuntimeError`: If deletion fails

##### `copy(source: Path, target: Path) -> bool`

Copies file or directory.

**Parameters:**
- `source`: Source path (can be external or within data directory)
- `target`: Target path within data directory

**Returns:**
- `bool`: True if successful

**Raises:**
- `FileNotFoundError`: If source doesn't exist
- `RuntimeError`: If copy operation fails

### TextNormalizer (`src/utils/text_normalizer.py`)

Text preprocessing for consistent similarity matching.

#### Functions

##### `normalize_text(text: str) -> str`

Applies comprehensive text normalization.

**Parameters:**
- `text`: Input text to normalize

**Returns:**
- `str`: Normalized text

**Normalization Steps:**
1. Unicode normalization (NFC)
2. Lowercase conversion
3. Emoji removal
4. Quote mark standardization
5. Number-to-words conversion
6. Punctuation removal (except quotes, apostrophes)
7. Whitespace normalization

**Example:**
```python
normalized = normalize_text("Hello! AI's 123 features… 😊")
# Result: "hello ai's one hundred twenty three features"
```

### IDGenerator (`src/utils/id_generator.py`)

Unique identifier generation for speakers and other entities.

#### Functions

##### `generate_speaker_id(name: str) -> str`

Generates unique speaker ID from name.

**Parameters:**
- `name`: Speaker's display name

**Returns:**
- `str`: Unique speaker ID

**Algorithm:**
- Converts name to lowercase
- Replaces spaces with underscores
- Removes special characters
- Appends random suffix for uniqueness

**Example:**
```python
speaker_id = generate_speaker_id("John Smith")
# Result: "john_smith_a1b2"
```

### SettingsEditor (`src/core/settings_editor.py`)

Configuration management with template-based defaults.

#### Class Definition

```python
class SettingsEditor:
    """
    Manages system configuration with template defaults
    """
    
    def __init__(self):
        """
        Initialize settings editor
        
        Attributes:
            template: Path to settings template
            settings: Path to user settings file
            template_data: Template configuration data
        """
```

#### Methods

##### `set(key: str, value: str) -> bool`

Updates configuration setting.

**Parameters:**
- `key`: Setting key to update
- `value`: New setting value

**Returns:**
- `bool`: True if successful

**Raises:**
- `RuntimeError`: If save operation fails

##### `unset(key: str) -> bool`

Resets setting to template default.

**Parameters:**
- `key`: Setting key to reset

**Returns:**
- `bool`: True if successful

**Raises:**
- `RuntimeError`: If save operation fails

##### `list() -> Settings`

Gets current configuration.

**Returns:**
- `Settings`: Current settings object

## Error Handling

### Exception Hierarchy

The Moves system uses Python's built-in exceptions with descriptive messages:

#### Common Exceptions

- **`ValueError`**: Invalid input parameters or data
- **`FileNotFoundError`**: Missing files or directories
- **`RuntimeError`**: System operation failures
- **`ConnectionError`**: Network or API connectivity issues

#### Error Message Format

All error messages follow a consistent format:
```
{Operation} failed for {context}: {specific_error}
```

**Examples:**
```python
# File operations
raise RuntimeError("PDF extraction failed for presentation.pdf (presentation): Invalid PDF format")

# API operations  
raise RuntimeError("LLM call failed: Authentication error - invalid API key")

# Data operations
raise ValueError("No speaker found matching 'john_doe'")
```

### Error Recovery

#### Graceful Degradation

The system continues operating when possible:

```python
try:
    semantic_results = self.semantic.compare(input_str, candidates)
    phonetic_results = self.phonetic.compare(input_str, candidates) 
    return combined_results
except SemanticError:
    # Fall back to phonetic-only
    return self.phonetic.compare(input_str, candidates)
except PhoneticError:
    # Fall back to semantic-only
    return self.semantic.compare(input_str, candidates)
```

#### Resource Cleanup

All components ensure proper cleanup:

```python
def cleanup(self):
    """Cleanup system resources"""
    self.shutdown_flag.set()
    
    # Wait for threads
    if self.audio_thread.is_alive():
        self.audio_thread.join(timeout=1.0)
    
    # Close streams
    if hasattr(self, 'stream'):
        self.recognizer.reset(self.stream)
```

## Type Hints and Validation

### Type Aliases

```python
SpeakerId = str  # Unique speaker identifier
HistoryId = str  # History entry identifier
```

### Generic Types

```python
from typing import Literal, Union, Optional, List, Dict, Any

# Literal types for constants
ExtractType = Literal["transcript", "presentation"]
SourceType = Literal["SOURCE", "LOCAL"]

# Union types for flexible parameters  
PathLike = Union[str, Path]
OptionalPath = Optional[Path]
```

### Runtime Validation

```python
from pydantic import BaseModel, Field, validator

class SectionItem(BaseModel):
    section_index: int = Field(..., ge=0, description="Index starting from 0")
    content: str = Field(..., min_length=1, description="Section content")
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v
```

This comprehensive API reference provides detailed documentation for all public interfaces in the Moves system, enabling developers to effectively use, extend, and integrate with the codebase.