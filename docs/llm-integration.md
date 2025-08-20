# LLM Integration

## Overview

The LLM (Large Language Model) integration system is responsible for processing presentation materials and transcripts to generate synchronized content sections. This AI-powered component bridges the gap between raw presentation slides and speaker narration, creating the foundation for voice-controlled navigation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          LLM Integration Pipeline                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐   │
│  │     PDF     │───▶│    Text     │───▶│     LLM     │───▶│    Sections     │   │
│  │ Extraction  │    │ Processing  │    │ Processing  │    │  Generation     │   │
│  │             │    │             │    │             │    │                 │   │
│  │ • Slides    │    │ • Format    │    │ • Alignment │    │ • JSON Output   │   │
│  │ • Transcript│    │ • Clean     │    │ • Synthesis │    │ • Validation    │   │
│  │ • PyMuPDF   │    │ • Structure │    │ • liteLLM   │    │ • Serialization │   │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────────┘   │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                             Provider Support                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │   OpenAI    │  │  Anthropic  │  │   Google    │  │      Others         │     │
│  │             │  │             │  │             │  │                     │     │
│  │ • GPT-4     │  │ • Claude-3  │  │ • Gemini    │  │ • Azure OpenAI      │     │
│  │ • GPT-3.5   │  │ • Haiku     │  │ • Pro       │  │ • AWS Bedrock       │     │
│  │ • Turbo     │  │ • Sonnet    │  │ • Flash     │  │ • Cohere           │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## PDF Processing System

### Multi-Format PDF Extraction

The system handles two distinct types of PDF content, each requiring specialized extraction approaches.

#### Presentation PDF Processing
```python
def _extract_pdf(pdf_path: Path, extraction_type: "presentation") -> str:
    """
    Extract presentation content with slide-by-slide structure
    """
    try:
        with pymupdf.open(pdf_path) as doc:
            markdown_sections = []
            slide_count = 0
            
            for i, page in enumerate(doc):
                # Extract text from each slide page
                page_text = page.get_text("text")
                
                # Clean and normalize whitespace  
                cleaned_text = " ".join(page_text.split())
                
                # Structure as markdown with slide headers
                markdown_sections.append(f"# Slide Page {i}\\n{cleaned_text}")
                slide_count += 1
            
            return "\\n\\n".join(markdown_sections)
            
    except Exception as e:
        raise RuntimeError(
            f"PDF extraction failed for {pdf_path} (presentation): {e}"
        ) from e
```

**Presentation Output Format:**
```markdown
# Slide Page 0
Introduction to Machine Learning Overview of key concepts and applications in modern AI

# Slide Page 1  
What is Machine Learning? Definition: A subset of artificial intelligence that enables systems to learn

# Slide Page 2
Types of Machine Learning Supervised Unsupervised Reinforcement learning approaches
```

#### Transcript PDF Processing
```python
def _extract_pdf(pdf_path: Path, extraction_type: "transcript") -> str:
    """
    Extract transcript as continuous narrative text
    """
    try:
        with pymupdf.open(pdf_path) as doc:
            # Extract all text pages as continuous content
            full_text = "".join(page.get_text("text") for page in doc)
            
            # Normalize whitespace while preserving sentence structure
            result = " ".join(full_text.split())
            return result
            
    except Exception as e:
        raise RuntimeError(
            f"PDF extraction failed for {pdf_path} (transcript): {e}"
        ) from e
```

**Transcript Output Format:**
```text
Welcome everyone to today's presentation on machine learning. As we begin our journey into artificial intelligence, I want to start by defining what machine learning actually means. Machine learning is a powerful subset of artificial intelligence that allows computers to learn and make decisions without being explicitly programmed for every scenario...
```

### PDF Processing Challenges

#### Text Extraction Issues
- **OCR Artifacts**: Scanned PDFs may contain recognition errors
- **Formatting Noise**: Headers, footers, page numbers mixed with content
- **Multi-Column Layouts**: Complex slide layouts affecting text order
- **Non-Text Elements**: Images, charts, diagrams that don't extract as text

#### Quality Assurance
```python
def validate_extracted_content(presentation_data: str, transcript_data: str) -> bool:
    """
    Validate extracted content quality before LLM processing
    """
    # Check for minimum content length
    if len(presentation_data.strip()) < 100:
        raise ValueError("Presentation content too short - possible extraction failure")
        
    if len(transcript_data.strip()) < 200:
        raise ValueError("Transcript content too short - possible extraction failure")
    
    # Check for reasonable slide count
    slide_count = len(presentation_data.split("# Slide Page"))
    if slide_count < 2:
        raise ValueError("Too few slides detected in presentation")
    
    return True
```

