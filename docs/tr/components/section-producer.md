# Bölüm Üreticisi

`SectionProducer`, sunum slaytlarını konuşmacı transkriptleriyle hizalayan AI destekli içerik üretiminden sorumludur. Navigasyon yeteneği olan bölümler oluşturmak için Büyük Dil Modellerini (LLM) kullanır ve bu sayede akıllı ses kontrollü sunum navigasyonu sağlanır.

## İçindekiler

- [Genel Bakış](#genel-bakış)
- [PDF İşleme](#pdf-işleme)
- [LLM Entegrasyonu](#llm-entegrasyonu)
- [İçerik Hizalama](#içerik-hizalama)
- [Veri Dönüştürme](#veri-dönüştürme)
- [Hata Yönetimi](#hata-yönetimi)
- [Kullanım Örnekleri](#kullanım-örnekleri)

## Genel Bakış

**Konum**: `src/core/components/section_producer.py`

SectionProducer, statik sunum içeriği ile dinamik konuşma kalıpları arasındaki boşluğu, her slayt için konuşmacının söylediği şeyleri temsil eden hizalanmış bölümler üreterek doldurur. Bu sayede sistem, gerçek zamanlı konuşmayı uygun slayt içeriğiyle eşleştirebilir.

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

## PDF İşleme

### Çift Modlu Çıkarma

SectionProducer, farklı çıkarma stratejileri gerektiren iki tür PDF içeriğini yönetir:

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

### Transkript İşleme

**Amaç**: Analiz için sürekli konuşma içeriğini çıkarmak

**İşlem**:

1. **Metin Çıkarma**: PDF sayfalarından tüm metni çıkar
2. **Normalleştirme**: Tüm içeriği sürekli bir metin haline getir
3. **Temizleme**: Aşırı boşlukları ve biçimlendirme kalıntılarını kaldır

**Sonuç**: Konuşmacının tam konuşmasını temsil eden tek bir sürekli dize

### Sunum İşleme

**Amaç**: İçerik hizalaması için slayt yapısını korumak

**İşlem**:

1. **Sayfa Sayfa İşleme**: Her slayttan içeriği ayrı ayrı çıkar
2. **Markdown Biçimlendirme**: Slayt başlıklarıyla içeriği yapılandır
3. **İçerik Temizleme**: Yapıyı korurken boşlukları normalleştir

**Sonuç**: Açık slayt sınırlarıyla yapılandırılmış markdown:

```markdown
# Slide Page 0

Welcome to our presentation on AI technology.

# Slide Page 1

Today we'll cover three main topics: machine learning, natural language processing, and computer vision.

# Slide Page 2

Let's start with machine learning fundamentals.
```

## LLM Entegrasyonu

### Yapılandırılmış Çıktı Oluşturma

SectionProducer, yapılandırılmış ve doğrulanmış çıktı sağlamak için `instructor` kütüphanesini LiteLLM ile birlikte kullanır:

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

**Doğrulama Özellikleri**:

- **Bölüm Sayısı Zorlaması**: Her slayt için tam bir bölüm garantiler
- **Dizin Doğrulaması**: Bölüm dizinlerinin 0’dan başlamasını teyit eder
- **İçerik Gereklilikleri**: Tüm bölümlerin içerik taşıdığını kontrol eder
- **Tür Güvenliği**: Tüm alanlar için güçlü tip tanımları

### LLM Çağrı Uygulaması

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

**LLM Yapılandırması**:

- **Düşük Sıcaklık**: Tutarlı, deterministik çıktı için 0.2
- **Yapılandırılmış Doğrulama**: Pydantic modelleri çıktı biçimini garanti eder
- **Hata Yönetimi**: Bağlam içeren kapsamlı hata raporlaması

## İçerik Hizalama

### AI İşleme Talimatları

**Konum**: `src/data/llm_instruction.md`

SectionProducer, LLM davranışını yönlendirmek için ayrıntılı talimatlar kullanır:

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

### Hizalama Süreci

1. **İçerik Analizi**: LLM, hem sunum yapısını hem de transkript içeriğini inceler
2. **Konu Eşleştirme**: Anlamsal benzerliğe göre transkript bölümlerini uygun slaytlarla eşler
3. **İçerik Çıkarma**: Her slayt için ilgili transkript pasajlarını alır
4. **Boşluk Doldurma**: İlgili transkript içeriği olmayan slaytlar için yeni içerik üretir
5. **Kalite Güvencesi**: Çıktının konuşmacının dili ve tonunu koruduğunu doğrular

### Çıktı Kalite Özellikleri

- **Dil Tutarlılığı**: Transkript dilini ve stilini yansıtır
- **İçerik Alaka Düzeyi**: Konuşma içeriğini slayt konularıyla hizalar
- **Tamamlayıcılık**: Her slaytın gezinilebilir içeriğe sahip olmasını sağlar
- **Konuşmacı Ses Tonu**: Transkriptin doğal konuşma kalıplarını sürdürür

## Veri Dönüştürme

### Bölüm Nesnesi Oluşturma

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

### Serileştirme Desteği

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

**Dönüştürme Özellikleri**:

- **İki Yönlü**: Nesneler ve serileştirilebilir formatlar arasında dönüşüm
- **Tür Güvenliği**: Dönüşümler sırasında tip bilgisi korunur
- **JSON Uyumluluğu**: Kalıcı depolama ve veri alışverişi sağlar

## Hata Yönetimi

### PDF İşleme Hataları

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

**Hata Senaryoları**:

- **Dosya Erişimi**: İzin veya yol problemlerini ele al
- **Bozuk PDF'ler**: Hatalı PDF dosyalarını yönet
- **Boş İçerik**: Çıkarılabilir metin olmayan PDF'leri ele al
- **Kodlama Sorunları**: Karakter kodlama problemlerini yönet

### LLM İşleme Hataları

```python
def _call_llm(...) -> list[str]:
    try:
        # LLM processing
        response = client.chat.completions.create(...)
        return [item.content for item in response.sections]
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e
```

**Hata Senaryoları**:

- **API Hataları**: Ağ sorunları, oran sınırlamaları, hizmet kesintileri
- **Kimlik Doğrulama**: Geçersiz API anahtarları veya süresi dolmuş kimlik bilgiler
- **Kota Aşımı**: Kullanım sınırı veya fatura problemleri
- **Doğrulama Başarısızlıkları**: Çıktının beklenen yapıya uymaması

### Kapsamlı Hata Bağlamı

Tüm hata yönetimi şunları sağlar:

- **İşlem Bağlamı**: Hangi aşamanın başarısız olduğu (PDF çıkarma, LLM işleme vb.)
- **Girdi Bilgisi**: Dosya yolları, model adları, veri özellikleri
- **Kök Neden**: Orijinal istisna detayları `from e` ile korunur
- **Eyleme Yönelik Mesajlar**: Neyin yanlış gittiğinin net açıklaması

## Kullanım Örnekleri

### Temel Bölüm Oluşturma

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

### Veri Sürekliliği

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

### Konuşmacı İşleme ile Entegrasyon

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

### Pratikte Hata Yönetimi

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

### Özel Model Yapılandırması

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

SectionProducer, sunum içeriğini doğal konuşma kalıplarıyla anlamak ve hizalamak için gerekli AI zekasını temsil eder. Sağlam PDF işleme, yapılandırılmış LLM entegrasyonu ve kapsamlı hata yönetimini birleştirerek akıllı ses kontrollü navigasyonun temelini oluşturur.