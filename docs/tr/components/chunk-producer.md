# Parça Üreticisi

`ChunkProducer`, işlenmiş sunum bölümlerinden gezilebilir metin segmentleri oluşturur, verimli gerçek zamanlı konuşma eşleştirmesini sağlar. Kaydırmalı pencere parçaları üretir ve optimal gezinme performansı için bağlamsal aday seçimi sunar.

## İçindekiler

- [Genel Bakış](#overview)
- [Parça Üretimi](#chunk-generation)
- [Kaydırmalı Pencere Algoritması](#sliding-window-algorithm)
- [Bağlamsal Aday Seçimi](#contextual-candidate-selection)
- [Performans Optimizasyonu](#performance-optimization)
- [Kullanım Örnekleri](#usage-examples)

## Genel Bakış

**Location**: `src/core/components/chunk_producer.py`

ChunkProducer, doğrusal sunum bölümlerini doğal konuşma kalıplarını temsil eden üst üste binen metin parçalarına dönüştürür. Bu parçalama yaklaşımı, sistemin konuşma parçacıklarını sunum içeriğiyle eşleştirmesini sağlarken bölüm sınırları arasında bağlamı korur.

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

## Parça Üretimi

### Kelime Düzeyi İşleme

ChunkProducer, kelime düzeyinde çalışarak ince ayrıntılı eşleştirme fırsatları yaratır:

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

1. **Kelime Çıkarımı**: Tüm bölümleri kelime düzeyinde token'lara düzleştir
2. **Kaynak İzleme**: Her kelime için bölüm referanslarını tut
3. **Pencere Oluşturma**: Belirtilen boyutta üst üste binen pencereler oluştur
4. **İçerik Normalizasyonu**: Tutarlı eşleştirme için metin normalizasyonu uygula
5. **Bölüm Toplama**: Her parça için katkıda bulunan tüm bölümleri izle

### Parça Yapısı

```python
@dataclass(frozen=True)
class Chunk:
    partial_content: str           # Normalized text content (12 words)
    source_sections: list[Section] # Contributing sections (sorted by index)
```

**Chunk Characteristics**:

- **Sabit Boyut**: Tutarlı işleme için 12 kelimelik pencereler
- **Üst Üste Binen**: Komşu parçalar 11 kelimeyi paylaşarak sorunsuz geçiş sağlar
- **Çok Bölümlü**: Tek bir parça birden fazla sunum bölümünü kapsayabilir
- **Normalleştirilmiş İçerik**: Güvenilir eşleştirme için tutarlı metin formatı

## Kaydırmalı Pencere Algoritması

### Pencere Boyutu Gerekçesi

```python
window_size: int = 12  # Default configuration
```

**Why 12 Words?**:

- **Konuşma Kalıpları**: Konuşma dilinde doğal ifade uzunluğu
- **Bağlam Koruma**: Anlamlı eşleştirme için yeterli bağlam
- **Performans Dengelemesi**: Doğruluk için yeterince büyük, hız için yeterince küçük
- **Tanıma Penceresi**: Tipik STT tanıma tamponlarıyla eşleşir

### Üst Üste Binen Strateji

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

- **Sorunsuz Geçişler**: Gezilebilir içerik arasında boşluk yok
- **Sınır İşleme**: Bölüm geçişlerini kapsayan konuşmayı yakalar
- **Yedeklilik**: Benzer içeriği eşleştirme şansı birden fazla
- **Hata Dayanıklılığı**: Tek bir parçanın eşleştirme hatalarının etkisini azaltır

### Bölümler Arası Parçalar

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

- **Doğal Sınırlar**: Slaytlar arasında doğal konuşma akışını eşleştirir
- **Geçiş Yakalama**: Konular arasında konuşmacı geçişlerini yönetir
- **Bağlam Sürekliliği**: Eşleştirme için anlatım akışını korur

## Bağlamsal Aday Seçimi

### Gezinme Bağlam Algoritması

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

1. **Pencere Tanımı**: Mevcut konumdan ±2-3 slayt
2. **Sınır Dahil Etme**: Tüm parça bölümleri pencere içinde olmalı
3. **Kenar Filtreleme**: Pencere kenarındaki tek bölümlü parçaları dışla
4. **Geçiş Kapsamı**: Aramayı bağlamsal olarak ilgili içeriğe sınırlar

### Bağlam Pencere Görselleştirme

```
Mevcut Konum: Slayt 10

Pencere: Slaytlar 8-13
    ┌─────┬─────┬─────┬──█──┬─────┬─────┐
    │  8  │  9  │ 10  │ 11 │ 12  │ 13  │
    └─────┴─────┴─────┴─█──┴─────┴─────┘
                     Mevcut

Aday Parçalar:
✓ 8-13 slaytları kapsayan parçalar
✓ Pencere içinde bölüm sınırlarını geçen parçalar
✗ Kenarlarda tek bölümlü parçalar (8, 13)
✗ Pencere sınırlarını aşan parçalar
```

**Bağlam Faydaları**:

- **Performans**: Benzerlik hesaplamalarını yaklaşık %70 azaltır
- **Doğruluk**: Alakasız uzak slaytlara atlamayı önler
- **Kullanıcı Deneyimi**: Mantıksal sunum akışını korur
- **Öngörülebilirlik**: Gezinme doğal ve beklenen hissettirir

### Kenar Durumları İşleme

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

## Performans Optimizasyonu

### Verimli Veri Yapıları

```python
# Pre-computed chunks for entire presentation
self.chunks = chunk_producer.generate_chunks(sections, window_size)

# Fast candidate selection using list comprehension
candidate_chunks = [chunk for chunk in self.chunks if meets_criteria(chunk)]
```

**Optimization Features**:

- **Ön Hesaplama**: Başlatma sırasında tüm parçaları bir kez üret
- **Bellek Verimliliği**: Parçalar arasında paylaşılan bölüm referansları
- **Hızlı Filtreleme**: Verimli aday seçme algoritmaları

### Bellek Yönetimi

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

- **Referans Paylaşımı**: Bölüm nesneleri birden fazla parça arasında paylaşılır
- **Değişmezlik**: Değişikliklerden kaynaklanan bellek sızıntılarını önler
- **Verimli Depolama**: Optimize edilmiş veri yapısı düzeni

### Hesaplamalı Verimlilik

```python
# Single normalization pass during chunk creation
partial_content=text_normalizer.normalize_text(" ".join(words))

# Efficient section sorting
source_sections=sorted(sections_in_window, key=lambda s: s.section_index)
```

## Kullanım Örnekleri

### Temel Parça Üretimi

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

### Bağlamsal Aday Seçimi

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

### Sunum Kontrolörü ile Entegrasyon

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

### Performans Testi

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

### Parça Analizi ve Hata Ayıklama

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

### Özel Pencere Boyutu Optimizasyonu

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

ChunkProducer, doğrusal sunum içeriğini doğal konuşma kalıplarına uyan üst üste binen, bağlamsal segmentlere dönüştürerek verimli gerçek zamanlı gezinmeyi sağlar. Kaydırmalı pencere yaklaşımı ve akıllı aday seçimi, doğru ve duyarlı ses kontrollü gezinme için temel oluşturur.