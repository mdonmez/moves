# Similarity Calculator

The `SimilarityCalculator` is the core component responsible for matching real-time speech against presentation content. It combines multiple similarity algorithms with sophisticated scoring mechanisms to determine optimal slide navigation decisions.

## Table of Contents

- [Overview](#overview)
- [Hybrid Similarity Approach](#hybrid-similarity-approach)
- [Similarity Units](#similarity-units)
- [Scoring Normalization](#scoring-normalization)
- [Performance Optimization](#performance-optimization)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)

## Overview

**Location**: `src/core/components/similarity_calculator.py`

The SimilarityCalculator implements a weighted hybrid approach that combines semantic understanding with phonetic matching to provide robust speech-to-content matching. This dual approach handles both meaning-based alignment and pronunciation-based matching, making the system resilient to speech recognition errors.

```python
class SimilarityCalculator:
    def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
        self.semantic_weight = semantic_weight
        self.phonetic_weight = phonetic_weight
        self.semantic = Semantic()      # Sentence transformer embeddings
        self.phonetic = Phonetic()      # Metaphone + fuzzy matching
```

## Hybrid Similarity Approach

### Architecture Overview

```
Real-time Speech Input
         │
    ┌────▼────┐
    │ Input   │
    │ Text    │
    └────┬────┘
         │
    ┌────▼────────────────┐
    │ Parallel Similarity │
    │ Calculation         │
    └────┬────────────────┘
         │
    ┌────▼────┐    ┌────▼────┐
    │Semantic │    │Phonetic │
    │40% wght │    │60% wght │
    └────┬────┘    └────┬────┘
         │              │
    ┌────▼──────────────▼────┐
    │ Score Normalization    │
    └────┬───────────────────┘
         │
    ┌────▼────┐
    │ Weighted│
    │ Final   │
    │ Score   │
    └─────────┘
```

### Dual Algorithm Strategy

The calculator uses complementary algorithms to handle different aspects of speech matching:

**Semantic Similarity (40% weight)**:

- **Purpose**: Understanding meaning and context
- **Technology**: Sentence transformer embeddings with cosine similarity
- **Strengths**: Handles paraphrasing, synonyms, concept matching
- **Use Cases**: "machine learning" ↔ "artificial intelligence algorithms"

**Phonetic Similarity (60% weight)**:

- **Purpose**: Matching pronunciation and sound patterns
- **Technology**: Metaphone phonetic encoding with fuzzy string matching
- **Strengths**: Handles speech recognition errors, mispronunciations
- **Use Cases**: "write" ↔ "right", "there" ↔ "their"

### Weight Rationale

```python
# Default configuration favors phonetic matching
semantic_weight = 0.4  # 40% - meaning-based matching
phonetic_weight = 0.6  # 60% - sound-based matching
```

**Why Phonetic Emphasis?**:

- **Speech Recognition Errors**: STT systems often produce phonetically similar but semantically different words
- **Real-Time Constraints**: Phonetic matching is computationally faster
- **Pronunciation Variations**: Handles accents, speaking speed variations
- **Error Resilience**: More robust to transcription mistakes

## Similarity Units

### Semantic Similarity Unit

**Location**: `src/core/components/similarity_units/semantic.py`

```python
class Semantic:
    def __init__(self):
        self.model = SentenceTransformer("src/core/components/ml_models/embedding")

    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        # Prepare inputs for batch processing
        embedding_input = [input_str] + [candidate.partial_content for candidate in candidates]

        # Generate embeddings
        embeddings = self.model.encode(
            embedding_input,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True  # Enable cosine similarity
        )

        # Calculate similarities
        input_embedding = embeddings[0]
        candidate_embeddings = embeddings[1:]
        cosine_scores = np.dot(candidate_embeddings, input_embedding)

        # Create results
        return [SimilarityResult(chunk=candidate, score=float(score))
                for candidate, score in zip(candidates, cosine_scores)]
```

**Semantic Features**:

- **Local Model**: No network dependency during presentations
- **Normalized Embeddings**: Consistent similarity scaling
- **Batch Processing**: Efficient computation for multiple candidates
- **Cosine Similarity**: Standard semantic similarity metric

### Phonetic Similarity Unit

**Location**: `src/core/components/similarity_units/phonetic.py`

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

    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        input_code = self._get_phonetic_code(input_str)
        results = []

        for candidate in candidates:
            candidate_code = self._get_phonetic_code(candidate.partial_content)
            score = self._calculate_fuzz_ratio(input_code, candidate_code)
            results.append(SimilarityResult(chunk=candidate, score=score))

        return sorted(results, key=lambda x: x.score, reverse=True)
```

**Phonetic Features**:

- **Metaphone Encoding**: Standard phonetic algorithm for English
- **LRU Caching**: Performance optimization for repeated calculations
- **Fuzzy Matching**: RapidFuzz for efficient string similarity
- **Normalized Scoring**: 0.0-1.0 range for consistent weighting

## Scoring Normalization

### Simple Normalization Algorithm

```python
def _normalize_scores_simple(self, results: list[SimilarityResult]) -> dict[int, float]:
    if not results:
        return {}

    # Filter valid scores (above threshold)
    valid_scores = [res.score for res in results if res.score >= 0.5]
    if not valid_scores:
        return {id(res.chunk): 0.0 for res in results}

    # Handle single score case
    min_val = min(valid_scores)
    max_val = max(valid_scores)
    if max_val == min_val:
        return {id(res.chunk): 1.0 if res.score >= 0.5 else 0.0 for res in results}

    # Min-max normalization
    score_range = max_val - min_val
    normalized = {}
    for res in results:
        if res.score >= 0.5:
            normalized[id(res.chunk)] = (res.score - min_val) / score_range
        else:
            normalized[id(res.chunk)] = 0.0

    return normalized
```

**Normalization Features**:

- **Threshold Filtering**: Only scores ≥ 0.5 are considered valid
- **Min-Max Scaling**: Normalizes to 0.0-1.0 range
- **Edge Case Handling**: Manages single scores and empty results
- **Quality Filtering**: Eliminates low-quality matches

### Final Score Calculation

```python
def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
    # Get similarity results from both algorithms
    semantic_results = self.semantic.compare(input_str, candidates)
    phonetic_results = self.phonetic.compare(input_str, candidates)

    # Normalize scores independently
    semantic_norm = self._normalize_scores_simple(semantic_results)
    phonetic_norm = self._normalize_scores_simple(phonetic_results)

    # Calculate weighted final scores
    final_results = []
    for candidate in candidates:
        candidate_id = id(candidate)
        sem_score = semantic_norm.get(candidate_id, 0.0)
        pho_score = phonetic_norm.get(candidate_id, 0.0)

        weighted_score = (
            self.semantic_weight * sem_score +
            self.phonetic_weight * pho_score
        )

        final_results.append(SimilarityResult(chunk=candidate, score=weighted_score))

    # Return sorted by score (highest first)
    return sorted(final_results, key=lambda x: x.score, reverse=True)
```

## Performance Optimization

### Caching Strategy

```python
# LRU caches for expensive operations
@lru_cache(maxsize=350)  # Metaphone encoding cache
@lru_cache(maxsize=350)  # Fuzzy ratio cache
```

**Cache Benefits**:

- **Reduced Computation**: Avoid recalculating phonetic codes
- **Memory Efficiency**: Bounded cache size prevents memory leaks
- **Real-Time Performance**: Faster similarity calculations

### Batch Processing

```python
# Semantic similarity batch processing
embedding_input = [input_str] + [candidate.partial_content for candidate in candidates]
embeddings = self.model.encode(embedding_input, ...)  # Single model call
```

**Batch Advantages**:

- **GPU Utilization**: Better hardware utilization for embeddings
- **Reduced Overhead**: Fewer model initialization costs
- **Consistent Processing**: Same model state for all candidates

### Early Termination

```python
# Threshold-based filtering eliminates poor matches early
valid_scores = [res.score for res in results if res.score >= 0.5]
if not valid_scores:
    return {id(res.chunk): 0.0 for res in results}  # Skip expensive normalization
```

## Configuration

### Weight Customization

```python
# Default configuration
calculator = SimilarityCalculator(
    semantic_weight=0.4,   # Meaning-based matching
    phonetic_weight=0.6    # Sound-based matching
)

# Custom configurations for different scenarios
fast_calculator = SimilarityCalculator(
    semantic_weight=0.2,   # Reduced semantic processing
    phonetic_weight=0.8    # Favor fast phonetic matching
)

precise_calculator = SimilarityCalculator(
    semantic_weight=0.7,   # Emphasize meaning
    phonetic_weight=0.3    # Reduce phonetic influence
)
```

### Performance Tuning

```python
# Cache size optimization
class Phonetic:
    @lru_cache(maxsize=500)  # Increase cache for longer presentations
    def _get_phonetic_code(self, text: str) -> str:
        # ...

# Threshold adjustment
def _normalize_scores_simple(self, results):
    valid_scores = [res.score for res in results if res.score >= 0.3]  # Lower threshold
```

## Usage Examples

### Basic Similarity Calculation

```python
from src.core.components.similarity_calculator import SimilarityCalculator
from src.data.models import Chunk

# Initialize calculator
calculator = SimilarityCalculator()

# Prepare input and candidates
input_text = "machine learning algorithms"
candidates = [
    Chunk(partial_content="artificial intelligence and ML techniques", source_sections=[]),
    Chunk(partial_content="deep learning neural networks", source_sections=[]),
    Chunk(partial_content="data science methodologies", source_sections=[])
]

# Calculate similarities
results = calculator.compare(input_str=input_text, candidates=candidates)

# Review results
for result in results:
    print(f"Score: {result.score:.3f} - Content: {result.chunk.partial_content}")
```

### Performance Testing

```python
import time

def test_similarity_performance():
    calculator = SimilarityCalculator()

    input_text = "That's right, we need to focus on the key concepts"
    candidates = [
        Chunk(partial_content="That's write, focus on key ideas", source_sections=[]),
        Chunk(partial_content="Correct approach to fundamental principles", source_sections=[]),
        Chunk(partial_content="Wrong direction for basic understanding", source_sections=[])
    ]

    start_time = time.time()
    results = calculator.compare(input_str=input_text, candidates=candidates)
    end_time = time.time()

    print(f"Calculation time: {(end_time - start_time) * 1000:.2f}ms")

    for result in results:
        print(f"Score: {result.score:.3f} - {result.chunk.partial_content}")

test_similarity_performance()
```

### Integration with Navigation

```python
def navigate_presentation(self):
    while not self.shutdown_flag.is_set():
        current_words = list(self.recent_words)

        if len(current_words) >= self.window_size:
            # Get navigation candidates
            candidate_chunks = chunk_producer.get_candidate_chunks(
                self.current_section, self.chunks
            )

            # Calculate similarities
            input_text = " ".join(current_words)
            similarity_results = self.similarity_calculator.compare(
                input_text, candidate_chunks
            )

            # Navigate to best match
            if similarity_results:
                best_result = similarity_results[0]
                target_section = best_result.chunk.source_sections[-1]
                self._navigate_to_section(target_section)
```

### Custom Weight Optimization

```python
def find_optimal_weights(test_data):
    """Find optimal semantic/phonetic weights for specific use case"""
    best_score = 0.0
    best_weights = (0.4, 0.6)

    # Test different weight combinations
    for semantic_weight in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        phonetic_weight = 1.0 - semantic_weight

        calculator = SimilarityCalculator(
            semantic_weight=semantic_weight,
            phonetic_weight=phonetic_weight
        )

        # Evaluate performance on test data
        score = evaluate_calculator(calculator, test_data)

        if score > best_score:
            best_score = score
            best_weights = (semantic_weight, phonetic_weight)

    print(f"Optimal weights: semantic={best_weights[0]}, phonetic={best_weights[1]}")
    return best_weights
```

### Error Handling

```python
def safe_similarity_calculation(calculator, input_text, candidates):
    try:
        results = calculator.compare(input_text, candidates)
        return results, None

    except Exception as e:
        error_msg = f"Similarity calculation failed: {e}"

        # Fallback: simple string matching
        fallback_results = []
        for candidate in candidates:
            # Basic substring matching as fallback
            score = 1.0 if input_text.lower() in candidate.partial_content.lower() else 0.0
            fallback_results.append(SimilarityResult(chunk=candidate, score=score))

        return sorted(fallback_results, key=lambda x: x.score, reverse=True), error_msg

# Usage
results, error = safe_similarity_calculation(calculator, input_text, candidates)
if error:
    print(f"Warning: {error}, using fallback matching")
```

The SimilarityCalculator represents a sophisticated approach to real-time speech matching that balances accuracy, performance, and reliability. By combining semantic understanding with phonetic matching, it provides robust navigation decisions even in the presence of speech recognition errors or pronunciation variations.
