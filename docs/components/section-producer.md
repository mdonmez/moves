# Section Producer

The `SectionProducer` is responsible for AI-powered content generation that aligns presentation slides with speaker transcripts. It uses Large Language Models (LLMs) to create navigable sections that enable intelligent voice-controlled presentation navigation.

## Table of Contents

- [Overview](#overview)
- [PDF Processing](#pdf-processing)
- [LLM Integration](#llm-integration)
- [Content Alignment](#content-alignment)
- [Data Conversion](#data-conversion)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

## Overview

**Location**: `src/core/components/section_producer.py`

The SectionProducer bridges the gap between static presentation content and dynamic speech patterns by generating aligned sections that represent what the speaker says for each slide. This enables the system to match real-time speech against appropriate slide content.

```python
def generate_sections(
    presentation_path: Path,
    transcript_path: Path,
    llm_model: str,
    llm_api_key: str
) -> list[Section]:
    # Extract content from PDFs
    presentation_data = _extract_pdf(presentation_path, "presentation")
    transcript_data = _extract_pdf(transcript_path, "transcript")

    # Generate aligned sections using AI
    section_contents = _call_llm(presentation_data, transcript_data, llm_model, llm_api_key)

    # Create structured section objects
    return [Section(content=content, section_index=idx)
            for idx, content in enumerate(section_contents)]
```

## PDF Processing

### Dual-Mode Extraction

The SectionProducer handles two types of PDF content with different extraction strategies:

```python
def _extract_pdf(pdf_path: Path, extraction_type: Literal["transcript", "presentation"]) -> str:
    try:
        with pymupdf.open(pdf_path) as doc:
            match extraction_type:
                case "transcript":
                    # Continuous text extraction
                    full_text = "".join(page.get_text("text") for page in doc)
                    return " ".join(full_text.split())

                case "presentation":
                    # Slide-by-slide extraction
                    markdown_sections = []
                    for i, page in enumerate(doc):
                        page_text = page.get_text("text")
                        cleaned_text = " ".join(page_text.split())
                        markdown_sections.append(f"# Slide Page {i}\n{cleaned_text}")
                    return "\n\n".join(markdown_sections)

    except Exception as e:
        raise RuntimeError(f"PDF extraction failed for {pdf_path} ({extraction_type}): {e}") from e
```

### Transcript Processing

**Purpose**: Extract continuous speech content for analysis

**Process**:

1. **Text Extraction**: Extract all text from PDF pages
2. **Normalization**: Join all content into continuous text
3. **Cleaning**: Remove excessive whitespace and formatting artifacts

**Result**: Single continuous string representing the speaker's complete speech

### Presentation Processing

**Purpose**: Maintain slide structure for content alignment

**Process**:

1. **Page-by-Page Processing**: Extract content from each slide separately
2. **Markdown Formatting**: Structure content with slide headers
3. **Content Cleaning**: Normalize whitespace while preserving structure

**Result**: Structured markdown with clear slide boundaries:

```markdown
# Slide Page 0

Welcome to our presentation on AI technology.

# Slide Page 1

Today we'll cover three main topics: machine learning, natural language processing, and computer vision.

# Slide Page 2

Let's start with machine learning fundamentals.
```

## LLM Integration

### Structured Output Generation

The SectionProducer uses the `instructor` library with LiteLLM to ensure structured, validated output:

```python
class SectionsOutputModel(BaseModel):
    class SectionItem(BaseModel):
        section_index: int = Field(..., ge=0, description="Index starting from 0")
        content: str = Field(..., description="Content of the section")

    sections: list[SectionItem] = Field(
        ...,
        description="List of section items, one for each slide",
        min_items=len(presentation_data.split("\n\n")),  # Enforce section count
        max_items=len(presentation_data.split("\n\n")),
    )
```

**Validation Features**:

- **Section Count Enforcement**: Ensures exactly one section per slide
- **Index Validation**: Validates section indices start from 0
- **Content Requirements**: Ensures all sections have content
- **Type Safety**: Strong typing for all fields

### LLM Call Implementation

```python
def _call_llm(presentation_data: str, transcript_data: str, llm_model: str, llm_api_key: str) -> list[str]:
    try:
        # Load system instructions
        system_prompt = Path("src/data/llm_instruction.md").read_text(encoding="utf-8")

        # Initialize structured client
        client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)

        # Generate response with validation
        response = client.chat.completions.create(
            model=llm_model,
            api_key=llm_api_key,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Presentation: {presentation_data}\nTranscript: {transcript_data}"},
            ],
            response_model=SectionsOutputModel,
            temperature=0.2,  # Low temperature for consistent results
        )

        # Extract content strings
        return [item.content for item in response.sections]

    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e
```

**LLM Configuration**:

- **Low Temperature**: 0.2 for consistent, deterministic output
- **Structured Validation**: Pydantic models ensure output format
- **Error Handling**: Comprehensive error reporting with context

## Content Alignment

### AI Processing Instructions

**Location**: `src/data/llm_instruction.md`

The SectionProducer uses detailed instructions to guide LLM behavior:

```markdown
Your primary function is to align presentation data with a speaker's transcript.

Your single objective is to produce one text segment for each slide provided.
Each segment must represent the speaker's narration corresponding to that specific slide's topic.

Key constraints:

1. Output-to-Input Correspondence: One segment per slide, exactly
2. Source Authority: Transcript is the authoritative source for content and language
3. Data Filtration: Ignore formatting, slide numbers, non-substantive content
4. Content Generation Hierarchy:
   A. Extract relevant passage from transcript (primary method)
   B. Synthesize missing content if completely absent (fallback)
5. No Empty Segments: Every slide must have corresponding content
```

### Alignment Process

1. **Content Analysis**: LLM analyzes both presentation structure and transcript content
2. **Topic Mapping**: Maps transcript portions to appropriate slides based on semantic similarity
3. **Content Extraction**: Extracts relevant transcript passages for each slide
4. **Gap Filling**: Generates content for slides with no corresponding transcript material
5. **Quality Assurance**: Ensures output maintains speaker's language and tone

### Output Quality Features

- **Language Consistency**: Matches transcript language and style
- **Content Relevance**: Aligns speech content with slide topics
- **Completeness**: Ensures every slide has navigable content
- **Speaker Voice**: Maintains natural speech patterns from transcript

## Data Conversion

### Section Object Creation

```python
def generate_sections(presentation_path: Path, transcript_path: Path, llm_model: str, llm_api_key: str) -> list[Section]:
    # Generate content strings from LLM
    section_contents = _call_llm(...)

    # Convert to structured Section objects
    generated_sections: list[Section] = []
    for idx, content in enumerate(section_contents):
        section = Section(content=content, section_index=idx)
        generated_sections.append(section)

    return generated_sections
```

### Serialization Support

```python
def convert_to_list(section_objects: list[Section]) -> list[dict[str, str | int]]:
    """Convert Section objects to JSON-serializable format"""
    return [
        {"content": s.content, "section_index": s.section_index}
        for s in section_objects
    ]

def convert_to_objects(section_list: list[dict[str, str | int]]) -> list[Section]:
    """Convert JSON data back to Section objects"""
    return [
        Section(
            content=cast(str, s_dict["content"]),
            section_index=cast(int, s_dict["section_index"]),
        )
        for s_dict in section_list
    ]
```

**Conversion Features**:

- **Bidirectional**: Convert between objects and serializable formats
- **Type Safety**: Maintains type information through conversions
- **JSON Compatibility**: Enables persistent storage and data exchange

## Error Handling

### PDF Processing Errors

```python
def _extract_pdf(pdf_path: Path, extraction_type: Literal["transcript", "presentation"]) -> str:
    try:
        with pymupdf.open(pdf_path) as doc:
            # PDF processing logic
            pass
    except Exception as e:
        raise RuntimeError(
            f"PDF extraction failed for {pdf_path} ({extraction_type}): {e}"
        ) from e
```

**Error Scenarios**:

- **File Access**: Handle permission or path issues
- **Corrupted PDFs**: Manage malformed PDF files
- **Empty Content**: Handle PDFs with no extractable text
- **Encoding Issues**: Manage character encoding problems

### LLM Processing Errors

```python
def _call_llm(...) -> list[str]:
    try:
        # LLM processing
        response = client.chat.completions.create(...)
        return [item.content for item in response.sections]
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e
```

**Error Scenarios**:

- **API Failures**: Network issues, rate limiting, service outages
- **Authentication**: Invalid API keys or expired credentials
- **Quota Exceeded**: Usage limit or billing issues
- **Validation Failures**: Output doesn't match expected structure

### Comprehensive Error Context

All error handling provides:

- **Operation Context**: Which phase failed (PDF extraction, LLM processing, etc.)
- **Input Information**: File paths, model names, data characteristics
- **Root Cause**: Original exception details preserved with `from e`
- **Actionable Messages**: Clear indication of what went wrong

## Usage Examples

### Basic Section Generation

```python
from pathlib import Path
from src.core.components.section_producer import generate_sections

# Generate sections from files
sections = generate_sections(
    presentation_path=Path("./presentation.pdf"),
    transcript_path=Path("./transcript.pdf"),
    llm_model="gemini/gemini-2.0-flash",
    llm_api_key="your-api-key"
)

print(f"Generated {len(sections)} sections")
for section in sections:
    print(f"Section {section.section_index}: {section.content[:100]}...")
```

### Data Persistence

```python
import json
from src.utils import data_handler
from src.core.components.section_producer import convert_to_list, convert_to_objects

# Convert sections to JSON format
sections_data = convert_to_list(sections)

# Save to file
output_path = Path("sections.json")
data_handler.write(
    output_path,
    json.dumps(sections_data, indent=2, ensure_ascii=False)
)

# Load from file later
loaded_data = json.loads(data_handler.read(output_path))
reconstructed_sections = convert_to_objects(loaded_data)
```

### Integration with Speaker Processing

```python
async def process_speaker(speaker, speaker_path, llm_model, llm_api_key):
    # File preparation
    presentation_path = speaker_path / "presentation.pdf"
    transcript_path = speaker_path / "transcript.pdf"

    # Generate sections
    sections = await asyncio.to_thread(
        generate_sections,
        presentation_path=presentation_path,
        transcript_path=transcript_path,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
    )

    # Save processed sections
    data_handler.write(
        speaker_path / "sections.json",
        json.dumps(convert_to_list(sections), indent=2)
    )

    return len(sections)
```

### Error Handling in Practice

```python
def safe_section_generation(presentation_path, transcript_path, llm_model, llm_api_key):
    try:
        sections = generate_sections(
            presentation_path=presentation_path,
            transcript_path=transcript_path,
            llm_model=llm_model,
            llm_api_key=llm_api_key
        )
        return sections, None

    except RuntimeError as e:
        if "PDF extraction failed" in str(e):
            return None, f"Could not read PDF files: {e}"
        elif "LLM call failed" in str(e):
            return None, f"AI processing failed: {e}"
        else:
            return None, f"Section generation failed: {e}"

    except Exception as e:
        return None, f"Unexpected error: {e}"

# Usage
sections, error = safe_section_generation(...)
if error:
    print(f"Error: {error}")
else:
    print(f"Success: Generated {len(sections)} sections")
```

### Custom Model Configuration

```python
# Different models for different use cases
models_config = {
    "fast": "gemini/gemini-2.0-flash",      # Quick processing
    "quality": "gpt-4",                      # High-quality alignment
    "cost_effective": "gpt-3.5-turbo",      # Budget-friendly option
}

def generate_with_model_selection(presentation_path, transcript_path, api_key, quality_level="fast"):
    model = models_config.get(quality_level, models_config["fast"])

    return generate_sections(
        presentation_path=presentation_path,
        transcript_path=transcript_path,
        llm_model=model,
        llm_api_key=api_key
    )
```

The SectionProducer represents the AI-powered intelligence that enables Moves to understand and align presentation content with natural speech patterns. By combining robust PDF processing, structured LLM integration, and comprehensive error handling, it creates the foundation for intelligent voice-controlled navigation.
