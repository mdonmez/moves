# Mimari Genel Bakış

moves, ses tanıma, doğal dil işleme ve makine öğrenimini birleştirerek akıllı sunum navigasyonu sağlayan modüler, gerçek zamanlı bir sistem olarak tasarlanmıştır. Bu belge, sistem mimarisi, tasarım kalıpları ve bileşen etkileşimlerinin kapsamlı bir genel bakışını sunar.

## İçindekiler

- [Sistem Mimarisi](#system-architecture)
- [Tasarım Prensipleri](#design-principles)
- [Temel Bileşenler](#core-components)
- [Veri Akışı](#data-flow)
- [İşleme Boru Hattı](#processing-pipeline)
- [Gerçek Zamanlı İşlemler](#real-time-operations)
- [Makine Öğrenimi Entegrasyonu](#machine-learning-integration)
- [Veri Depolama](#data-storage)
- [İş Parçacığı Modeli](#threading-model)
- [Hata Yönetimi](#error-handling)
- [Performans Düşünceleri](#performance-considerations)

## Sistem Mimarisi

moves, net bir sorumluluk ayrımıyla katmanlı bir mimari izler:

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface Layer                      │
│                      (app.py)                              │
├─────────────────────────────────────────────────────────────┤
│                   Core Business Logic                       │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Presentation    │ │ Speaker          │ │ Settings     │ │
│  │ Controller      │ │ Manager          │ │ Editor       │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Processing Components                     │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Section         │ │ Similarity       │ │ Chunk        │ │
│  │ Producer        │ │ Calculator       │ │ Producer     │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    ML/AI Integration                        │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Speech-to-Text  │ │ Embedding        │ │ LLM          │ │
│  │ (Local ONNX)    │ │ Models           │ │ (Cloud API)  │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     Utility Layer                          │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Data Handler    │ │ Text             │ │ Logger       │ │
│  │                 │ │ Normalizer       │ │              │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    External Interfaces                     │
│  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Audio Input     │ │ File System      │ │ LLM APIs     │ │
│  │ (Microphone)    │ │ (Local Storage)  │ │ (Network)    │ │
│  └─────────────────┘ └──────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Tasarım Prensipleri

### 1. Modüler Mimari

- **Tek Sorumluluk**: Her bileşen tek bir açık amaca sahiptir
- **Gevşek Bağlantı**: Bileşenler iyi tanımlanmış arayüzler aracılığıyla etkileşir
- **Yüksek Uyum**: İlgili işlevsellik bir arada gruplanır

### 2. Gerçek Zamanlı İşleme

- **Çoklu İş Parçacığı**: Ses, işleme ve navigasyon için ayrı iş parçacıkları
- **Engellemesiz İşlemler**: Mümkün olduğunda eşzamanlı işleme
- **Düşük Gecikme**: Yanıt veren kullanıcı deneyimi için optimize edilmiş

### 3. Yapılandırılabilirlik

- **Ayar Yönetimi**: Merkezi yapılandırma sistemi
- **Model Esnekliği**: Çoklu AI modelleri ve sağlayıcıları desteği
- **Genişletilebilirlik**: Yeni benzerlik algoritmaları ve işlemcileri eklemek kolay

### 4. Veri Kalıcılığı

- **Yapılandırılmış Depolama**: Konuşmacılar ve oturumlar için düzenli veri hiyerarşisi
- **JSON Serileştirme**: İnsan tarafından okunabilir veri formatları
- **Dosya Sistemi Entegrasyonu**: Verimli dosya işleme ve yönetimi

## Temel Bileşenler

### 1. Sunum Denetleyicisi

**Location**: `src/core/presentation_controller.py`

Gerçek zamanlı navigasyon sisteminin kalbi:

```python
class PresentationController:
    def __init__(self, sections, start_section, window_size=12):
        # Real-time audio processing
        self.recognizer = OnlineRecognizer.from_transducer(...)
        self.similarity_calculator = SimilarityCalculator()

        # Navigation state
        self.current_section = start_section
        self.recent_words = deque(maxlen=window_size)

        # Threading coordination
        self.shutdown_flag = threading.Event()
        self.navigator_working = False
```

**Ana Sorumluluklar**:

- Gerçek zamanlı ses yakalama ve konuşma tanıma
- Sunum içeriğine karşı sürekli benzerlik hesaplaması
- Konuşma eşleşmelerine dayanarak otomatik slayt navigasyonu
- Manuel klavye geçersiz kılma desteği
- İş parçacığı koordinasyonu ve yaşam döngüsü yönetimi

### 2. Konuşmacı Yöneticisi

**Location**: `src/core/speaker_manager.py`

Konuşmacı profillerini ve veri işleme işlemlerini yönetir:

```python
class SpeakerManager:
    def add(self, name, source_presentation, source_transcript):
        # Create speaker profile with unique ID

    def process(self, speakers, llm_model, llm_api_key):
        # AI-powered section generation

    def resolve(self, speaker_pattern):
        # Flexible speaker lookup by name or ID
```

**Ana Sorumluluklar**:

- Konuşmacı profili yaşam döngüsü (CRUD işlemleri)
- Sunum ve transkript dosyalarının yönetimi
- İçerik üretimi için AI işleme koordinasyonu
- Veri doğrulama ve hata yönetimi

### 3. Ayarlar Düzenleyicisi

**Location**: `src/core/settings_editor.py`

Şablon tabanlı yaklaşım ile yapılandırma yönetimi:

```python
class SettingsEditor:
    def __init__(self):
        # Load template defaults
        self.template_data = yaml.load(self.template)

        # Merge with user settings
        self._data = {**self.template_data, **user_data}
```

**Ana Özellikler**:

- Varsayılanlarla şablon tabanlı yapılandırma
- İnsan tarafından okunabilir ayarlar için YAML formatı
- Şablon şemasına karşı doğrulama
- Varsayılanlara otomatik geri dönüş

## Veri Akışı

### 1. Kurulum Aşaması

```
Kullanıcı Girişi → Konuşmacı Yöneticisi → Dosya Sistemi → AI İşleme → Depolanmış Bölümler
     ↓              ↓              ↓              ↓              ↓
  CLI Komutu → PDF Çıkarma → LLM Analizi → Bölüm Verisi → JSON Depolama
```

### 2. Gerçek Zamanlı Navigasyon Aşaması

```
Ses Girişi → Konuşma Tanıma → Metin İşleme → Benzerlik Eşleştirme → Navigasyon
     ↓               ↓                    ↓               ↓               ↓
  Mikrofon → Transkribe Edilmiş Metin → Normalleştirilmiş Kelimeler → Parça Eşleştirme → Slayt Navigasyonu
```

### 3. Veri İşleme Akışı

```
Sunum PDF'i + Transkript PDF'i
            ↓
    Bölüm Üreticisi (AI)
            ↓
    Oluşturulan Bölümler
            ↓
    Parça Üreticisi
            ↓
    Gezilebilir Parçalar
            ↓
    Benzerlik Hesaplayıcı
            ↓
    Gerçek Zamanlı Navigasyon
```

## İşleme Boru Hattı

### 1. İçerik Hazırlama Boru Hattı

```python
# PDF Processing
presentation_data = _extract_pdf(presentation_path, "presentation")
transcript_data = _extract_pdf(transcript_path, "transcript")

# AI Section Generation
sections = _call_llm(presentation_data, transcript_data, llm_model, llm_api_key)

# Chunk Generation for Navigation
chunks = chunk_producer.generate_chunks(sections, window_size)
```

**Adımlar**:

1. **PDF Çıkarma**: Sunum ve transkript dosyalarından metin içeriği çıkarır
2. **AI Analizi**: LLM'yi kullanarak transkript içeriğini sunum slaytlarıyla hizalar
3. **Bölüm Oluşturma**: İçerik ve indekslerle yapılandırılmış bölümler oluşturur
4. **Parça Üretimi**: Gerçek zamanlı eşleştirme için kaydırmalı pencere parçaları oluşturur

### 2. Gerçek Zamanlı Navigasyon Boru Hattı

```python
# Audio Processing Thread
audio_data → STT Model → recognized_text → text_normalizer → normalized_words

# Navigation Thread
normalized_words → chunk_matching → similarity_scoring → navigation_decision → keyboard_control
```

**Adımlar**:

1. **Ses Yakalama**: Düşük gecikmeli sürekli mikrofon girişi
2. **Konuşma Tanıma**: Gerçek zamanlı STT için yerel ONNX modeli
3. **Metin Normalizasyonu**: Tanınan metni temizler ve standartlaştırır
4. **Benzerlik Eşleştirme**: Konuşmayı sunum parçalarıyla karşılaştırır
5. **Navigasyon Kararı**: En uygun slayt hareketini belirler
6. **Klavye Kontrolü**: Slayt navigasyonu için ok tuşu basışlarını simüle eder

## Gerçek Zamanlı İşlemler

### İş Parçacığı Modeli

moves, gerçek zamanlı performans için çok iş parçacıklı bir mimari kullanır:

```python
# Main Threads
audio_thread = threading.Thread(target=self.process_audio, daemon=True)
navigator_thread = threading.Thread(target=self.navigate_presentation, daemon=True)
keyboard_thread = Listener(on_press=self._on_key_press)

# Coordination
self.shutdown_flag = threading.Event()  # Global shutdown coordination
self.navigator_working = False          # Navigation state protection
```

**İş Parçacığı Sorumlulukları**:

1. **Audio Thread**:

   - Mikrofon'dan sürekli ses yakalama
   - ONNX modelleri ile konuşma tanıma
   - Kelime kuyruğu yönetimi

2. **Navigator Thread**:

   - Sunum içeriğine karşı benzerlik hesabı
   - Navigasyon kararları verme
   - Slayt kontrolü için klavye simülasyonu

3. **Keyboard Thread**:

   - Manuel geçersiz kılma kontrolleri (ok tuşları, duraklatma)
   - Otomatik navigasyonla entegrasyon

4. **Main Thread**:
   - Ses akışı yönetimi
   - İş parçacığı yaşam döngüsü koordinasyonu
   - Kullanıcı arayüzü ve geri bildirim

### Performans Optimizasyonları

#### 1. Ses İşleme

- **Düşük Gecikme**: Tepkili tanıma için 0.1s çerçeve süresi
- **Arabellek Yönetimi**: Sınırlı kuyruklar bellek birikmesini önler
- **Cihaz Optimizasyonu**: Otomatik mikrofon seçimi ve yapılandırması

#### 2. Konuşma Tanıma

- **Yerel İşleme**: ONNX modelleri ağ gecikmesini ortadan kaldırır
- **Optimizasyonlu Modeller**: Daha hızlı çıkarım için INT8 kantifikasyonu
- **İş Parçacığı Güvenliği**: Oturum başına izole tanıma akışları

#### 3. Benzerlik Hesaplaması

- **Önbellekleme**: Fonetik kod üretimi için LRU önbellek
- **Vektörleştirme**: Anlamsal benzerlik için NumPy işlemleri
- **Erken Çıkış**: Navigasyon devam ederken işlemi atla

## Makine Öğrenimi Entegrasyonu

### 1. Konuşmadan Metne (STT)

**Teknoloji**: Yerel modellerle Sherpa-ONNX  
**Location**: `src/core/components/ml_models/stt/`

```python
self.recognizer = OnlineRecognizer.from_transducer(
    tokens="stt/tokens.txt",
    encoder="stt/encoder.int8.onnx",
    decoder="stt/decoder.int8.onnx",
    joiner="stt/joiner.int8.onnx",
    num_threads=8,
    decoding_method="greedy_search"
)
```

**Avantajlar**:

- Sunumlar sırasında ağ bağımlılığı yok
- Tutarlı gecikme ve performans
- Gizlilik koruması (ses dışarı gönderilmez)
- Hız için optimize edilmiş INT8 modeller

### 2. Anlamsal Gömüler

**Teknoloji**: Sentence Transformers  
**Location**: `src/core/components/ml_models/embedding/`

```python
self.model = SentenceTransformer("src/core/components/ml_models/embedding")
embeddings = self.model.encode(texts, normalize_embeddings=True)
cosine_scores = np.dot(candidate_embeddings, input_embedding)
```

**Özellikler**:

- Gizlilik için yerel gömme modeli
- Tutarlı puanlama için normalleştirilmiş gömmeler
- Verimlilik için toplu işleme
- Anlamsal eşleştirme için kosinüs benzerliği

### 3. Büyük Dil Modeli (LLM)

**Teknoloji**: Çoklu sağlayıcı desteği ile LiteLLM  
**Amaç**: İçerik üretimi ve hizalama

```python
client = instructor.from_litellm(completion, mode=instructor.Mode.JSON)
response = client.chat.completions.create(
    model=llm_model,
    messages=[system_prompt, user_content],
    response_model=SectionsOutputModel
)
```

**Yetenekler**:

- Çoklu sağlayıcı desteği (Gemini, OpenAI, Anthropic)
- Pydantic modelleri ile yapılandırılmış çıktı
- Transkriptler ve slaytlar arasında akıllı içerik hizalaması
- Kullanıcı tercihine göre yapılandırılabilir model seçimi

## Veri Depolama

### Dizin Yapısı

```
~/.moves/                           # Kullanıcı veri dizini
├── settings.yaml                   # Kullanıcı yapılandırması
├── logs/                          # Uygulama logları
│   ├── speaker_manager.log
│   ├── presentation_controller.log
│   └── ...
└── speakers/                      # Konuşmacı verileri
    └── {speaker-id}/              # Tekil konuşmacı dizini
        ├── speaker.json           # Konuşmacı meta verisi
        ├── presentation.pdf       # Yerel sunum kopyası
        ├── transcript.pdf         # Yerel transkript kopyası
        └── sections.json          # Oluşturulan navigasyon bölümleri
```

### Veri Modelleri

**Location**: `src/data/models.py`

```python
@dataclass(frozen=True)
class Section:
    content: str           # Aligned speech content for slide
    section_index: int     # Zero-based slide index

@dataclass(frozen=True)
class Chunk:
    partial_content: str           # Sliding window text content
    source_sections: list[Section] # Contributing sections

@dataclass
class Speaker:
    name: str                    # Human-readable name
    speaker_id: SpeakerId       # Unique identifier
    source_presentation: Path   # Original presentation file
    source_transcript: Path     # Original transcript file
```

**Tasarım Özellikleri**:

- **Değiştirilemez Bölümler/Parçalar**: Navigasyon sırasında kazara değişikliği önler
- **Tip Güvenliği**: Özel tip takma adlarıyla güçlü tipleme
- **Serileştirme Desteği**: Veri kalıcılığı için JSON uyumlu

## Hata Yönetimi

### 1. Zarif Gerileme

```python
try:
    # Critical operation
    result = process_audio()
except Exception as e:
    logger.error(f"Audio processing failed: {e}")
    # Continue with degraded functionality
    self.shutdown_flag.set()
```

### 2. Kaynak Yönetimi

```python
try:
    with sd.InputStream(...) as stream:
        # Audio processing
        pass
finally:
    # Cleanup threads and resources
    self.shutdown_flag.set()
    audio_thread.join(timeout=1.0)
```

### 3. Kullanıcı Dostu Mesajlar

```python
# CLI error handling
except Exception as e:
    typer.echo(f"Could not add speaker '{name}'.", err=True)
    typer.echo(f"    {str(e)}", err=True)
    raise typer.Exit(1)
```

**Hata Yönetimi Prensipleri**:

- **Hızlı Başarısızlık**: İşleme boru hattında hataları erken tespit eder
- **Kaynak Temizliği**: İş parçacıklarının ve dosyaların doğru şekilde kapatılmasını sağlar
- **Kullanıcı İletişimi**: İşe yarar hata mesajları sağlar
- **Loglama**: Hata ayıklama ve izleme için kapsamlı loglama

## Performans Düşünceleri

### 1. Bellek Yönetimi

- **Sınırlı Kuyruklar**: Ses işleme sırasında sınırsız bellek artışını önler
- **LRU Önbellekleme**: Maliyetli hesaplamaları (fonetik kodlar, gömmeler) önbelleğe alır
- **Verimli Veri Yapıları**: Farklı kullanım durumları için uygun konteynerler kullanır

### 2. CPU Optimizasyonu

- **Çoklu İş Parçacığı**: Ses, navigasyon ve UI için paralel işleme
- **Model Optimizasyonu**: Daha hızlı çıkarım için INT8 kantifike modeller
- **Toplu İşleme**: Mümkün olduğunda işlemleri gruplar

### 3. G/Ç Optimizasyonu

- **Asenkron İşlemler**: Engellemesiz dosya ve ağ işlemleri
- **Yerel Modeller**: Sunumlar sırasında ağ bağımlılığını azaltır
- **Verimli Serileştirme**: İnsan tarafından okunabilir, verimli veri depolama için JSON

### 4. Gerçek Zamanlı Kısıtlamalar

- **Hedef Gecikme**: Konuşmadan navigasyona < 500ms
- **Çerçeve Hızı**: Tepkili tanıma için 100ms ses çerçeveleri
- **İş Parçacığı Öncelikleri**: Ses işleme en yüksek önceliği alır

Bu mimari, moves'un güvenilir, gerçek zamanlı sunum navigasyonu sağlamasını mümkün kılar ve gelecekteki geliştirmeler için modülerlik ve genişletilebilirliği korur.
