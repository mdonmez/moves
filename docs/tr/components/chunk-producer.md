# Chunk Producer

The `ChunkProducer` creates navigable text segments from processed presentation sections, enabling efficient real-time speech matching. It generates sliding window chunks and provides contextual candidate selection for optimal navigation performance.

## Table of Contents

- [Overview](#overview)
- [Chunk Generation](#chunk-generation)
- [Sliding Window Algorithm](#sliding-window-algorithm)
- [Contextual Candidate Selection](#contextual-candidate-selection)
- [Performance Optimization](#performance-optimization)
- [Usage Examples](#usage-examples)

## Overview

**Location**: `src/core/components/chunk_producer.py`

The ChunkProducer transforms linear presentation sections into overlapping text chunks that represent natural speech patterns. This chunking approach enables the system to match speech fragments against presentation content while maintaining context across section boundaries.

```python
def generate_chunks(sections: list[Section], window_size: int = 12) -> list[Chunk]:
    # Create word-section pairs
    words_with_sources = [
        (word, section) for section in sections for word in section.content.split()
    ]

    # Generate sliding window chunks
    return [
        Chunk(
            partial_content=normalize_text(" ".join(words)),
            source_sections=sorted(unique_sections)
        )
        for i in range(len(words_with_sources) - window_size + 1)
    ]
```

## Chunk Generation

### Word-Level Processing

The ChunkProducer works at the word level to create fine-grained matching opportunities:

```python
def generate_chunks(sections: list[Section], window_size: int = 12) -> list[Chunk]:
    # Flatten sections into word-section pairs
    words_with_sources = [
        (word, section) for section in sections for word in section.content.split()
    ]

    # Validate minimum content
    if len(words_with_sources) < window_size:
        return []  # Not enough content for chunking

    # Generate overlapping chunks
    chunks = []
    for i in range(len(words_with_sources) - window_size + 1):
        # Extract window of words and their source sections
        window = words_with_sources[i : i + window_size]
        words = [word for word, _ in window]
        sections_in_window = {section for _, section in window}

        # Create chunk with normalized content
        chunk = Chunk(
            partial_content=text_normalizer.normalize_text(" ".join(words)),
            source_sections=sorted(sections_in_window, key=lambda s: s.section_index)
        )
        chunks.append(chunk)

    return chunks
```

**Processing Steps**:

1. **Word Extraction**: Flatten all sections into word-level tokens
2. **Source Tracking**: Maintain section references for each word
3. **Window Creation**: Generate overlapping windows of specified size
4. **Content Normalization**: Apply text normalization for consistent matching
5. **Section Aggregation**: Track all contributing sections per chunk

### Chunk Structure

```python
@dataclass(frozen=True)
class Chunk:
    partial_content: str           # Normalized text content (12 words)
    source_sections: list[Section] # Contributing sections (sorted by index)
```

**Chunk Characteristics**:

- **Fixed Size**: Consistent 12-word windows for uniform processing
- **Overlapping**: Adjacent chunks share 11 words for smooth transitions
- **Multi-Section**: Single chunk can span multiple presentation sections
- **Normalized Content**: Consistent text format for reliable matching

## Sliding Window Algorithm

### Window Size Rationale

```python
window_size: int = 12  # Default configuration
```

**Why 12 Words?**:

- **Speech Patterns**: Natural phrase length in conversational speech
- **Context Preservation**: Sufficient context for meaningful matching
- **Performance Balance**: Large enough for accuracy, small enough for speed
- **Recognition Window**: Matches typical STT recognition buffers

### Overlap Strategy

```
Section 1: "Welcome to our presentation on machine learning"
Section 2: "Today we will discuss neural networks and algorithms"

Chunks generated:
[0]: "Welcome to our presentation on machine learning Today we will discuss neural networks"
[1]: "to our presentation on machine learning Today we will discuss neural networks and"
[2]: "our presentation on machine learning Today we will discuss neural networks and algorithms"
...
```

**Overlap Benefits**:

- **Smooth Transitions**: No gaps between navigable content
- **Boundary Handling**: Captures speech that spans section transitions
- **Redundancy**: Multiple chances to match similar content
- **Error Resilience**: Reduces impact of individual chunk matching failures

### Cross-Section Chunks

```python
# Example chunk spanning sections
chunk = Chunk(
    partial_content="learning algorithms today we will explore deep neural networks",
    source_sections=[
        Section(content="...machine learning algorithms", section_index=5),
        Section(content="Today we will explore deep neural networks...", section_index=6)
    ]
)
```

**Cross-Section Features**:

- **Natural Boundaries**: Matches natural speech flow across slides
- **Transition Capture**: Handles speaker transitions between topics
- **Context Continuity**: Maintains narrative flow for matching

## Contextual Candidate Selection

### Navigation Context Algorithm

```python
def get_candidate_chunks(current_section: Section, all_chunks: list[Chunk]) -> list[Chunk]:
    idx = int(current_section.section_index)
    start, end = idx - 2, idx + 3  # ±2-3 slide window

    return [
        chunk for chunk in all_chunks
        if all(start <= int(s.section_index) <= end for s in chunk.source_sections)
        and not (
            len(chunk.source_sections) == 1
            and int(chunk.source_sections[0].section_index) in (start, end)
        )
    ]
```

**Selection Logic**:

1. **Window Definition**: ±2-3 slides from current position
2. **Boundary Inclusion**: All chunk sections must be within window
3. **Edge Filtering**: Exclude single-section chunks at window edges
4. **Navigation Scope**: Limits search to contextually relevant content

### Context Window Visualization

```
Current Position: Slide 10

Window: Slides 8-13
    ┌─────┬─────┬─────┬──█──┬─────┬─────┐
    │  8  │  9  │ 10  │ 11 │ 12  │ 13  │
    └─────┴─────┴─────┴─█──┴─────┴─────┘
                     Current

Candidate Chunks:
✓ Chunks spanning slides 8-13
✓ Chunks crossing section boundaries within window
✗ Single-section chunks at edges (8, 13)
✗ Chunks extending beyond window boundaries
```

**Context Benefits**:

- **Performance**: Reduces similarity calculations by ~70%
- **Accuracy**: Prevents jumping to unrelated distant slides
- **User Experience**: Maintains logical presentation flow
- **Predictability**: Navigation feels natural and expected

### Edge Case Handling

```python
# Handle presentation boundaries
if start < 0:
    start = 0
if end >= len(sections):
    end = len(sections) - 1

# Filter edge cases
valid_chunks = []
for chunk in filtered_chunks:
    # Skip single-section chunks at window edges
    if (len(chunk.source_sections) == 1 and
        chunk.source_sections[0].section_index in (start, end)):
        continue
    valid_chunks.append(chunk)
```

## Performance Optimization

### Efficient Data Structures

```python
# Pre-computed chunks for entire presentation
self.chunks = chunk_producer.generate_chunks(sections, window_size)

# Fast candidate selection using list comprehension
candidate_chunks = [chunk for chunk in self.chunks if meets_criteria(chunk)]
```

**Optimization Features**:

- **Pre-Computation**: Generate all chunks once during initialization
- **Memory Efficiency**: Shared section references across chunks
- **Fast Filtering**: Efficient candidate selection algorithms

### Memory Management

```python
# Immutable chunks prevent accidental modification
@dataclass(frozen=True)
class Chunk:
    partial_content: str
    source_sections: list[Section]

# Shared section objects across chunks
words_with_sources = [(word, section) for section in sections ...]
```

**Memory Benefits**:

- **Reference Sharing**: Section objects shared across multiple chunks
- **Immutability**: Prevents memory leaks from modification
- **Efficient Storage**: Optimized data structure layout

### Computational Efficiency

```python
# Single normalization pass during chunk creation
partial_content=text_normalizer.normalize_text(" ".join(words))

# Efficient section sorting
source_sections=sorted(sections_in_window, key=lambda s: s.section_index)
```

## Usage Examples

### Basic Chunk Generation

```python
from src.core.components.chunk_producer import generate_chunks
from src.data.models import Section

# Create presentation sections
sections = [
    Section(content="Welcome to our presentation on machine learning", section_index=0),
    Section(content="Today we will discuss neural networks and deep learning", section_index=1),
    Section(content="Let's start with basic concepts and fundamentals", section_index=2)
]

# Generate chunks
chunks = generate_chunks(sections, window_size=12)

print(f"Generated {len(chunks)} chunks from {len(sections)} sections")
for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
    print(f"Chunk {i}: {chunk.partial_content}")
    print(f"  Spans sections: {[s.section_index for s in chunk.source_sections]}")
```

### Contextual Candidate Selection

```python
from src.core.components.chunk_producer import get_candidate_chunks

# Current presentation position
current_section = sections[1]  # Section index 1

# Get contextual candidates
candidate_chunks = get_candidate_chunks(current_section, chunks)

print(f"Current section: {current_section.section_index}")
print(f"Candidates: {len(candidate_chunks)} chunks")

for chunk in candidate_chunks:
    section_indices = [s.section_index for s in chunk.source_sections]
    print(f"  Candidate spans sections {section_indices}")
    print(f"    Content: {chunk.partial_content[:50]}...")
```

### Integration with Presentation Controller

```python
class PresentationController:
    def __init__(self, sections, start_section, window_size=12):
        # Pre-generate all chunks
        self.sections = sections
        self.current_section = start_section
        self.chunks = chunk_producer.generate_chunks(sections, window_size)

    def navigate_presentation(self):
        while not self.shutdown_flag.is_set():
            # Get contextual candidates for current position
            candidate_chunks = chunk_producer.get_candidate_chunks(
                self.current_section, self.chunks
            )

            if not candidate_chunks:
                continue  # No valid candidates

            # Calculate similarities against candidates
            input_text = " ".join(self.recent_words)
            similarity_results = self.similarity_calculator.compare(
                input_text, candidate_chunks
            )

            # Navigate to best match
            best_chunk = similarity_results[0].chunk
            target_section = best_chunk.source_sections[-1]
            self._navigate_to_section(target_section)
```

### Performance Testing

```python
import time

def test_chunk_generation_performance():
    # Create large presentation
    sections = []
    for i in range(100):
        content = f"This is section {i} with content about topic {i} and related concepts"
        sections.append(Section(content=content, section_index=i))

    # Test chunk generation performance
    start_time = time.time()
    chunks = generate_chunks(sections, window_size=12)
    generation_time = time.time() - start_time

    print(f"Generated {len(chunks)} chunks in {generation_time:.3f} seconds")
    print(f"Performance: {len(chunks) / generation_time:.0f} chunks/second")

    # Test candidate selection performance
    current_section = sections[50]  # Middle section

    start_time = time.time()
    candidates = get_candidate_chunks(current_section, chunks)
    selection_time = time.time() - start_time

    print(f"Selected {len(candidates)} candidates in {selection_time:.3f} seconds")

test_chunk_generation_performance()
```

### Chunk Analysis and Debugging

```python
def analyze_chunks(chunks):
    """Analyze chunk characteristics for debugging"""

    # Basic statistics
    total_chunks = len(chunks)
    single_section_chunks = sum(1 for c in chunks if len(c.source_sections) == 1)
    multi_section_chunks = total_chunks - single_section_chunks

    print(f"Chunk Analysis:")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Single-section: {single_section_chunks} ({single_section_chunks/total_chunks:.1%})")
    print(f"  Multi-section: {multi_section_chunks} ({multi_section_chunks/total_chunks:.1%})")

    # Section span analysis
    max_sections = max(len(c.source_sections) for c in chunks)
    section_span_dist = {}
    for c in chunks:
        span = len(c.source_sections)
        section_span_dist[span] = section_span_dist.get(span, 0) + 1

    print(f"  Section span distribution:")
    for span in sorted(section_span_dist.keys()):
        count = section_span_dist[span]
        print(f"    {span} sections: {count} chunks ({count/total_chunks:.1%})")

    # Content length analysis
    content_lengths = [len(c.partial_content.split()) for c in chunks]
    avg_length = sum(content_lengths) / len(content_lengths)
    print(f"  Average chunk length: {avg_length:.1f} words")

# Usage
chunks = generate_chunks(sections, window_size=12)
analyze_chunks(chunks)
```

### Custom Window Size Optimization

```python
def find_optimal_window_size(sections, test_queries):
    """Find optimal window size for specific content"""

    results = {}
    for window_size in range(8, 20, 2):  # Test 8, 10, 12, 14, 16, 18
        chunks = generate_chunks(sections, window_size)

        # Simulate navigation accuracy
        correct_matches = 0
        for query, expected_section in test_queries:
            # Test matching logic here
            candidates = get_candidate_chunks(sections[expected_section], chunks)
            # ... similarity calculation ...
            if best_match_section == expected_section:
                correct_matches += 1

        accuracy = correct_matches / len(test_queries)
        results[window_size] = {
            'accuracy': accuracy,
            'chunk_count': len(chunks),
            'chunks_per_section': len(chunks) / len(sections)
        }

        print(f"Window size {window_size}: {accuracy:.2%} accuracy, {len(chunks)} chunks")

    # Find best performing window size
    best_window = max(results.keys(), key=lambda k: results[k]['accuracy'])
    print(f"Optimal window size: {best_window}")
    return best_window
```

The ChunkProducer enables efficient real-time navigation by transforming linear presentation content into overlapping, contextual segments that match natural speech patterns. Its sliding window approach combined with intelligent candidate selection provides the foundation for accurate and responsive voice-controlled navigation.
