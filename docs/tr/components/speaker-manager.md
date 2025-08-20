# Konuşmacı Yöneticisi

`SpeakerManager`, konuşmacı profillerini yönetmek, sunum ve transkript dosyalarını işlemek ve gezilebilir bölümler oluşturmak için AI‑destekli işleme koordine etmekten sorumludur. Konuşmacı ile ilgili işlemler ve veri yönetimi için birincil arayüz olarak hizmet verir.

## İçindekiler

- [Genel Bakış](#genel-bakış)
- [Temel İşlevsellik](#temel-işlevsellik)
- [Konuşmacı Yaşam Döngüsü](#konuşmacı-yaşam-döngüsü)
- [Dosya Yönetimi](#dosya-yonetimi)
- [AI İşleme Boru Hattı](#ai-işleme-boru-hatti)
- [Veri Kalıcılaştırma](#veri-kalıcılaştırma)
- [Konuşmacı Çözümleme](#konuşmacı-çözümleme)
- [Hata Yönetimi](#hata-yonetimi)
- [Kullanım Örnekleri](#kullanım-örnekleri)

## Genel Bakış

**Konum**: `src/core/speaker_manager.py`

SpeakerManager, konuşmacı profillerinin oluşturulmasından AI işleme ve silinmeye kadar tam yaşam döngüsünü yönetir. Hem meta verileri (konuşmacı bilgileri) hem de ilişkili dosyaları (sunumlar ve transkriptler) kontrol ederken, gezilebilir içerik oluşturmak için AI servisleriyle koordinasyon sağlar.

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

## Temel İşlevsellik

### 1. Konuşmacı Profili Yönetimi

- **Oluşturma**: Kimlik oluşturma ile benzersiz konuşmacı profilleri üret
- **Değiştirme**: Sunum veya transkript dosyalarını güncelle
- **Silme**: Konuşmacı verisi ve dosyalarının temiz kaldırılması
- **Listeleme**: Durum bilgisiyle tüm kayıtlı konuşmacıları enumerate et

### 2. Dosya Sistemi İşlemleri

- **Dosya Kopyalama**: Sunum ve transkript dosyalarını yönet
- **Yol Çözümleme**: Hem kaynak hem de yerel dosya yollarını ele al
- **Depolama Organizasyonu**: Konuşmacı bazında yapılandırılmış dizin düzeni

### 3. AI Entegrasyonu Koordinasyonu

- **Toplu İşleme**: Birden fazla konuşmacıyı aynı anda ele al
- **Async İşlemler**: Doğru koordinasyonla bloklamayan işleme
- **Sonuç Toplama**: İşleme çıktılarının toplanması ve döndürülmesi

## Konuşmacı Yaşam Döngüsü

### 1. Oluşturma Aşaması

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

**Oluşturma Süreci**:

1. **Kimlik Oluşturma**: Benzersiz, insan‑okunur kimlik üret
2. **Yol Çözümleme**: Göreli yolları mutlak yollara çevir
3. **Doğrulama**: Gerekli dosyaların var ve erişilebilir olduğunu teyit et
4. **Kalıcılaştırma**: Konuşmacı meta verisini JSON olarak sakla
5. **Dizin Yapısı**: Düzenli konuşmacı‑özel dizinler oluştur

### 2. İşleme Aşaması

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

**İşleme Boru Hattı**:

1. **Dosya Hazırlama**: Kaynak dosyaları yerel olarak kopyala ve düzenle
2. **AI Üretimi**: LLM kullanarak hizalanmış bölümler oluştur
3. **Veri Depolama**: Gezinti için üretilen bölümleri kalıcıla
4. **Sonuç Raporlama**: İşleme çıktıları ve istatistikleri sağla

### 3. Çözümleme ve Alma

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

## Dosya Yönetimi

### Dosya Organizasyon Stratejisi

```
~/.moves/speakers/
└── {speaker-id}/              # örn., "john-doe-Ax9K2"
    ├── speaker.json           # Konuşmacı meta verisi
    ├── presentation.pdf       # Yerel sunum kopyası
    ├── transcript.pdf         # Yerel transkript kopyası
    └── sections.json          # İşleme sonrası oluşturulan gezinti bölümleri
```

### Dosya İşleme Mantığı

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

**Dosya Yönetimi Özellikleri**:

- **Kaynak Önceliği**: Kaynak dosyalar, önbelleğe alınmış yerel kopyalardan tercih edilir
- **İsim Normalizasyonu**: Tutarlı erişim için dosya adları standartlaştırılır
- **Geri Dönüş Stratejisi**: Kaynak dosyalar bulunamadığında yerel kopyalar kullanılır
- **Hata Yönetimi**: Eksik dosyalar için net hata mesajları sağlanır

## AI İşleme Boru Hattı

### Toplu İşleme Mimarisi

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

**İşleme Özellikleri**:

- **Eşzamanlı Çalıştırma**: Birden fazla konuşmacıyı aynı anda işle
- **Sırayla Gecikmeler**: API oran sınırlamasını önlemek için gecikmeli başlangıçlar
- **Hata İzolasyonu**: Bireysel hatalar diğer konuşmacıları etkilemez
- **Sonuç Toplama**: Toplu raporlama için çıktıları birleştir

### AI Entegrasyon Akışı

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

## Veri Kalıcılaştırma

### Konuşmacı Meta Verisi Biçimi

```json
{
  "name": "John Doe",
  "speaker_id": "john-doe-Ax9K2",
  "source_presentation": "/path/to/original/presentation.pdf",
  "source_transcript": "/path/to/original/transcript.pdf"
}
```

### Oluşturulan Bölümler Biçimi

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

### Veri Serileştirme

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

## Konuşmacı Çözümleme

### Esnek Arama Sistemi

SpeakerManager, hem kimlikleri hem de isimleri destekleyen esnek bir konuşmacı çözümlemesi sunar:

```python
# Resolution strategies
1. Direct ID match: "john-doe-Ax9K2" → exact speaker
2. Name match: "John Doe" → speaker with matching name
3. Partial match: "John" → speaker if unique name match
4. Ambiguity handling: Multiple matches → error with suggestions
```

### Çözümleme Örnekleri

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

## Hata Yönetimi

### Doğrulama ve Hata Önleme

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

### İşleme Hata Yönetimi

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

**Hata Yönetimi Prensipleri**:

- **Erken Doğrulama**: İşlemlerden önce ön koşulları kontrol et
- **Bağlamlı Hatalar**: Konuşmacı bağlamı içeren net hata mesajları sağla
- **Kaynak Temizliği**: Başarısızlıklarda uygun temizlik yap
- **Hata Yayma**: Ek bağlamla hataları üst katmanlara aktar

## Kullanım Örnekleri

### Temel Konuşmacı İşlemleri

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

### Dosya Yönetimi İşlemleri

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

### Toplu İşleme

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

### Temizleme İşlemleri

```python
# Delete speaker and all associated data
success = speaker_manager.delete(speaker)
if success:
    print(f"Speaker {speaker.name} deleted successfully")
else:
    print(f"Failed to delete speaker {speaker.name}")
```

### CLI Entegrasyonu

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

SpeakerManager, konuşmacı profillerini ve ilişkili verilerini yönetmek için sağlam bir temel sunar; ilk dosya yönetiminden AI işleme ve son temizlik aşamasına kadar her adımı ele alır. Esnek çözümleme sistemi ve kapsamlı hata yönetimi, hem programatik kullanım hem de CLI entegrasyonu için güvenilirliğini artırır.