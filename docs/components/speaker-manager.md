# Speaker Manager

The `SpeakerManager` is responsible for managing speaker profiles, handling their presentation and transcript files, and coordinating AI-powered processing to generate navigable sections. It serves as the primary interface for speaker-related operations and data management.

## Table of Contents

- [Overview](#overview)
- [Core Functionality](#core-functionality)
- [Speaker Lifecycle](#speaker-lifecycle)
- [File Management](#file-management)
- [AI Processing Pipeline](#ai-processing-pipeline)
- [Data Persistence](#data-persistence)
- [Speaker Resolution](#speaker-resolution)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

## Overview

**Location**: `src/core/speaker_manager.py`

The SpeakerManager handles the complete lifecycle of speaker profiles, from initial creation through AI processing to deletion. It manages both the metadata (speaker information) and associated files (presentations and transcripts) while coordinating with AI services to generate navigable content.

```python
class SpeakerManager:
    def __init__(self):
        self.SPEAKERS_PATH = data_handler.DATA_FOLDER.resolve() / "speakers"

    # Core operations
    def add(self, name, source_presentation, source_transcript) -> Speaker
    def edit(self, speaker, source_presentation=None, source_transcript=None) -> Speaker
    def process(self, speakers, llm_model, llm_api_key) -> list[ProcessResult]
    def delete(self, speaker) -> bool
    def list(self) -> list[Speaker]
    def resolve(self, speaker_pattern) -> Speaker
```

## Core Functionality

### 1. Speaker Profile Management

- **Creation**: Generate unique speaker profiles with ID generation
- **Modification**: Update presentation or transcript files
- **Deletion**: Clean removal of speaker data and files
- **Listing**: Enumerate all registered speakers with status

### 2. File System Operations

- **File Copying**: Manage presentation and transcript files
- **Path Resolution**: Handle both source and local file paths
- **Storage Organization**: Structured directory layout per speaker

### 3. AI Integration Coordination

- **Batch Processing**: Handle multiple speakers simultaneously
- **Async Operations**: Non-blocking processing with proper coordination
- **Result Aggregation**: Collect and return processing outcomes

## Speaker Lifecycle

### 1. Creation Phase

```python
def add(self, name: str, source_presentation: Path, source_transcript: Path) -> Speaker:
    # Generate unique identifier
    speaker_id = id_generator.generate_speaker_id(name)

    # Create speaker object
    speaker = Speaker(
        name=name,
        speaker_id=speaker_id,
        source_presentation=source_presentation.resolve(),
        source_transcript=source_transcript.resolve(),
    )

    # Persist to file system
    speaker_path = self.SPEAKERS_PATH / speaker_id
    data = {k: str(v) if isinstance(v, Path) else v
            for k, v in asdict(speaker).items()}
    data_handler.write(speaker_path / "speaker.json", json.dumps(data, indent=4))

    return speaker
```

**Creation Process**:

1. **ID Generation**: Create unique, human-readable identifier
2. **Path Resolution**: Convert relative paths to absolute
3. **Validation**: Ensure required files exist and are accessible
4. **Persistence**: Store speaker metadata as JSON
5. **Directory Structure**: Create organized speaker-specific directories

### 2. Processing Phase

```python
async def process_speaker(speaker, speaker_path, delay):
    # File management
    presentation_path, transcript_path = await prepare_files(speaker, speaker_path)

    # AI section generation
    sections = await asyncio.to_thread(
        section_producer.generate_sections,
        presentation_path=presentation_path,
        transcript_path=transcript_path,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
    )

    # Data persistence
    data_handler.write(
        speaker_path / "sections.json",
        json.dumps(section_producer.convert_to_list(sections), indent=2),
    )

    return ProcessResult(
        section_count=len(sections),
        transcript_from=transcript_from,
        presentation_from=presentation_from,
    )
```

**Processing Pipeline**:

1. **File Preparation**: Copy and organize source files locally
2. **AI Generation**: Create aligned sections using LLM
3. **Data Storage**: Persist generated sections for navigation
4. **Result Reporting**: Provide processing outcomes and statistics

### 3. Resolution and Retrieval

```python
def resolve(self, speaker_pattern: str) -> Speaker:
    speakers = self.list()
    speaker_ids = [speaker.speaker_id for speaker in speakers]

    # Direct ID match
    if speaker_pattern in speaker_ids:
        return speakers[speaker_ids.index(speaker_pattern)]

    # Name-based matching
    matched_speakers = [s for s in speakers if s.name == speaker_pattern]

    if len(matched_speakers) == 1:
        return matched_speakers[0]
    elif len(matched_speakers) > 1:
        # Handle ambiguous matches
        speaker_list = "\n".join([f"    {s.name} ({s.speaker_id})" for s in matched_speakers])
        raise ValueError(f"Multiple speakers found matching '{speaker_pattern}':\n{speaker_list}")

    raise ValueError(f"No speaker found matching '{speaker_pattern}'.")
```

## File Management

### File Organization Strategy

```
~/.moves/speakers/
└── {speaker-id}/              # e.g., "john-doe-Ax9K2"
    ├── speaker.json           # Speaker metadata
    ├── presentation.pdf       # Local presentation copy
    ├── transcript.pdf         # Local transcript copy
    └── sections.json          # Generated navigation sections (after processing)
```

### File Handling Logic

```python
# Source file priority
if source_presentation.exists():
    # Copy from source and normalize name
    data_handler.copy(source_presentation, speaker_path)
    if source_presentation.name != "presentation.pdf":
        # Standardize filename
        relative_path = (speaker_path / source_presentation.name).relative_to(data_handler.DATA_FOLDER)
        data_handler.rename(relative_path, "presentation.pdf")
    presentation_path = speaker_path / "presentation.pdf"
    presentation_from = "SOURCE"
elif local_presentation.exists():
    # Use existing local file
    presentation_path = local_presentation
    presentation_from = "LOCAL"
else:
    raise FileNotFoundError(f"Missing presentation file for speaker {speaker.name}")
```

**File Management Features**:

- **Source Priority**: Prefer source files over cached local copies
- **Name Normalization**: Standardize filenames for consistent access
- **Fallback Strategy**: Use local copies when source files unavailable
- **Error Handling**: Clear error messages for missing files

## AI Processing Pipeline

### Batch Processing Architecture

```python
def process(self, speakers: list[Speaker], llm_model: str, llm_api_key: str) -> list[ProcessResult]:
    async def run():
        # Create processing tasks with staggered delays
        tasks = [
            process_speaker(speaker, speaker_path, idx)
            for idx, (speaker, speaker_path) in enumerate(zip(speakers, speaker_paths))
        ]

        # Execute concurrently
        results = await asyncio.gather(*tasks)
        return results

    return asyncio.run(run())
```

**Processing Features**:

- **Concurrent Execution**: Process multiple speakers simultaneously
- **Staggered Delays**: Prevent API rate limiting with delayed starts
- **Error Isolation**: Individual failures don't affect other speakers
- **Result Aggregation**: Collect outcomes for batch reporting

### AI Integration Workflow

```python
# 1. File Preparation
presentation_data = section_producer._extract_pdf(presentation_path, "presentation")
transcript_data = section_producer._extract_pdf(transcript_path, "transcript")

# 2. LLM Processing
sections = section_producer._call_llm(
    presentation_data=presentation_data,
    transcript_data=transcript_data,
    llm_model=llm_model,
    llm_api_key=llm_api_key,
)

# 3. Data Structuring
structured_sections = [
    Section(content=content, section_index=idx)
    for idx, content in enumerate(sections)
]
```

## Data Persistence

### Speaker Metadata Format

```json
{
  "name": "John Doe",
  "speaker_id": "john-doe-Ax9K2",
  "source_presentation": "/path/to/original/presentation.pdf",
  "source_transcript": "/path/to/original/transcript.pdf"
}
```

### Generated Sections Format

```json
[
  {
    "content": "Welcome to our presentation on AI technology and its applications.",
    "section_index": 0
  },
  {
    "content": "Today we'll explore machine learning, NLP, and computer vision.",
    "section_index": 1
  }
]
```

### Data Serialization

```python
# Speaker metadata serialization
data = {k: str(v) if isinstance(v, Path) else v
        for k, v in asdict(speaker).items()}
data_handler.write(speaker_path / "speaker.json", json.dumps(data, indent=4))

# Section data serialization
sections_data = section_producer.convert_to_list(sections)
data_handler.write(
    speaker_path / "sections.json",
    json.dumps(sections_data, indent=2, ensure_ascii=False)
)
```

## Speaker Resolution

### Flexible Lookup System

The SpeakerManager provides flexible speaker resolution supporting both IDs and names:

```python
# Resolution strategies
1. Direct ID match: "john-doe-Ax9K2" → exact speaker
2. Name match: "John Doe" → speaker with matching name
3. Partial match: "John" → speaker if unique name match
4. Ambiguity handling: Multiple matches → error with suggestions
```

### Resolution Examples

```python
# Direct ID resolution
speaker = speaker_manager.resolve("john-doe-Ax9K2")

# Name-based resolution
speaker = speaker_manager.resolve("John Doe")

# Ambiguous resolution (raises ValueError)
try:
    speaker = speaker_manager.resolve("John")  # Multiple Johns exist
except ValueError as e:
    print(e)  # "Multiple speakers found matching 'John': ..."
```

## Error Handling

### Validation and Error Prevention

```python
def add(self, name: str, source_presentation: Path, source_transcript: Path) -> Speaker:
    current_speakers = self.list()
    speaker_ids = [speaker.speaker_id for speaker in current_speakers]

    # Prevent name/ID conflicts
    if name in speaker_ids:
        raise ValueError(f"Given name '{name}' conflicts with existing speaker ID.")

    # Validate file existence (handled by CLI layer)
    # File validation occurs before SpeakerManager methods are called
```

### Processing Error Management

```python
async def process_speaker(speaker, speaker_path, delay):
    try:
        # File preparation
        if not ((source_presentation.exists() and source_transcript.exists()) or
                (local_presentation.exists() and local_transcript.exists())):
            raise FileNotFoundError(f"Missing files for speaker {speaker.name}")

        # AI processing
        sections = await asyncio.to_thread(section_producer.generate_sections, ...)

        # Success result
        return ProcessResult(...)

    except Exception as e:
        # Error propagation with context
        raise RuntimeError(f"Failed to process speaker {speaker.name}: {e}") from e
```

**Error Handling Principles**:

- **Early Validation**: Check preconditions before operations
- **Contextual Errors**: Provide clear error messages with speaker context
- **Resource Cleanup**: Ensure proper cleanup on failures
- **Error Propagation**: Pass errors up with additional context

## Usage Examples

### Basic Speaker Operations

```python
# Initialize manager
speaker_manager = SpeakerManager()

# Add new speaker
speaker = speaker_manager.add(
    name="Dr. Smith",
    source_presentation=Path("./research-presentation.pdf"),
    source_transcript=Path("./research-transcript.pdf")
)

# List all speakers
speakers = speaker_manager.list()
for speaker in speakers:
    print(f"{speaker.name} ({speaker.speaker_id})")

# Find specific speaker
found_speaker = speaker_manager.resolve("Dr. Smith")
```

### File Management Operations

```python
# Update speaker files
updated_speaker = speaker_manager.edit(
    speaker=found_speaker,
    source_presentation=Path("./updated-presentation.pdf"),
    source_transcript=None  # Keep existing transcript
)

# Show speaker status
speaker_path = data_handler.DATA_FOLDER / "speakers" / speaker.speaker_id
sections_file = speaker_path / "sections.json"
status = "Ready" if sections_file.exists() else "Not Ready"
print(f"Speaker {speaker.name} is {status}")
```

### Batch Processing

```python
# Process multiple speakers
speakers_to_process = [
    speaker_manager.resolve("Dr. Smith"),
    speaker_manager.resolve("Prof. Johnson")
]

results = speaker_manager.process(
    speakers=speakers_to_process,
    llm_model="gemini/gemini-2.0-flash",
    llm_api_key="your-api-key"
)

# Review results
for speaker, result in zip(speakers_to_process, results):
    print(f"{speaker.name}: {result.section_count} sections created")
    print(f"  Sources: {result.presentation_from}, {result.transcript_from}")
```

### Cleanup Operations

```python
# Delete speaker and all associated data
success = speaker_manager.delete(speaker)
if success:
    print(f"Speaker {speaker.name} deleted successfully")
else:
    print(f"Failed to delete speaker {speaker.name}")
```

### Integration with CLI

```python
# CLI command integration example
@speaker_app.command("add")
def speaker_add(name: str, source_presentation: Path, source_transcript: Path):
    try:
        speaker_manager = SpeakerManager()
        speaker = speaker_manager.add(name, source_presentation, source_transcript)

        # Success feedback
        typer.echo(f"Speaker '{speaker.name}' ({speaker.speaker_id}) added.")
        typer.echo(f"    ID -> {speaker.speaker_id}")
        typer.echo(f"    Presentation -> {speaker.source_presentation}")
        typer.echo(f"    Transcript -> {speaker.source_transcript}")

    except Exception as e:
        typer.echo(f"Could not add speaker '{name}'.", err=True)
        typer.echo(f"    {str(e)}", err=True)
        raise typer.Exit(1)
```

The SpeakerManager provides a robust foundation for managing speaker profiles and their associated data, handling everything from initial file management through AI processing to final cleanup. Its flexible resolution system and comprehensive error handling make it reliable for both programmatic use and CLI integration.