## LLM Provider Integration

### LiteLLM Framework

The system uses LiteLLM for unified access to multiple LLM providers, enabling flexibility in model selection and cost optimization.

#### Provider Configuration
```python
import instructor
from litellm import completion

def _call_llm(presentation_data: str, transcript_data: str, 
              llm_model: str, llm_api_key: str) -> list[str]:
    """
    Call LLM with multi-provider support
    """
    try:
        # Create instructor client with liteLLM backend
        client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)
        
        # Make structured API call
        response = client.chat.completions.create(
            model=llm_model,
            api_key=llm_api_key,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Presentation: {presentation_data}\\nTranscript: {transcript_data}"},
            ],
            response_model=SectionsOutputModel,
            temperature=0.2,  # Low temperature for consistent output
        )
        
        return [item.content for item in response.sections]
        
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e
```

### Supported Providers

#### OpenAI Integration
```python
# Model configurations
model_configs = {
    "openai/gpt-4": {
        "max_tokens": 8192,
        "context_window": 128000,
        "cost_per_1k": {"input": 0.03, "output": 0.06}
    },
    "openai/gpt-3.5-turbo": {
        "max_tokens": 4096, 
        "context_window": 16385,
        "cost_per_1k": {"input": 0.0015, "output": 0.002}
    }
}
```

#### Anthropic Integration
```python
# Claude model support
model_configs = {
    "anthropic/claude-3-sonnet": {
        "max_tokens": 4096,
        "context_window": 200000,
        "cost_per_1k": {"input": 0.003, "output": 0.015}
    },
    "anthropic/claude-3-haiku": {
        "max_tokens": 4096,
        "context_window": 200000,
        "cost_per_1k": {"input": 0.00025, "output": 0.00125}
    }
}
```

#### Google Gemini Integration  
```python
# Gemini model support
model_configs = {
    "gemini/gemini-2.0-flash": {
        "max_tokens": 8192,
        "context_window": 1000000,  # 1M token context
        "cost_per_1k": {"input": 0.000075, "output": 0.0003}
    },
    "gemini/gemini-pro": {
        "max_tokens": 2048,
        "context_window": 30720,
        "cost_per_1k": {"input": 0.0005, "output": 0.0015}
    }
}
```

## Instruction System

### System Prompt Design

The system uses a carefully crafted instruction template that guides the LLM to perform accurate slide-to-transcript alignment.

#### Loading Instructions
```python
def load_system_prompt() -> str:
    """
    Load LLM instructions from markdown template
    """
    system_prompt = Path("src/data/llm_instruction.md").read_text(encoding="utf-8")
    return system_prompt
```

#### Instruction Template Structure

**Core Directives (from llm_instruction.md):**

1. **Output-to-Input Correspondence**
   - Exactly one text segment per slide
   - No exceptions, no empty sections
   - Direct 1:1 mapping requirement

2. **Source Authority and Language**  
   - Transcript is single source of truth
   - All output must match transcript language
   - No external knowledge injection

3. **Data Filtration**
   - Ignore slide numbers, formatting, artifacts
   - Focus only on substantive content
   - Match based on meaning, not literal text

4. **Content Generation Hierarchy**
   - **Primary**: Extract relevant transcript passages
   - **Secondary**: Minor condensation for focus
   - **Fallback**: Synthesize missing content in transcript style

5. **Prohibition of Omission**
   - Every slide must have corresponding content
   - No empty or missing sections allowed
   - Fallback synthesis when necessary

### Prompt Engineering Strategy

#### Context Management
```python
def build_prompt_context(presentation_data: str, transcript_data: str) -> str:
    """
    Structure input data for optimal LLM processing
    """
    prompt = f"""Presentation: {presentation_data}

Transcript: {transcript_data}"""
    
    # Validate total context length doesn't exceed model limits
    if len(prompt) > MAX_CONTEXT_LENGTH:
        # Implement truncation or chunking strategy
        prompt = truncate_context(prompt, MAX_CONTEXT_LENGTH)
    
    return prompt
```

#### Temperature and Parameters
```python
llm_parameters = {
    "temperature": 0.2,        # Low temperature for consistency
    "max_tokens": 4096,        # Sufficient for long presentations
    "top_p": 0.9,             # Nucleus sampling for quality
    "frequency_penalty": 0.0,  # No repetition penalty needed
    "presence_penalty": 0.0,   # No topic steering needed
}
```

