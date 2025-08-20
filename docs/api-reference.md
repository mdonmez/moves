# API Reference

This document provides a comprehensive reference for all public APIs, interfaces, and classes in the Moves application. These APIs enable integration with external tools and facilitate extension of the system.

## Table of Contents

- [Overview](#overview)
- [Core APIs](#core-apis)
- [Data Models](#data-models)
- [Component APIs](#component-apis)
- [Utility APIs](#utility-apis)
- [Configuration APIs](#configuration-apis)
- [Error Classes](#error-classes)
- [Type Definitions](#type-definitions)
- [Constants](#constants)

## Overview

The Moves API is designed with modularity and extensibility in mind. All public interfaces follow consistent patterns and provide clear separation of concerns.

**API Design Principles**:

- **Immutability**: Data structures are immutable where possible
- **Type Safety**: Full type hints for all public interfaces
- **Error Handling**: Explicit error types and handling patterns
- **Documentation**: Comprehensive docstrings following Google style
- **Backwards Compatibility**: Semantic versioning for breaking changes

## Core APIs

### PresentationController

**Location**: `src/core/presentation_controller.py`

Main interface for voice-controlled presentation navigation.

#### Class Definition

```python
class PresentationController:
    """Real-time voice-controlled presentation navigation system.

    Provides multi-threaded audio processing with similarity-based navigation
    using both semantic and phonetic matching algorithms.
    """

    def __init__(
        self,
        sections: list[str],
        start_section: int = 0,
        window_size: int = 12
    ) -> None:
        """Initialize presentation controller.

        Args:
            sections: List of presentation section content
            start_section: Starting section index (default: 0)
            window_size: Number of chunks per navigation window (default: 12)

        Raises:
            ValueError: If sections is empty or start_section is invalid
            ModelLoadError: If ML models fail to initialize
        """
```

#### Public Methods

```python
def start_listening(self) -> None:
    """Start voice recognition and navigation system.

    Initializes audio capture, starts processing threads, and begins
    real-time speech recognition for navigation commands.

    Raises:
        AudioError: If audio system initialization fails
        ModelError: If speech recognition models are unavailable
    """

def stop_listening(self) -> None:
    """Stop all processing and clean up resources.

    Gracefully shuts down audio processing threads, cleans up
    ML model resources, and releases audio devices.
    """

def navigate_to_section(self, section_index: int) -> bool:
    """Navigate directly to a specific section.

    Args:
        section_index: Target section index (0-based)

    Returns:
        bool: True if navigation successful, False otherwise

    Raises:
        IndexError: If section_index is out of range
    """

def get_current_section(self) -> int:
    """Get current section index.

    Returns:
        int: Current section index (0-based)
    """

def get_available_sections(self) -> list[str]:
    """Get list of all available sections.

    Returns:
        list[str]: Section content strings
    """

def is_listening(self) -> bool:
    """Check if voice recognition is active.

    Returns:
        bool: True if currently listening, False otherwise
    """

def get_recognition_status(self) -> dict[str, Any]:
    """Get detailed status of recognition system.

    Returns:
        dict: Status information including:
            - listening: Whether system is active
            - current_section: Current section index
            - last_recognition: Last recognized text
            - model_status: ML model health status
            - thread_status: Processing thread status
    """
```

#### Events and Callbacks

```python
def on_section_changed(self, callback: Callable[[int, str], None]) -> None:
    """Register callback for section change events.

    Args:
        callback: Function called with (section_index, section_content)
    """

def on_recognition_result(self, callback: Callable[[str, float], None]) -> None:
    """Register callback for speech recognition results.

    Args:
        callback: Function called with (recognized_text, confidence)
    """

def on_navigation_event(self, callback: Callable[[str, dict], None]) -> None:
    """Register callback for navigation events.

    Args:
        callback: Function called with (event_type, event_data)
    """
```

### SpeakerManager

**Location**: `src/core/speaker_manager.py`

Interface for managing speaker profiles and presentation data.

#### Class Definition

```python
class SpeakerManager:
    """Manages speaker profiles and their associated presentations.

    Provides CRUD operations for speakers, manages presentation data,
    and coordinates AI processing of presentation content.
    """

    def __init__(self) -> None:
        """Initialize speaker manager with default configuration."""
```

#### Public Methods

```python
async def add_speaker(
    self,
    name: str,
    description: str = "",
    pdf_files: list[Path] = None
) -> str:
    """Add new speaker with optional PDF processing.

    Args:
        name: Speaker name
        description: Optional speaker description
        pdf_files: List of PDF file paths to process

    Returns:
        str: Generated speaker ID

    Raises:
        ValueError: If name is empty or invalid
        FileNotFoundError: If PDF files don't exist
        ProcessingError: If PDF processing fails
    """

async def edit_speaker(
    self,
    speaker_id: str,
    name: str = None,
    description: str = None
) -> bool:
    """Update existing speaker information.

    Args:
        speaker_id: Target speaker ID
        name: New speaker name (optional)
        description: New description (optional)

    Returns:
        bool: True if update successful

    Raises:
        SpeakerNotFoundError: If speaker doesn't exist
    """

def list_speakers(self) -> list[SpeakerInfo]:
    """Get list of all speakers.

    Returns:
        list[SpeakerInfo]: Speaker information objects
    """

def get_speaker(self, speaker_id: str) -> SpeakerInfo:
    """Get detailed speaker information.

    Args:
        speaker_id: Target speaker ID

    Returns:
        SpeakerInfo: Complete speaker information

    Raises:
        SpeakerNotFoundError: If speaker doesn't exist
    """

def delete_speaker(self, speaker_id: str) -> bool:
    """Delete speaker and all associated data.

    Args:
        speaker_id: Target speaker ID

    Returns:
        bool: True if deletion successful

    Raises:
        SpeakerNotFoundError: If speaker doesn't exist
    """

async def process_pdfs(
    self,
    speaker_id: str,
    pdf_files: list[Path],
    presentation_id: str = None
) -> str:
    """Process PDF files for a speaker.

    Args:
        speaker_id: Target speaker ID
        pdf_files: List of PDF file paths
        presentation_id: Optional presentation ID (auto-generated if None)

    Returns:
        str: Presentation ID

    Raises:
        SpeakerNotFoundError: If speaker doesn't exist
        FileNotFoundError: If PDF files don't exist
        ProcessingError: If AI processing fails
    """

def get_presentations(self, speaker_id: str) -> list[PresentationInfo]:
    """Get all presentations for a speaker.

    Args:
        speaker_id: Target speaker ID

    Returns:
        list[PresentationInfo]: Presentation information objects

    Raises:
        SpeakerNotFoundError: If speaker doesn't exist
    """
```

### SettingsEditor

**Location**: `src/core/settings_editor.py`

Interface for configuration management.

#### Class Definition

```python
class SettingsEditor:
    """Template-based configuration management system.

    Manages user settings with validation against a template schema,
    providing type-safe configuration access and modification.
    """

    def __init__(self, template_path: Path = None) -> None:
        """Initialize settings editor.

        Args:
            template_path: Path to settings template (optional)
        """
```

#### Public Methods

```python
def list_settings(self) -> dict[str, Any]:
    """Get all current settings with values and descriptions.

    Returns:
        dict: Settings with structure:
            {
                "setting_name": {
                    "value": current_value,
                    "default": default_value,
                    "description": setting_description,
                    "type": value_type
                }
            }
    """

def get_setting(self, key: str) -> Any:
    """Get specific setting value.

    Args:
        key: Setting key name

    Returns:
        Any: Setting value (with proper type)

    Raises:
        SettingNotFoundError: If setting key doesn't exist
    """

def set_setting(self, key: str, value: Any) -> bool:
    """Set setting value with validation.

    Args:
        key: Setting key name
        value: New setting value

    Returns:
        bool: True if setting was updated

    Raises:
        SettingNotFoundError: If setting key doesn't exist
        ValidationError: If value doesn't match expected type
    """

def unset_setting(self, key: str) -> bool:
    """Reset setting to default value.

    Args:
        key: Setting key name

    Returns:
        bool: True if setting was reset

    Raises:
        SettingNotFoundError: If setting key doesn't exist
    """

def validate_settings(self) -> list[ValidationError]:
    """Validate all current settings against template.

    Returns:
        list[ValidationError]: List of validation errors (empty if valid)
    """

def export_settings(self, file_path: Path) -> None:
    """Export current settings to file.

    Args:
        file_path: Target file path

    Raises:
        PermissionError: If file cannot be written
    """

def import_settings(self, file_path: Path) -> int:
    """Import settings from file.

    Args:
        file_path: Source file path

    Returns:
        int: Number of settings imported

    Raises:
        FileNotFoundError: If file doesn't exist
        ValidationError: If imported settings are invalid
    """
```

## Data Models

### Core Data Structures

#### SpeakerInfo

```python
@dataclass
class SpeakerInfo:
    """Speaker information container.

    Attributes:
        id: Unique speaker identifier
        name: Speaker display name
        description: Optional speaker description
        created_at: Creation timestamp
        updated_at: Last update timestamp
        presentation_count: Number of associated presentations
    """
    id: str
    name: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    presentation_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SpeakerInfo':
        """Create instance from dictionary."""
```

#### PresentationInfo

```python
@dataclass
class PresentationInfo:
    """Presentation information container.

    Attributes:
        id: Unique presentation identifier
        speaker_id: Associated speaker ID
        title: Presentation title
        section_count: Number of sections
        chunk_count: Number of navigation chunks
        created_at: Creation timestamp
        source_files: List of source PDF files
    """
    id: str
    speaker_id: str
    title: str = ""
    section_count: int = 0
    chunk_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    source_files: list[str] = field(default_factory=list)
```

#### Chunk

```python
@dataclass
class Chunk:
    """Navigation chunk container.

    Attributes:
        id: Unique chunk identifier
        section_index: Associated section index
        partial_content: Text content for similarity matching
        start_position: Start position in section
        end_position: End position in section
    """
    id: str
    section_index: int
    partial_content: str
    start_position: int
    end_position: int

    def get_content_length(self) -> int:
        """Get content length."""
        return len(self.partial_content)
```

#### SimilarityResult

```python
@dataclass
class SimilarityResult:
    """Similarity calculation result.

    Attributes:
        chunk: Associated chunk object
        similarity_score: Similarity score (0.0 to 1.0)
        similarity_type: Type of similarity calculation
        metadata: Additional calculation metadata
    """
    chunk: Chunk
    similarity_score: float
    similarity_type: str  # "semantic", "phonetic", "hybrid"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: 'SimilarityResult') -> bool:
        """Enable sorting by similarity score."""
        return self.similarity_score < other.similarity_score
```

## Component APIs

### SimilarityCalculator

**Location**: `src/core/components/similarity_calculator.py`

#### Class Definition

```python
class SimilarityCalculator:
    """Hybrid similarity calculation using semantic and phonetic matching.

    Combines transformer-based semantic embeddings with metaphone phonetic
    codes to provide robust similarity matching for voice navigation.
    """

    def __init__(
        self,
        semantic_weight: float = 0.7,
        phonetic_weight: float = 0.3
    ) -> None:
        """Initialize similarity calculator.

        Args:
            semantic_weight: Weight for semantic similarity (0.0-1.0)
            phonetic_weight: Weight for phonetic similarity (0.0-1.0)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
```

#### Public Methods

```python
def calculate_similarity(
    self,
    input_text: str,
    chunks: list[Chunk],
    top_k: int = 5
) -> list[SimilarityResult]:
    """Calculate similarity scores for input against chunks.

    Args:
        input_text: Input text to match against
        chunks: List of chunks to compare
        top_k: Number of top results to return

    Returns:
        list[SimilarityResult]: Top matching chunks with scores

    Raises:
        ValueError: If input_text is empty or chunks is empty
    """

def calculate_semantic_similarity(
    self,
    input_text: str,
    chunks: list[Chunk]
) -> list[SimilarityResult]:
    """Calculate semantic similarity using embeddings.

    Args:
        input_text: Input text to match
        chunks: Chunks to compare against

    Returns:
        list[SimilarityResult]: Results with semantic scores
    """

def calculate_phonetic_similarity(
    self,
    input_text: str,
    chunks: list[Chunk]
) -> list[SimilarityResult]:
    """Calculate phonetic similarity using metaphone codes.

    Args:
        input_text: Input text to match
        chunks: Chunks to compare against

    Returns:
        list[SimilarityResult]: Results with phonetic scores
    """

def update_weights(
    self,
    semantic_weight: float,
    phonetic_weight: float
) -> None:
    """Update similarity calculation weights.

    Args:
        semantic_weight: New semantic weight
        phonetic_weight: New phonetic weight

    Raises:
        ValueError: If weights don't sum to 1.0
    """
```

### ChunkProducer

**Location**: `src/core/components/chunk_producer.py`

#### Class Definition

```python
class ChunkProducer:
    """Generates navigation chunks from presentation sections.

    Creates overlapping text windows for robust voice navigation,
    optimized for similarity-based matching algorithms.
    """

    def __init__(self, window_size: int = 12, overlap: int = 4) -> None:
        """Initialize chunk producer.

        Args:
            window_size: Number of sentences per chunk
            overlap: Sentence overlap between consecutive chunks
        """
```

#### Public Methods

```python
def generate_chunks(
    self,
    sections: list[str],
    window_size: int = None
) -> list[Chunk]:
    """Generate chunks from presentation sections.

    Args:
        sections: List of section content strings
        window_size: Override default window size (optional)

    Returns:
        list[Chunk]: Generated navigation chunks

    Raises:
        ValueError: If sections is empty
    """

def chunk_single_section(
    self,
    section_content: str,
    section_index: int,
    window_size: int = None
) -> list[Chunk]:
    """Generate chunks from single section.

    Args:
        section_content: Section text content
        section_index: Section index number
        window_size: Override default window size

    Returns:
        list[Chunk]: Generated chunks for the section
    """

def get_chunk_statistics(self, chunks: list[Chunk]) -> dict[str, Any]:
    """Get statistics about generated chunks.

    Args:
        chunks: List of chunks to analyze

    Returns:
        dict: Statistics including:
            - total_chunks: Total number of chunks
            - avg_length: Average chunk length
            - sections_covered: Number of sections covered
            - coverage_ratio: Content coverage ratio
    """
```

## Utility APIs

### TextNormalizer

**Location**: `src/utils/text_normalizer.py`

#### Class Definition

```python
class TextNormalizer:
    """Text normalization and cleaning utilities.

    Provides consistent text preprocessing for speech recognition,
    similarity calculations, and content processing.
    """

    def __init__(self) -> None:
        """Initialize text normalizer with default rules."""
```

#### Public Methods

```python
def normalize_text(self, text: str) -> str:
    """Complete text normalization pipeline.

    Args:
        text: Input text to normalize

    Returns:
        str: Normalized text

    Raises:
        ValueError: If text is not string type
    """

def normalize_for_similarity(self, text: str) -> str:
    """Normalize text for similarity comparison.

    Args:
        text: Input text to normalize

    Returns:
        str: Text optimized for similarity matching
    """

def normalize_for_search(self, text: str) -> str:
    """Normalize text for search operations.

    Args:
        text: Input text to normalize

    Returns:
        str: Text optimized for search
    """
```

### IDGenerator

**Location**: `src/utils/id_generator.py`

#### Static Methods

```python
class IDGenerator:
    """Generates various types of unique identifiers."""

    @staticmethod
    def generate_uuid() -> str:
        """Generate standard UUID4.

        Returns:
            str: UUID4 string
        """

    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate shorter readable ID.

        Args:
            length: Desired ID length

        Returns:
            str: Short ID string
        """

    @staticmethod
    def generate_hash_id(content: str, length: int = 16) -> str:
        """Generate content-based hash ID.

        Args:
            content: Content to hash
            length: Hash length

        Returns:
            str: Hash-based ID
        """
```

## Configuration APIs

### Settings Schema

```python
class SettingsSchema:
    """Settings template schema definition."""

    TEMPLATE_SCHEMA = {
        "llm_model": {
            "type": str,
            "default": "gemini/gemini-2.0-flash",
            "description": "LLM model identifier"
        },
        "llm_api_key": {
            "type": str,
            "default": "",
            "description": "API key for LLM service"
        },
        "similarity_semantic_weight": {
            "type": float,
            "default": 0.7,
            "description": "Weight for semantic similarity (0.0-1.0)"
        },
        "similarity_phonetic_weight": {
            "type": float,
            "default": 0.3,
            "description": "Weight for phonetic similarity (0.0-1.0)"
        },
        "audio_sample_rate": {
            "type": int,
            "default": 16000,
            "description": "Audio sampling rate (Hz)"
        },
        "audio_frame_duration": {
            "type": float,
            "default": 0.1,
            "description": "Audio processing frame duration (seconds)"
        }
    }
```

## Error Classes

### Custom Exceptions

```python
class MovesError(Exception):
    """Base exception for Moves application."""
    pass

class SpeakerNotFoundError(MovesError):
    """Raised when speaker ID is not found."""
    pass

class PresentationNotFoundError(MovesError):
    """Raised when presentation ID is not found."""
    pass

class ProcessingError(MovesError):
    """Raised when AI processing fails."""
    pass

class ValidationError(MovesError):
    """Raised when data validation fails."""
    pass

class AudioError(MovesError):
    """Raised when audio system fails."""
    pass

class ModelLoadError(MovesError):
    """Raised when ML model loading fails."""
    pass

class SettingNotFoundError(MovesError):
    """Raised when configuration setting is not found."""
    pass

class ConfigurationError(MovesError):
    """Raised when configuration is invalid."""
    pass
```

## Type Definitions

### Type Aliases

```python
from typing import TypeAlias, Callable, Any

# Function types
NavigationCallback: TypeAlias = Callable[[int, str], None]
RecognitionCallback: TypeAlias = Callable[[str, float], None]
EventCallback: TypeAlias = Callable[[str, dict[str, Any]], None]

# Data types
SpeakerID: TypeAlias = str
PresentationID: TypeAlias = str
ChunkID: TypeAlias = str
SectionIndex: TypeAlias = int

# Configuration types
SettingKey: TypeAlias = str
SettingValue: TypeAlias = Any
SettingsDict: TypeAlias = dict[SettingKey, SettingValue]

# ML types
EmbeddingVector: TypeAlias = list[float]
SimilarityScore: TypeAlias = float
ModelName: TypeAlias = str
```

### Protocol Definitions

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SimilarityUnit(Protocol):
    """Protocol for similarity calculation units."""

    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        """Compare input against candidate chunks."""
        ...

@runtime_checkable
class AudioProcessor(Protocol):
    """Protocol for audio processing components."""

    def start_processing(self) -> None:
        """Start audio processing."""
        ...

    def stop_processing(self) -> None:
        """Stop audio processing."""
        ...

    def is_processing(self) -> bool:
        """Check if currently processing."""
        ...

@runtime_checkable
class DataPersistence(Protocol):
    """Protocol for data persistence layers."""

    def save(self, key: str, data: Any) -> bool:
        """Save data with key."""
        ...

    def load(self, key: str) -> Any:
        """Load data by key."""
        ...

    def delete(self, key: str) -> bool:
        """Delete data by key."""
        ...
```

## Constants

### Application Constants

```python
# Application metadata
APP_NAME = "Moves"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered voice-controlled presentation navigation"

# File system constants
DATA_DIR_NAME = ".moves"
SETTINGS_FILE_NAME = "settings.yaml"
TEMPLATE_FILE_NAME = "settings_template.yaml"
LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "moves.log"

# Processing constants
DEFAULT_WINDOW_SIZE = 12
DEFAULT_OVERLAP = 4
DEFAULT_SIMILARITY_THRESHOLD = 0.3
MAX_RECOGNITION_RESULTS = 5

# Audio constants
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_FRAME_DURATION = 0.1
DEFAULT_AUDIO_CHANNELS = 1

# Model constants
STT_MODEL_PATH = "src/core/components/ml_models/stt/"
EMBEDDING_MODEL_PATH = "src/core/components/ml_models/embedding/"
DEFAULT_LLM_TEMPERATURE = 0.2

# Similarity weights
DEFAULT_SEMANTIC_WEIGHT = 0.7
DEFAULT_PHONETIC_WEIGHT = 0.3

# File extensions
SUPPORTED_PDF_EXTENSIONS = [".pdf"]
SUPPORTED_AUDIO_EXTENSIONS = [".wav", ".mp3", ".flac"]
SUPPORTED_CONFIG_EXTENSIONS = [".yaml", ".yml", ".json"]
```

### Error Codes

```python
class ErrorCodes:
    """Standard error codes for API responses."""

    # Success
    SUCCESS = 0

    # General errors
    UNKNOWN_ERROR = 1000
    INVALID_INPUT = 1001
    PERMISSION_DENIED = 1002

    # Data errors
    NOT_FOUND = 2000
    ALREADY_EXISTS = 2001
    DATA_CORRUPTION = 2002

    # Processing errors
    PROCESSING_FAILED = 3000
    MODEL_ERROR = 3001
    AUDIO_ERROR = 3002

    # Configuration errors
    CONFIG_ERROR = 4000
    VALIDATION_ERROR = 4001
    SETTING_NOT_FOUND = 4002
```

This API reference provides comprehensive documentation for all public interfaces in the Moves application, enabling developers to integrate with and extend the system effectively.
