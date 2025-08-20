# Machine Learning Models

Moves integrates multiple machine learning models to provide intelligent presentation control. This includes local speech-to-text models, embedding models for semantic similarity, and cloud-based large language models for content generation.

## Table of Contents

- [Overview](#overview)
- [Speech-to-Text Models](#speech-to-text-models)
- [Embedding Models](#embedding-models)
- [Large Language Models](#large-language-models)
- [Model Integration](#model-integration)
- [Performance Optimization](#performance-optimization)
- [Model Management](#model-management)

## Overview

Moves employs a hybrid ML architecture that combines local models for privacy and performance with cloud models for advanced AI capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                     ML Model Architecture                   │
├─────────────────────────────────────────────────────────────┤
│ Local Models (Privacy & Performance)                       │
│  ┌─────────────────┐ ┌──────────────────┐                  │
│  │ Speech-to-Text  │ │ Embedding        │                  │
│  │ (ONNX)          │ │ (Sentence Trans) │                  │
│  └─────────────────┘ └──────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│ Cloud Models (Advanced AI)                                 │
│  ┌─────────────────┐                                       │
│  │ Large Language  │                                       │
│  │ Models (LiteLLM)│                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

## Speech-to-Text Models

### Model Location and Structure

**Location**: `src/core/components/ml_models/stt/`

```
ml_models/stt/
├── decoder.int8.onnx      # Decoder model (INT8 quantized)
├── encoder.int8.onnx      # Encoder model (INT8 quantized)
├── joiner.int8.onnx       # Joiner model (INT8 quantized)
└── tokens.txt             # Token vocabulary
```

### Sherpa-ONNX Integration

```python
from sherpa_onnx import OnlineRecognizer

self.recognizer = OnlineRecognizer.from_transducer(
    tokens=str(Path("src/core/components/ml_models/stt/tokens.txt")),
    encoder=str(Path("src/core/components/ml_models/stt/encoder.int8.onnx")),
    decoder=str(Path("src/core/components/ml_models/stt/decoder.int8.onnx")),
    joiner=str(Path("src/core/components/ml_models/stt/joiner.int8.onnx")),
    num_threads=8,
    decoding_method="greedy_search",
)
```

**Model Characteristics**:

- **Architecture**: Transducer-based neural network
- **Quantization**: INT8 for optimized performance
- **Deployment**: Local inference, no network dependency
- **Latency**: Real-time streaming recognition
- **Privacy**: Audio never leaves local system

### STT Model Performance

```python
# Performance configuration
self.frame_duration = 0.1      # 100ms processing frames
self.sample_rate = 16000       # 16kHz audio sampling
num_threads = 8                # Multi-threaded inference
```

**Performance Characteristics**:

- **Latency**: ~100-200ms from audio to text
- **Accuracy**: Optimized for conversational English
- **CPU Usage**: Moderate (scales with thread count)
- **Memory**: ~200MB model memory footprint
- **Throughput**: Real-time processing at 16kHz

### STT Usage Pattern

```python
def process_audio(self):
    while not self.shutdown_flag.is_set():
        # Get audio chunk from queue
        chunk = self.audio_queue.popleft()

        # Feed to recognition stream
        self.stream.accept_waveform(self.sample_rate, chunk)

        # Process available audio
        while self.recognizer.is_ready(self.stream):
            self.recognizer.decode_stream(self.stream)

        # Extract results
        if text := self.recognizer.get_result(self.stream):
            # Process recognized text
            self.handle_recognized_text(text)
```

## Embedding Models

### Model Location and Structure

**Location**: `src/core/components/ml_models/embedding/`

```
ml_models/embedding/
├── config_sentence_transformers.json    # Sentence Transformers config
├── config.json                          # Model configuration
├── model.safetensors                    # Model weights (SafeTensors format)
├── modules.json                         # Model architecture definition
├── README.md                            # Model documentation
├── sentence_bert_config.json            # BERT-specific configuration
├── special_tokens_map.json              # Special token mappings
├── tokenizer_config.json               # Tokenizer configuration
├── tokenizer.json                       # Tokenizer model
├── vocab.txt                           # Vocabulary file
└── 1_Pooling/                          # Pooling layer configuration
    └── config.json
```

### Sentence Transformers Integration

```python
from sentence_transformers import SentenceTransformer

class Semantic:
    def __init__(self):
        self.model = SentenceTransformer("src/core/components/ml_models/embedding")

    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        # Prepare batch input
        embedding_input = [input_str] + [candidate.partial_content for candidate in candidates]

        # Generate embeddings
        embeddings = self.model.encode(
            embedding_input,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        # Calculate similarities
        input_embedding = embeddings[0]
        candidate_embeddings = embeddings[1:]
        cosine_scores = np.dot(candidate_embeddings, input_embedding)
```

**Model Characteristics**:

- **Architecture**: Pre-trained sentence transformer model
- **Output**: 384 or 768-dimensional embeddings (model-dependent)
- **Normalization**: L2-normalized for cosine similarity
- **Language**: Optimized for English text
- **Privacy**: Local inference, no data transmission

### Embedding Model Performance

```python
# Performance optimization
embeddings = self.model.encode(
    texts,
    convert_to_numpy=True,        # NumPy for efficiency
    show_progress_bar=False,      # Disable UI overhead
    normalize_embeddings=True,    # Enable cosine similarity
    batch_size=32                 # Optimal batch size
)
```

**Performance Characteristics**:

- **Latency**: ~10-50ms per batch (depends on batch size)
- **Accuracy**: High semantic similarity accuracy
- **CPU Usage**: Moderate (can utilize GPU if available)
- **Memory**: ~500MB model memory footprint
- **Scalability**: Batch processing for efficiency

## Large Language Models

### LiteLLM Integration

Moves uses LiteLLM for unified access to multiple LLM providers:

```python
import instructor
from litellm import completion

# Initialize structured client
client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)

# Generate structured response
response = client.chat.completions.create(
    model=llm_model,
    api_key=llm_api_key,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    response_model=SectionsOutputModel,  # Pydantic model for structure
    temperature=0.2                      # Low temperature for consistency
)
```

### Supported LLM Providers

#### Primary Models

```python
# Google Gemini (Recommended)
model = "gemini/gemini-2.0-flash"      # Fast, cost-effective
model = "gemini/gemini-pro"            # Higher quality

# OpenAI
model = "gpt-4"                        # High quality
model = "gpt-3.5-turbo"               # Cost-effective

# Anthropic
model = "claude-3-opus"                # Highest quality
model = "claude-3-sonnet"              # Balanced
```

#### Alternative Providers

```python
# Cohere
model = "cohere/command-r-plus"

# Mistral
model = "mistral/mistral-large"

# Azure OpenAI
model = "azure/gpt-4"

# Local models (via Ollama)
model = "ollama/llama2"
```

### LLM Configuration and Usage

```python
def _call_llm(presentation_data: str, transcript_data: str, llm_model: str, llm_api_key: str):
    # Load processing instructions
    system_prompt = Path("src/data/llm_instruction.md").read_text(encoding="utf-8")

    # Create structured output model
    class SectionsOutputModel(BaseModel):
        class SectionItem(BaseModel):
            section_index: int = Field(..., ge=0)
            content: str = Field(...)

        sections: list[SectionItem] = Field(
            ...,
            min_items=slide_count,
            max_items=slide_count
        )

    # Generate response
    response = client.chat.completions.create(
        model=llm_model,
        api_key=llm_api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Presentation: {presentation_data}\nTranscript: {transcript_data}"}
        ],
        response_model=SectionsOutputModel,
        temperature=0.2  # Consistent output
    )

    return [item.content for item in response.sections]
```

## Model Integration

### Multi-Model Pipeline

```python
# Real-time processing pipeline
Audio Input → STT Model → Text Normalization → Embedding Model → Similarity Calculation → Navigation

# AI processing pipeline
PDF Files → Text Extraction → LLM Processing → Section Generation → Chunk Creation → Storage
```

### Model Coordination

```python
class PresentationController:
    def __init__(self, sections, start_section, window_size=12):
        # Local STT model
        self.recognizer = OnlineRecognizer.from_transducer(...)

        # Similarity calculator with embedding model
        self.similarity_calculator = SimilarityCalculator()

        # Pre-generated chunks from LLM processing
        self.chunks = chunk_producer.generate_chunks(sections, window_size)
```

### Model Lifecycle Management

```python
# Initialization phase (one-time setup)
1. Load STT models into memory
2. Initialize embedding model
3. Validate LLM API connectivity

# Processing phase (per speaker)
1. Extract PDFs using text processing
2. Generate sections using LLM
3. Create chunks for navigation
4. Store results for runtime use

# Runtime phase (during presentation)
1. Continuous STT processing
2. Real-time embedding generation
3. Similarity calculation and navigation
```

## Performance Optimization

### Local Model Optimization

```python
# STT Model Optimization
self.recognizer = OnlineRecognizer.from_transducer(
    # ... model paths ...
    num_threads=8,                    # Match CPU cores
    decoding_method="greedy_search"   # Fastest decoding
)

# Embedding Model Optimization
embeddings = self.model.encode(
    texts,
    batch_size=32,                    # Optimal batch size
    convert_to_numpy=True,            # NumPy performance
    normalize_embeddings=True         # Enable cosine similarity
)
```

### Cloud Model Optimization

```python
# LLM Optimization
response = client.chat.completions.create(
    model=llm_model,
    temperature=0.2,                  # Consistent output
    max_tokens=None,                  # No artificial limits
    timeout=60                        # Reasonable timeout
)
```

### Caching Strategies

```python
# Phonetic code caching
@lru_cache(maxsize=350)
def _get_phonetic_code(text: str) -> str:
    return metaphone(text).replace(" ", "")

# Embedding caching (for development)
def cache_embeddings(texts: list[str]) -> dict[str, np.ndarray]:
    cache = {}
    for text in texts:
        cache[text] = self.model.encode([text])[0]
    return cache
```

## Model Management

### Model Updates and Versioning

```python
# Model version tracking
MODEL_VERSIONS = {
    "stt": "sherpa-onnx-streaming-zipformer-en-2023-06-26",
    "embedding": "all-MiniLM-L6-v2",
    "llm": "dynamic"  # Based on user configuration
}

def check_model_compatibility():
    """Verify model versions are compatible"""
    # Implementation for model validation
    pass
```

### Model Health Monitoring

```python
def test_model_health():
    """Test all models for basic functionality"""

    # Test STT model
    try:
        recognizer = OnlineRecognizer.from_transducer(...)
        stream = recognizer.create_stream()
        # Basic functionality test
        stt_healthy = True
    except Exception:
        stt_healthy = False

    # Test embedding model
    try:
        model = SentenceTransformer("src/core/components/ml_models/embedding")
        test_embedding = model.encode(["test sentence"])
        embedding_healthy = len(test_embedding.shape) == 2
    except Exception:
        embedding_healthy = False

    # Test LLM connectivity
    try:
        # Basic API test with minimal request
        llm_healthy = test_llm_api()
    except Exception:
        llm_healthy = False

    return {
        "stt": stt_healthy,
        "embedding": embedding_healthy,
        "llm": llm_healthy
    }
```

### Performance Benchmarking

```python
import time

def benchmark_models():
    """Benchmark model performance"""

    results = {}

    # STT benchmark
    start = time.time()
    # Process sample audio
    results["stt_latency"] = time.time() - start

    # Embedding benchmark
    start = time.time()
    embeddings = embedding_model.encode(["test sentence"] * 10)
    results["embedding_throughput"] = 10 / (time.time() - start)

    # LLM benchmark
    start = time.time()
    # Make test API call
    results["llm_latency"] = time.time() - start

    return results
```

### Model Resource Management

```python
def optimize_for_hardware():
    """Configure models based on available hardware"""

    import psutil

    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total // (1024**3)

    # Configure STT threads
    stt_threads = min(8, cpu_count)

    # Configure embedding batch size
    if memory_gb >= 8:
        embedding_batch_size = 64
    elif memory_gb >= 4:
        embedding_batch_size = 32
    else:
        embedding_batch_size = 16

    return {
        "stt_threads": stt_threads,
        "embedding_batch_size": embedding_batch_size
    }
```

The ML models in Moves are carefully orchestrated to provide fast, accurate, and privacy-preserving presentation control. The combination of local models for real-time processing and cloud models for advanced AI capabilities delivers the best of both worlds - performance and intelligence.