## Structured Output Processing

### Response Model Definition

The system uses Pydantic models to ensure structured, validated output from the LLM.

#### Output Schema
```python
from pydantic import BaseModel, Field

class SectionsOutputModel(BaseModel):
    """
    Structured response model for LLM section generation
    """
    class SectionItem(BaseModel):
        section_index: int = Field(
            ..., 
            ge=0, 
            description="Index starting from 0"
        )
        content: str = Field(
            ..., 
            description="Content of the section",
            min_length=10,  # Ensure non-empty content
            max_length=2000  # Reasonable section length limit
        )

    sections: list[SectionItem] = Field(
        ...,
        description="List of section items, one for each slide",
        min_items=1,  # At least one section required
        max_items=200  # Reasonable presentation size limit
    )
```

#### Dynamic Validation
```python
def create_response_model(slide_count: int) -> type[BaseModel]:
    """
    Create response model with slide-count-specific validation
    """
    class DynamicSectionsModel(BaseModel):
        sections: list[SectionItem] = Field(
            ...,
            description="List of section items, one for each slide",
            min_items=slide_count,  # Exact slide count required
            max_items=slide_count   # No more, no less
        )
    
    return DynamicSectionsModel
```

### Response Processing

#### Content Extraction
```python
def extract_sections_from_response(response: SectionsOutputModel) -> list[str]:
    """
    Extract section content from structured LLM response
    """
    # Sort sections by index to ensure proper order
    sorted_sections = sorted(response.sections, key=lambda x: x.section_index)
    
    # Extract content strings
    section_contents = [section.content for section in sorted_sections]
    
    # Validate no sections are missing
    expected_indices = list(range(len(sorted_sections)))
    actual_indices = [section.section_index for section in sorted_sections]
    
    if expected_indices != actual_indices:
        raise ValueError(f"Missing or duplicate section indices: {actual_indices}")
    
    return section_contents
```

#### Quality Assurance
```python
def validate_generated_sections(sections: list[str], slide_count: int) -> bool:
    """
    Validate generated sections meet quality standards
    """
    # Check section count matches slide count
    if len(sections) != slide_count:
        raise ValueError(f"Generated {len(sections)} sections, expected {slide_count}")
    
    # Check no empty sections
    for i, section in enumerate(sections):
        if not section.strip():
            raise ValueError(f"Section {i} is empty")
        
        # Check minimum content length
        if len(section.strip()) < 10:
            raise ValueError(f"Section {i} too short: '{section}'")
    
    return True
```

## Section Generation Process

### End-to-End Workflow

#### Main Generation Function
```python
def generate_sections(presentation_path: Path, transcript_path: Path, 
                     llm_model: str, llm_api_key: str) -> list[Section]:
    """
    Complete pipeline for generating synchronized sections
    """
    # Step 1: Extract content from PDFs
    presentation_data = _extract_pdf(presentation_path, "presentation")
    transcript_data = _extract_pdf(transcript_path, "transcript")
    
    # Step 2: Validate extracted content
    validate_extracted_content(presentation_data, transcript_data)
    
    # Step 3: Call LLM for content alignment
    section_contents = _call_llm(
        presentation_data=presentation_data,
        transcript_data=transcript_data,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
    )
    
    # Step 4: Create Section objects
    generated_sections = []
    for idx, content in enumerate(section_contents):
        section = Section(
            content=content,
            section_index=idx,
        )
        generated_sections.append(section)
    
    # Step 5: Final validation
    validate_generated_sections(
        [s.content for s in generated_sections], 
        len(presentation_data.split("\\n\\n"))
    )
    
    return generated_sections
```

### Content Alignment Examples

#### Example 1: Technical Presentation

**Input Slide:**
```markdown
# Slide Page 5
Machine Learning Algorithms
• Supervised Learning
• Unsupervised Learning  
• Reinforcement Learning
```

**Input Transcript Excerpt:**
```text
Now let's dive into the core algorithms that power machine learning. We have three main categories here. First is supervised learning, where we train models on labeled data to make predictions. Then there's unsupervised learning, which finds patterns in data without labels. Finally, reinforcement learning teaches agents through rewards and penalties...
```

**Generated Section:**
```text
Now let's dive into the core algorithms that power machine learning. We have three main categories here. First is supervised learning, where we train models on labeled data to make predictions. Then there's unsupervised learning, which finds patterns in data without labels. Finally, reinforcement learning teaches agents through rewards and penalties.
```

