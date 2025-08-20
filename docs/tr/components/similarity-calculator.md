# Benzerlik Hesaplayıcı

`SimilarityCalculator`, gerçek zamanlı konuşmayı sunum içeriğiyle eşleştirmekten sorumlu çekirdek bileşendir. Birden çok benzerlik algoritmasını, optimal slayt navigasyon kararlarını belirlemek için gelişmiş puanlama mekanizmalarıyla birleştirir.

## İçindekiler

- [Genel Bakış](#genel-bakış)
- [Hibrit Benzerlik Yaklaşımı](#hibrit-benzerlik-yaklaşımı)
- [Benzerlik Birimleri](#benzerlik-birimleri)
- [Puan Normalizasyonu](#puan-normalizasyonu)
- [Performans Optimizasyonu](#performans-optimizasyonu)
- [Yapılandırma](#yapılandırma)
- [Kullanım Örnekleri](#kullanım-örnekleri)

## Genel Bakış

**Konum**: `src/core/components/similarity_calculator.py`

SimilarityCalculator, anlamsal anlayışı fonetik eşleştirme ile birleştiren ağırlıklı bir hibrit yaklaşımı uygular ve sağlam bir konuşmadan içeriğe eşleştirme sağlar. Bu çift yaklaşım, anlam temelli hizalamayı ve telaffuz temelli eşleştirmeyi aynı anda ele alarak sistemi konuşma tanıma hatalarına karşı dayanıklı hâle getirir.

```python
class SimilarityCalculator:
    def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
        self.semantic_weight = semantic_weight
        self.phonetic_weight = phonetic_weight
        self.semantic = Semantic()      # Sentence transformer embeddings
        self.phonetic = Phonetic()      # Metaphone + fuzzy matching
```

## Hibrit Benzerlik Yaklaşımı

### Mimari Genel Görünüm

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

### Çift Algoritma Stratejisi

Hesaplayıcı, konuşma eşleştirmenin farklı yönlerini ele almak için tamamlayıcı algoritmalar kullanır:

**Anlamsal Benzerlik (%40 ağırlık)**:

- **Amaç**: Anlamı ve bağlamı anlamak
- **Teknoloji**: Kosinüs benzerliğiyle cümle dönüştürücü gömme
- **Güçlü Yönleri**: Parafraz, eşanlamlılar, kavram eşleştirme
- **Kullanım Durumları**: "machine learning" ↔ "artificial intelligence algorithms"

**Fonetik Benzerlik (%60 ağırlık)**:

- **Amaç**: Telaffuz ve ses desenlerini eşleştirmek
- **Teknoloji**: Metaphone fonetik kodlaması + bulanık dize eşleştirme
- **Güçlü Yönleri**: Konuşma tanıma hataları, yanlış telaffuzları yönetir
- **Kullanım Durumları**: "write" ↔ "right", "there" ↔ "their"

### Ağırlık Gerekçesi

```python
# Default configuration favors phonetic matching
semantic_weight = 0.4  # 40% - meaning-based matching
phonetic_weight = 0.6  # 60% - sound-based matching
```

**Neden Fonetik Önem?**:

- **Konuşma Tanıma Hataları**: STT sistemleri sıklıkla fonetik olarak benzer ama anlamsal olarak farklı kelimeler üretir
- **Gerçek Zamanlı Kısıtlamalar**: Fonetik eşleştirme hesaplamada daha hızlıdır
- **Telaffuz Varyasyonları**: Aksanları, konuşma hızı çeşitliliklerini yönetir
- **Hata Dayanıklılığı**: Transkripsiyon hatalarına karşı daha dayanıklıdır

## Benzerlik Birimleri

### Anlamsal Benzerlik Birimi

**Konum**: `src/core/components/similarity_units/semantic.py`

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

**Anlamsal Özellikler**:

- **Yerel Model**: Sunum sırasında ağ bağımlılığı yok
- **Normalleştirilmiş Gömme**: Tutarlı benzerlik ölçeklendirmesi
- **Toplu İşleme**: Birden çok aday için verimli hesaplama
- **Kosinüs Benzerliği**: Standart anlamsal benzerlik ölçütü

### Fonetik Benzerlik Birimi

**Konum**: `src/core/components/similarity_units/phonetic.py`

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

**Fonetik Özellikler**:

- **Metaphone Kodlaması**: İngilizce için standart fonetik algoritma
- **LRU Önbellekleme**: Tekrarlanan hesaplamalar için performans iyileştirmesi
- **Bulanık Eşleştirme**: Verimli dize benzerliği için RapidFuzz
- **Normalleştirilmiş Puanlama**: Tutarlı ağırlıklandırma için 0.0-1.0 aralığı

## Puan Normalizasyonu

### Basit Normalizasyon Algoritması

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

**Normalizasyon Özellikleri**:

- **Eşik Filtreleme**: Yalnızca ≥ 0.5 puanlar geçerli kabul edilir
- **Min-Maks Ölçekleme**: 0.0-1.0 aralığına normalleştirir
- **Kenar Durumu İşleme**: Tek puanları ve boş sonuçları yönetir
- **Kalite Filtrelemesi**: Düşük kaliteli eşleşmeleri ortadan kaldırır

### Son Puan Hesaplaması

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

## Performans Optimizasyonu

### Önbellek Stratejisi

```python
# LRU caches for expensive operations
@lru_cache(maxsize=350)  # Metaphone encoding cache
@lru_cache(maxsize=350)  # Fuzzy ratio cache
```

**Önbellek Yararları**:

- **Azaltılmış Hesaplama**: Fonetik kodların yeniden hesaplanmasını önler
- **Bellek Verimliliği**: Sınırlı önbellek boyutu bellek sızıntılarını önler
- **Gerçek Zamanlı Performans**: Daha hızlı benzerlik hesaplamaları

### Toplu İşleme

```python
# Semantic similarity batch processing
embedding_input = [input_str] + [candidate.partial_content for candidate in candidates]
embeddings = self.model.encode(embedding_input, ...)  # Single model call
```

**Toplu İşleme Avantajları**:

- **GPU Kullanımı**: Gömme işlemleri için donanım kullanımını artırır
- **Azaltılmış Yük**: Daha az model başlatma maliyeti
- **Tutarlı İşleme**: Tüm adaylar için aynı model durumu

### Erken Sonlandırma

```python
# Threshold-based filtering eliminates poor matches early
valid_scores = [res.score for res in results if res.score >= 0.5]
if not valid_scores:
    return {id(res.chunk): 0.0 for res in results}  # Skip expensive normalization
```

## Yapılandırma

### Ağırlık Özelleştirme

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

### Performans Ayarı

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

## Kullanım Örnekleri

### Temel Benzerlik Hesaplaması

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

### Performans Testi

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

### Navigasyon ile Entegrasyon

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

### Özel Ağırlık Optimizasyonu

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

### Hata İşleme

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

SimilarityCalculator, doğruluk, performans ve güvenilirliği dengeleyen sofistike bir gerçek zamanlı konuşma eşleştirme yaklaşımıdır. Anlamsal anlayışı fonetik eşleştirme ile birleştirerek, konuşma tanıma hataları veya telaffuz varyasyonları olsa bile sağlam navigasyon kararları sağlar.