# Veri Modelleri

moves, sistemdeki tüm varlıkların yapı ve ilişkilerini tanımlayan kapsamlı bir veri modeli seti kullanır. Bu modeller tip güvenliği, doğrulama ve farklı sistem bileşenleri arasındaki net arayüzler sağlar.

## İçindekiler

- [Genel Bakış](#overview)
- [Temel Veri Modelleri](#core-data-models)
- [Tür Takma Adları](#type-aliases)
- [Model İlişkileri](#model-relationships)
- [Serileştirme Desteği](#serialization-support)
- [Kullanım Örnekleri](#usage-examples)

## Genel Bakış

**Konum**: `src/data/models.py`

Veri modelleri modülü, Python veri sınıflarını kullanarak tüm temel veri yapılarını tanımlar; uygun yerlerde değişmezlik, tip güvenliği ve sistem varlıklarının net belgelenmesini sağlar. Bu modeller, uygulama boyunca veri akışının temelini oluşturur.

```python
from dataclasses import dataclass
from typing import Literal
from pathlib import Path

# Type aliases for clarity and consistency
SpeakerId = str
HistoryId = str
```

## Temel Veri Modelleri

### Section Model

```python
@dataclass(frozen=True)
class Section:
    content: str
    section_index: int
```

**Amaç**: Tek bir sunum slaytını, ona karşılık gelen konuşma içeriğiyle birlikte temsil eder.

**Alanlar**:

- **content**: Bu slaytla ilişkili konuşma içeriği (AI tarafından üretilir)
- **section_index**: Sunumdaki slayt konumunu gösteren sıfır‑tabanlı indeks

**Özellikler**:

- **Değişmez**: `frozen=True` oluşturulduktan sonra değişikliği engeller
- **Gezinme Birimi**: Sunum gezinmesi için birincil birim
- **AI Tarafından Üretilmiş**: İçerik LLM işleme ile oluşturulmuştur

**Örnek**:

```python
section = Section(
    content="Welcome to our presentation on machine learning and its applications in modern technology.",
    section_index=0
)
```

### Chunk Model

```python
@dataclass(frozen=True)
class Chunk:
    partial_content: str
    source_sections: list[Section]
```

**Amaç**: Gerçek zamanlı konuşma eşleştirme için kayan bir metin penceresini temsil eder.

**Alanlar**:

- **partial_content**: Normalleştirilmiş metin içeriği (genellikle 12 kelime)
- **source_sections**: Katkıda bulunan bölümlerin listesi (indekse göre sıralanmış)

**Özellikler**:

- **Değişmez**: Gezinme sırasında kazara değişikliği önler
- **Çoklu Bölüm**: Birden fazla sunum bölümü arasında yayılabilir
- **Normalleştirilmiş**: Tutarlı eşleştirme için işlenmiş içerik

**Örnek**:

```python
chunk = Chunk(
    partial_content="machine learning algorithms today we will explore deep neural networks",
    source_sections=[section1, section2]  # Spans two sections
)
```

### Speaker Model

```python
@dataclass
class Speaker:
    name: str
    speaker_id: SpeakerId
    source_presentation: Path
    source_transcript: Path
```

**Amaç**: İlgili sunum materyalleriyle birlikte bir konuşmacı profilini temsil eder.

**Alanlar**:

- **name**: İnsan tarafından okunabilir konuşmacı adı
- **speaker_id**: Tekil tanımlayıcı (isim + rastgele ekten oluşturulur)
- **source_presentation**: Orijinal sunum PDF dosyasının yolu
- **source_transcript**: Orijinal transkript PDF dosyasının yolu

**Özellikler**:

- **Değiştirilebilir**: Sunum ve transkript yollarının düzenlenmesine izin verir
- **Dosya Yönetimi**: Hem kaynak hem de yerel dosya konumlarını takip eder
- **Tekil Kimlik**: Her konuşmacının küresel olarak benzersiz bir kimliği vardır

**Örnek**:

```python
speaker = Speaker(
    name="Dr. Sarah Johnson",
    speaker_id="dr-sarah-johnson-Ax9K2",
    source_presentation=Path("/path/to/presentation.pdf"),
    source_transcript=Path("/path/to/transcript.pdf")
)
```

### SimilarityResult Model

```python
@dataclass(frozen=True)
class SimilarityResult:
    chunk: Chunk
    score: float
```

**Amaç**: Konuşma ile içerik arasındaki benzerlik hesabının sonucunu temsil eder.

**Alanlar**:

- **chunk**: Karşılaştırılan aday parça
- **score**: Benzerlik puanı (0.0‑1.0, yüksek değeri daha iyidir)

**Özellikler**:

- **Değişmez**: Sonuçların değiştirilmesini engeller
- **Sıralanabilir**: Genellikle puana göre sıralanarak derecelendirilir
- **Geçiş Kararı**: Slayt geçişlerini belirlemek için kullanılır

**Örnek**:

```python
result = SimilarityResult(
    chunk=candidate_chunk,
    score=0.85  # High similarity
)
```

### Settings Model

```python
@dataclass
class Settings:
    model: str
    key: str
```

**Amaç**: Sistem yapılandırma ayarlarını temsil eder.

**Alanlar**:

- **model**: LLM model tanımlayıcısı (örn. "gemini/gemini-2.0-flash")
- **key**: LLM sağlayıcısı için API anahtarı

**Özellikler**:

- **Değiştirilebilir**: Çalışma zamanında yapılandırma değişikliklerine izin verir
- **Şablon Tabanlı**: Ayar şablonundan başlatılır
- **Doğrulama**: Mevcut modeller ve anahtar formatlarıyla doğrulanır

**Örnek**:

```python
settings = Settings(
    model="gemini/gemini-2.0-flash",
    key="your-api-key-here"
)
```

### ProcessResult Model

```python
@dataclass(frozen=True)
class ProcessResult:
    section_count: int
    transcript_from: Literal["SOURCE", "LOCAL"]
    presentation_from: Literal["SOURCE", "LOCAL"]
```

**Amaç**: Konuşmacı işleme işleminin sonucunu temsil eder.

**Alanlar**:

- **section_count**: İşlemeden üretilen bölüm sayısı
- **transcript_from**: Kullanılan transkript dosyasının kaynağı
- **presentation_from**: Kullanılan sunum dosyasının kaynağı

**Özellikler**:

- **Değişmez**: İşleme sonrası sonuçlar değiştirilemez
- **Dosya İzleme**: İşleme için hangi dosyaların kullanıldığını kaydeder
- **Metrikler**: Nicel işlem sonuçları sağlar

**Örnek**:

```python
result = ProcessResult(
    section_count=25,
    transcript_from="SOURCE",
    presentation_from="LOCAL"
)
```

## Tür Takma Adları

### Konuşmacı ve Geçmiş Tanımlayıcıları

```python
SpeakerId = str  # e.g., "john-doe-Ax9K2"
HistoryId = str  # e.g., "20240120_14-30-25"
```

**Amaç**: Dize tanımlayıcılara anlamsal bir anlam kazandırmak ve tip denetimini mümkün kılmaktır.

**Faydalar**:

- **Tip Güvenliği**: Farklı kimlik türlerinin karışmasını önler
- **Kod Açıklığı**: Fonksiyon imzalarını daha açıklayıcı hâle getirir
- **IDE Desteği**: Otomatik tamamlama ve hata tespiti iyileşir
- **Gelecek Uzantıları**: Doğrulama eklemek ya da temel tipleri değiştirmek kolaydır

**Kullanım Örnekleri**:

```python
def resolve_speaker(speaker_id: SpeakerId) -> Speaker: ...
def create_history_entry(history_id: HistoryId) -> None: ...
```

## Model İlişkileri

### Hiyerarşik Yapı

```
Speaker
├── Has presentation PDF
├── Has transcript PDF
├── Generates → Sections (via AI processing)
└── Creates → Chunks (from Sections)

Section
├── Has content (aligned speech)
├── Has index (slide position)
└── Contributes to → Chunks (via sliding window)

Chunk
├── Has partial_content (normalized text)
├── References → source_sections
└── Used in → SimilarityResults

SimilarityResult
├── References → Chunk
├── Has score (similarity measure)
└── Used for → Navigation decisions
```

### Veri Akışı İlişkileri

```python
# Processing flow
Speaker → PDF files → AI processing → Sections → Chunks → SimilarityResults → Navigation

# Example flow
speaker = Speaker(...)
sections = generate_sections(speaker.source_presentation, speaker.source_transcript)
chunks = generate_chunks(sections)
results = similarity_calculator.compare(speech, chunks)
best_match = results[0]  # Highest scoring result
```

### Referans Bütünlüğü

- **Sections**: Kendi içinde tamdır, dış referans içermez
- **Chunks**: Kendilerini oluşturan bölümleri referans alır
- **SimilarityResults**: Değerlendirdikleri parçaları referans alır
- **Speakers**: Dosya yollarını referans alır (geçersiz hâle gelebilir)

## Serileştirme Desteği

### JSON Serileştirme

Çoğu model, kalıcılık için JSON serileştirmesini destekler:

```python
# Section serialization
section_dict = {
    "content": section.content,
    "section_index": section.section_index
}

# Speaker serialization (with Path conversion)
speaker_dict = {
    "name": speaker.name,
    "speaker_id": speaker.speaker_id,
    "source_presentation": str(speaker.source_presentation),  # Path → string
    "source_transcript": str(speaker.source_transcript)
}
```

### Serileştirme Yardımcıları

```python
# In section_producer.py
def convert_to_list(section_objects: list[Section]) -> list[dict[str, str | int]]:
    return [
        {"content": s.content, "section_index": s.section_index}
        for s in section_objects
    ]

def convert_to_objects(section_list: list[dict[str, str | int]]) -> list[Section]:
    return [
        Section(
            content=cast(str, s_dict["content"]),
            section_index=cast(int, s_dict["section_index"]),
        )
        for s_dict in section_list
    ]
```

### Dosya Biçimi Örnekleri

**Speaker JSON** (`~/.moves/speakers/{id}/speaker.json`):

```json
{
  "name": "Dr. Sarah Johnson",
  "speaker_id": "dr-sarah-johnson-Ax9K2",
  "source_presentation": "/Users/sarah/presentations/ml-intro.pdf",
  "source_transcript": "/Users/sarah/transcripts/ml-speech.pdf"
}
```

**Sections JSON** (`~/.moves/speakers/{id}/sections.json`):

```json
[
  {
    "content": "Welcome to our comprehensive presentation on machine learning fundamentals.",
    "section_index": 0
  },
  {
    "content": "Today we'll explore neural networks, deep learning, and practical applications.",
    "section_index": 1
  }
]
```

## Kullanım Örnekleri

### Modelleri Oluşturma ve Kullanma

```python
from src.data.models import Section, Chunk, Speaker, SimilarityResult
from pathlib import Path

# Create a presentation section
section = Section(
    content="Machine learning is transforming how we approach data analysis",
    section_index=0
)

# Create a speaker profile
speaker = Speaker(
    name="Prof. Data Science",
    speaker_id="prof-data-science-Xy5Z8",
    source_presentation=Path("./ml-presentation.pdf"),
    source_transcript=Path("./ml-transcript.pdf")
)

# Create chunks for navigation
chunk = Chunk(
    partial_content="machine learning transforming data analysis techniques",
    source_sections=[section]
)

# Similarity results for navigation decisions
result = SimilarityResult(chunk=chunk, score=0.92)
```

### Model Doğrulama ve Tip Güvenliği

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type checking benefits
    def process_speaker(speaker_id: SpeakerId) -> list[Section]:
        # IDE knows speaker_id is meant to be a speaker identifier
        pass

    def navigate_to_section(section_index: int) -> None:
        # Clear parameter types
        pass
```

### Değişmez Modellerle Çalışma

```python
# Sections and Chunks are immutable
section = Section(content="Original content", section_index=0)

# This would raise an error:
# section.content = "Modified content"  # FrozenInstanceError

# Instead, create new instances
updated_section = Section(
    content="Updated content",
    section_index=section.section_index
)
```

### Model Karşılaştırma ve Sıralama

```python
# Sections can be sorted by index
sections = [section2, section0, section1]
sorted_sections = sorted(sections, key=lambda s: s.section_index)

# Similarity results are typically sorted by score
results = [
    SimilarityResult(chunk1, 0.75),
    SimilarityResult(chunk2, 0.90),
    SimilarityResult(chunk3, 0.65)
]
best_results = sorted(results, key=lambda r: r.score, reverse=True)
```

### İş Mantığıyla Entegrasyon

```python
def find_target_section(similarity_results: list[SimilarityResult]) -> Section | None:
    """Find target section from similarity results"""
    if not similarity_results:
        return None

    best_result = similarity_results[0]  # Highest scored result
    best_chunk = best_result.chunk

    # Navigate to the last section in the chunk (typical behavior)
    target_section = best_chunk.source_sections[-1]
    return target_section

def calculate_navigation_distance(current: Section, target: Section) -> int:
    """Calculate slides to navigate"""
    return target.section_index - current.section_index
```

### Modellerle Hata Yönetimi

```python
def safe_section_creation(content: str, index: int) -> Section | None:
    """Safely create section with validation"""
    try:
        if not content.strip():
            raise ValueError("Section content cannot be empty")
        if index < 0:
            raise ValueError("Section index must be non-negative")

        return Section(content=content, section_index=index)
    except ValueError as e:
        print(f"Invalid section data: {e}")
        return None

# Usage
section = safe_section_creation("Valid content", 0)
if section:
    print(f"Created section {section.section_index}")
```

Veri modelleri, moves sisteminde tip‑güvenli, güvenilir veri işleme için sağlam bir temel sağlar. Açık yapıları ve değişmez özellikleri, hataları önlerken kod netliğini ve sürdürülebilirliğini artırır.