#### Example 2: Language Mismatch

**Input Slide (Spanish):**
```markdown
# Slide Page 3
Beneficios de la Inteligencia Artificial
• Automatización de procesos
• Mejora en la toma de decisiones
• Reducción de errores humanos
```

**Input Transcript (Spanish):**
```text
Ahora vamos a hablar sobre los principales beneficios que nos ofrece la inteligencia artificial en el mundo empresarial. Primero, tenemos la automatización de procesos repetitivos que nos permite ahorrar tiempo y recursos. Segundo, la IA mejora significativamente nuestra capacidad para tomar decisiones basadas en datos. Y tercero, reduce considerablemente los errores que normalmente cometen los humanos...
```

**Generated Section:**
```text
Ahora vamos a hablar sobre los principales beneficios que nos ofrece la inteligencia artificial en el mundo empresarial. Primero, tenemos la automatización de procesos repetitivos que nos permite ahorrar tiempo y recursos. Segundo, la IA mejora significativamente nuestra capacidad para tomar decisiones basadas en datos. Y tercero, reduce considerablemente los errores que normalmente cometen los humanos.
```

## Data Serialization

### Section Object Management

#### Section-to-JSON Conversion
```python
def convert_to_list(section_objects: list[Section]) -> list[dict[str, str | int]]:
    """
    Convert Section objects to JSON-serializable list
    """
    return [
        {
            "content": section.content,
            "section_index": section.section_index,
        }
        for section in section_objects
    ]
```

#### JSON-to-Section Conversion
```python
def convert_to_objects(section_list: list[dict[str, str | int]]) -> list[Section]:
    """
    Convert JSON data back to Section objects
    """
    sections = []
    for section_data in section_list:
        section = Section(
            content=str(section_data["content"]),
            section_index=int(section_data["section_index"]),
        )
        sections.append(section)
    
    # Sort by section index to ensure proper order
    return sorted(sections, key=lambda s: s.section_index)
```

#### Storage Format
```json
[
    {
        "content": "Welcome everyone to today's presentation on machine learning...",
        "section_index": 0
    },
    {
        "content": "Now let's dive into what machine learning actually means...", 
        "section_index": 1
    },
    {
        "content": "We have three main categories of machine learning algorithms...",
        "section_index": 2
    }
]
```

## Error Handling and Recovery

### LLM API Errors

#### Network and Timeout Handling
```python
def call_llm_with_retry(presentation_data: str, transcript_data: str,
                       llm_model: str, llm_api_key: str, 
                       max_retries: int = 3) -> list[str]:
    """
    Call LLM with retry logic for transient failures
    """
    for attempt in range(max_retries):
        try:
            return _call_llm(presentation_data, transcript_data, llm_model, llm_api_key)
            
        except requests.exceptions.Timeout as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM request timed out after {max_retries} attempts")
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except requests.exceptions.ConnectionError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM connection failed after {max_retries} attempts")
            time.sleep(2 ** attempt)
            
        except Exception as e:
            # Don't retry for authentication or quota errors
            if "authentication" in str(e).lower() or "quota" in str(e).lower():
                raise RuntimeError(f"LLM API error: {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM processing failed: {e}")
            time.sleep(1)
```

### Response Validation Errors

#### Malformed Response Recovery
```python
def handle_invalid_response(response_text: str, slide_count: int) -> list[str]:
    """
    Attempt to recover from malformed LLM responses
    """
    try:
        # Try to parse as JSON manually
        import json
        data = json.loads(response_text)
        
        if isinstance(data, dict) and "sections" in data:
            sections = data["sections"]
            if len(sections) == slide_count:
                return [section.get("content", "") for section in sections]
        
        # Fallback: create placeholder sections
        return [f"Content for slide {i+1} (processing error)" 
                for i in range(slide_count)]
                
    except Exception:
        # Last resort: placeholder content
        return [f"Slide {i+1} content unavailable" 
                for i in range(slide_count)]
```

### Content Quality Issues

#### Incomplete Content Detection
```python
def detect_content_issues(sections: list[str]) -> list[str]:
    """
    Detect and report potential content quality issues
    """
    issues = []
    
    for i, section in enumerate(sections):
        # Check for very short content
        if len(section.strip()) < 20:
            issues.append(f"Section {i}: Content too short")
        
        # Check for placeholder text
        if "content unavailable" in section.lower():
            issues.append(f"Section {i}: Placeholder content detected")
        
        # Check for repetitive content
        if i > 0 and section.strip() == sections[i-1].strip():
            issues.append(f"Section {i}: Duplicate content")
    
    return issues
```

## Performance Optimization

### Context Length Management

#### Efficient Content Truncation
```python
def optimize_context_length(presentation_data: str, transcript_data: str,
                          max_context_length: int) -> tuple[str, str]:
    """
    Optimize input content to fit within model context limits
    """
    # Calculate current lengths
    presentation_length = len(presentation_data)
    transcript_length = len(transcript_data)
    total_length = presentation_length + transcript_length
    
    if total_length <= max_context_length:
        return presentation_data, transcript_data
    
    # Proportional truncation to maintain balance
    presentation_ratio = presentation_length / total_length
    transcript_ratio = transcript_length / total_length
    
    max_presentation = int(max_context_length * presentation_ratio * 0.9)
    max_transcript = int(max_context_length * transcript_ratio * 0.9)
    
    # Truncate while preserving structure
    truncated_presentation = truncate_presentation(presentation_data, max_presentation)
    truncated_transcript = truncate_transcript(transcript_data, max_transcript)
    
    return truncated_presentation, truncated_transcript
```

### Batch Processing Support

#### Multiple Speaker Processing
```python
async def process_multiple_speakers(speakers: list[Speaker], 
                                  llm_model: str, llm_api_key: str) -> list[ProcessResult]:
    """
    Process multiple speakers concurrently with rate limiting
    """
    semaphore = asyncio.Semaphore(3)  # Limit concurrent API calls
    
    async def process_single_speaker(speaker: Speaker, delay: float) -> ProcessResult:
        await asyncio.sleep(delay)  # Stagger requests
        
        async with semaphore:
            sections = await asyncio.to_thread(
                generate_sections,
                presentation_path=speaker.presentation_path,
                transcript_path=speaker.transcript_path,
                llm_model=llm_model,
                llm_api_key=llm_api_key,
            )
            
            return ProcessResult(
                section_count=len(sections),
                transcript_from="SOURCE",
                presentation_from="SOURCE"
            )
    
    # Create tasks with staggered delays to avoid rate limits
    tasks = [
        process_single_speaker(speaker, idx * 2.0)  # 2-second delays
        for idx, speaker in enumerate(speakers)
    ]
    
    return await asyncio.gather(*tasks)
```

## Cost Optimization

### Token Usage Monitoring

#### Cost Estimation
```python
def estimate_processing_cost(presentation_data: str, transcript_data: str,
                           model_name: str) -> float:
    """
    Estimate API cost before processing
    """
    # Rough token estimation (1 token ≈ 4 characters)
    input_tokens = (len(presentation_data) + len(transcript_data)) / 4
    
    # Estimate output tokens based on slide count
    slide_count = len(presentation_data.split("# Slide Page"))
    output_tokens = slide_count * 50  # ~50 tokens per section
    
    # Get model pricing
    pricing = MODEL_PRICING.get(model_name, {"input": 0.001, "output": 0.002})
    
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    
    return input_cost + output_cost
```

#### Model Selection Optimization
```python
def select_optimal_model(presentation_size: str) -> str:
    """
    Select most cost-effective model based on content size
    """
    if presentation_size == "small":  # < 5 slides
        return "gemini/gemini-2.0-flash"  # Cheapest option
    elif presentation_size == "medium":  # 5-20 slides
        return "anthropic/claude-3-haiku"  # Good balance
    else:  # > 20 slides
        return "openai/gpt-3.5-turbo"  # Better handling of long contexts
```

## Future Enhancements

### Advanced Processing Features

1. **Multi-Language Support**:
   - Language detection in PDFs
   - Model selection based on content language
   - Cross-language alignment capabilities

2. **Domain Specialization**:
   - Medical presentation processing
   - Technical documentation alignment
   - Educational content optimization

3. **Quality Improvements**:
   - Confidence scoring for generated sections
   - Human-in-the-loop validation workflows
   - Iterative refinement based on user feedback

4. **Performance Enhancements**:
   - Caching of processed content
   - Incremental processing for updated presentations
   - Smart batching and request optimization

The LLM integration system provides the intelligent foundation for transforming raw presentation materials into synchronized content that enables accurate voice-controlled navigation, while maintaining flexibility, reliability, and cost-effectiveness across multiple AI providers.