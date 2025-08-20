# Sunum Kontrolcüsü

The `PresentationController` is the core component responsible for real-time voice-controlled presentation navigation. It integrates speech recognition, similarity matching, and slide navigation into a cohesive system that responds to speaker's voice in real-time.

## Table of Contents

- [Genel Bakış](#overview)
- [Mimari](#architecture)
- [Temel Özellikler](#key-features)
- [İş Parçacığı Modeli](#threading-model)
- [Ses İşleme](#audio-processing)
- [Gezinme Mantığı](#navigation-logic)
- [Manuel Kontroller](#manual-controls)
- [Konfigürasyon](#configuration)
- [Performans Optimizasyonu](#performance-optimization)
- [Hata Yönetimi](#error-handling)
- [Kullanım Örnekleri](#usage-examples)

## Genel Bakış

**Konum**: `src/core/presentation_controller.py`

PresentationController, ses girişinden slayt gezinmesine kadar tüm gerçek zamanlı sunum kontrol oturumunu yönetir. Sürekli çalışan çok iş parçacıklı bir sistem olarak çalışır:

1. **Ses Yakalar**: Düşük gecikmeli mikrofon girişini kaydeder
2. **Konuşmayı Tanır**: Yerel ONNX modelleri kullanarak sesi metne dönüştürür
3. **İçeriği Eşleştirir**: Konuşmayı sunum bölümleriyle karşılaştırır
4. **Slaytları Gezer**: Otomatik olarak uygun slaytlara geçer
5. **Geri Bildirim Sağlar**: Gerçek zamanlı eşleştirme bilgilerini gösterir

## Mimari

```python
class PresentationController:
    def __init__(self, sections, start_section, window_size=12):
        # Core components
        self.similarity_calculator = SimilarityCalculator()
        self.recognizer = OnlineRecognizer.from_transducer(...)

        # Navigation state
        self.sections = sections
        self.current_section = start_section
        self.chunks = chunk_producer.generate_chunks(sections, window_size)

        # Real-time processing
        self.recent_words = deque(maxlen=window_size)
        self.audio_queue = deque(maxlen=5)

        # Thread coordination
        self.shutdown_flag = threading.Event()
        self.navigator_working = False
        self.paused = False
```

### Temel Bileşenler

#### 1. Konuşma Tanıma Motoru

- **Teknoloji**: Yerel transdüser modelleriyle Sherpa-ONNX
- **Modeller**: Optimal performans için INT8 kuantize edilmiş
- **İşleme**: Gerçek zamanlı akış tanıma

#### 2. Benzerlik Hesaplayıcı

- **Hibrit Yaklaşım**: Anlamsal ve fonetik eşleşmeyi birleştirir
- **Ağırlıklar**: Benzerlik türleri arasında yapılandırılabilir denge
- **Performans**: Gerçek zamanlı çalışma için optimize edilmiştir

#### 3. Gezinme Motoru

- **Durum Yönetimi**: Mevcut konumu ve hedef slaytları izler
- **Klavye Simülasyonu**: Programatik slayt gezinmesi
- **Manuel Geçersiz Kılma**: Kesintisiz klavye kontrol entegrasyonu

## Temel Özellikler

### 1. Gerçek Zamanlı Konuşma İşleme

```python
def process_audio(self):
    while not self.shutdown_flag.is_set():
        if self.audio_queue:
            chunk = self.audio_queue.popleft()
            self.stream.accept_waveform(self.sample_rate, chunk)

            if text := self.recognizer.get_result(self.stream):
                normalized_text = text_normalizer.normalize_text(text)
                words = normalized_text.strip().split()[-self.window_size:]
                self.recent_words.extend(words)
```

**Özellikler**:

- **Sürekli İşleme**: Engellemesiz ses akışı işleme
- **Kelime Penceresi**: Son konuşmanın kayan penceresini tutar
- **Metin Normalizasyonu**: Tutarlı eşleşme için metni standartlaştırır

### 2. Akıllı Gezinme

```python
def navigate_presentation(self):
    while not self.shutdown_flag.is_set():
        current_words = list(self.recent_words)

        if len(current_words) >= self.window_size and not self.paused:
            # Get candidate chunks near current position
            candidate_chunks = chunk_producer.get_candidate_chunks(
                self.current_section, self.chunks
            )

            # Calculate similarity scores
            input_text = " ".join(current_words)
            similarity_results = self.similarity_calculator.compare(
                input_text, candidate_chunks
            )

            # Navigate to best match
            best_chunk = similarity_results[0].chunk
            target_section = best_chunk.source_sections[-1]
            self._navigate_to_section(target_section)
```

**Gezinme Mantığı**:

- **Bağlamsal Eşleşme**: Yalnızca mevcut konuma yakın slaytları dikkate alır
- **En İyi Eşleşme Seçimi**: En yüksek benzerlik puanını seçer
- **Yumuşak Geçişler**: Çoklu slayt atlamalarını sorunsuz yönetir

### 3. Çok Modlu Kontrol

The controller supports both automatic and manual navigation:

**Otomatik Gezinme**:

- Konuşma tabanlı slayt geçişleri
- Gerçek zamanlı benzerlik eşleşmesi
- Bağlamsal konumlandırma

**Manuel Geçersiz Kılma**:

- **Sağ Ok**: Sonraki slayt
- **Sol Ok**: Önceki slayt
- **Insert Tuşu**: Otomatik gezinmeyi duraklat/ devam ettir

## İş Parçacığı Modeli

The PresentationController uses a sophisticated multi-threaded architecture:

```python
# Thread Structure
├── Main Thread (Audio Stream Management)
├── Audio Processing Thread (Speech Recognition)
├── Navigation Thread (Similarity & Navigation)
└── Keyboard Listener Thread (Manual Controls)
```

### İş Parçacığı Koordinasyonu

```python
# Global coordination
self.shutdown_flag = threading.Event()  # Shutdown signal
self.navigator_working = False          # Navigation lock
self.paused = False                     # User pause state

# Thread startup
audio_thread = threading.Thread(target=self.process_audio, daemon=True)
self.navigator = threading.Thread(target=self.navigate_presentation, daemon=True)
self.keyboard_listener = Listener(on_press=self._on_key_press)

# Synchronized shutdown
self.shutdown_flag.set()
audio_thread.join(timeout=1.0)
self.navigator.join(timeout=1.0)
self.keyboard_listener.stop()
```

**Faydalar**:

- **Duyarlılık**: Ses ve gezinme işleme bağımsız çalışır
- **İş Parçacığı Güvenliği**: Doğru senkronizasyon yarış durumlarını önler
- **Temiz Kapatma**: Tüm iş parçacıklarının sorunsuz sonlandırılması

## Ses İşleme

### Ses Yapılandırması

```python
# Audio parameters optimized for speech recognition
self.frame_duration = 0.1      # 100ms frames for low latency
self.sample_rate = 16000       # Standard speech recognition rate
self.selected_mic = sd.default.device[0]  # Auto-detect microphone
```

### İşleme Boru Hattı

```python
# Audio capture → Queue → Recognition → Normalization → Word extraction
with sd.InputStream(
    samplerate=self.sample_rate,
    blocksize=int(self.sample_rate * self.frame_duration),
    callback=lambda indata, *_: self.audio_queue.append(indata[:, 0].copy())
):
    # Continuous audio stream processing
```

**Optimizasyon Özellikleri**:

- **Düşük Gecikme**: Tepkili tanıma için 100ms çerçeve işleme
- **Arabellek Yönetimi**: Sınırlı kuyruklar bellek birikimini önler
- **Cihaz Esnekliği**: Otomatik mikrofon algılama ve yapılandırma

## Gezinme Mantığı

### Bağlamsal Eşleşme

The controller doesn't match against all slides, but uses contextual windows:

```python
def get_candidate_chunks(current_section, all_chunks):
    idx = int(current_section.section_index)
    start, end = idx - 2, idx + 3  # ±2-3 slide window

    return [chunk for chunk in all_chunks
            if all(start <= s.section_index <= end for s in chunk.source_sections)]
```

**Faydalar**:

- **Performans**: Arama alanını sınırlayarak işlemi azaltır
- **Doğruluk**: Alakasız uzak slaytlara atlamayı önler
- **Bağlam Koruma**: Mantıksal sunum akışını sürdürür

### Gezinme Yürütme

```python
def _navigate_to_section(self, target_section):
    current_idx = self.current_section.section_index
    target_idx = target_section.section_index
    navigation_distance = target_idx - current_idx

    if navigation_distance != 0:
        key = Key.right if navigation_distance > 0 else Key.left

        # Execute multiple key presses for large jumps
        for _ in range(abs(navigation_distance)):
            self.keyboard_controller.press(key)
            self.keyboard_controller.release(key)
            if abs(navigation_distance) > 1:
                time.sleep(0.01)  # Brief delay between presses

    self.current_section = target_section
```

## Manuel Kontroller

### Klavye Entegrasyonu

The controller seamlessly integrates manual keyboard controls:

```python
def _on_key_press(self, key):
    if key == Key.right:
        self._next_section()
    elif key == Key.left:
        self._prev_section()
    elif key == Key.insert:
        self._toggle_pause()

def _toggle_pause(self):
    self.paused = not self.paused
    print("\n[Paused]" if self.paused else "\n[Resumed]")
```

**Manuel Kontroller**:

- **Ok Tuşları**: Otomatik gezinmeyi geçersiz kılar
- **Insert Tuşu**: Otomatik gezinmeyi açıp kapatır
- **Sorunsuz Entegrasyon**: Manuel kontroller iç durumu günceller

### Durum Yönetimi

```python
def _next_section(self):
    current_idx = self.current_section.section_index
    if current_idx < len(self.sections) - 1:
        self.current_section = self.sections[current_idx + 1]
        print(f"\n[Manual Next] {current_idx + 1} → {current_idx + 2}")
```

## Konfigürasyon

### Başlatma Parametreleri

```python
def __init__(
    self,
    sections: list[Section],        # Processed presentation sections
    start_section: Section,         # Initial slide position
    window_size: int = 12,          # Speech window size (words)
):
```

### Çalışma Zamanı Konfigürasyonu

```python
# Audio settings
self.frame_duration = 0.1       # Audio frame duration (seconds)
self.sample_rate = 16000        # Audio sampling rate (Hz)

# Recognition settings
num_threads=8,                  # ONNX model threads
decoding_method="greedy_search" # Recognition strategy

# Navigation settings
maxlen=window_size             # Word window size
maxlen=5                       # Audio queue size
```

**Ayarlanabilir Parametreler**:

- **Pencere Boyutu**: Bağlam ve duyarlılık arasında denge
- **Çerçeve Süresi**: Gecikme ve tanıma doğruluğu arasında taviz
- **Kuyruk Boyutları**: Bellek ve işleme arabellek yönetimi

## Performans Optimizasyonu

### 1. Ses İşleme Optimizasyonu

```python
# Efficient audio handling
self.audio_queue = deque(maxlen=5)        # Bounded queue
blocksize = int(self.sample_rate * self.frame_duration)  # Optimal block size
dtype="float32"                           # Efficient audio format
```

### 2. Tanıma Optimizasyonu

```python
# Local ONNX models for zero network latency
self.recognizer = OnlineRecognizer.from_transducer(
    encoder="encoder.int8.onnx",    # Quantized for speed
    decoder="decoder.int8.onnx",
    joiner="joiner.int8.onnx",
    num_threads=8                   # Multi-threaded inference
)
```

### 3. Gezinme Optimizasyonu

```python
# Prevent navigation conflicts
if not self.navigator_working:
    self.navigator_working = True
    try:
        # Navigation logic
        pass
    finally:
        self.navigator_working = False
```

**Performans Özellikleri**:

- **İş Parçacığı İzolasyonu**: Ses ve gezinme arasında engelleme önler
- **Verimli Veri Yapıları**: Bellek yönetimi için sınırlı koleksiyonlar
- **Yerel İşleme**: Sunum sırasında ağ bağımlılığı yok

## Hata Yönetimi

### Graceful Degradation

```python
def process_audio(self):
    while not self.shutdown_flag.is_set():
        try:
            # Audio processing
            pass
        except Exception as e:
            raise RuntimeError(f"Audio processing error: {e}") from e
```

### Resource Management

```python
def control(self):
    try:
        with sd.InputStream(...):
            # Presentation control loop
            pass
    except KeyboardInterrupt:
        pass  # Graceful exit on Ctrl+C
    finally:
        self.shutdown_flag.set()
        # Cleanup all threads
        if audio_thread.is_alive():
            audio_thread.join(timeout=1.0)
```

**Hata Yönetim Stratejisi**:

- **Hızlı Başarısızlık**: Hataları erken algılar ve net mesajlar verir
- **Kaynak Temizliği**: İş parçacığı ve kaynakların doğru temizlenmesini sağlar
- **Kullanıcı Deneyimi**: Kesintileri sorunsuz yönetir

## Kullanım Örnekleri

### Temel Kullanım

```python
# Initialize with processed sections
controller = PresentationController(
    sections=processed_sections,
    start_section=processed_sections[0],
    window_size=12
)

# Start voice control session
controller.control()  # Blocks until Ctrl+C or error
```

### Özel Konfigürasyon

```python
# Custom window size for different speech patterns
controller = PresentationController(
    sections=sections,
    start_section=start_section,
    window_size=8  # Smaller window for faster speakers
)

# Access internal state
current_slide = controller.current_section.section_index
print(f"Currently on slide {current_slide + 1}")
```

### Entegrasyon Örneği

```python
# CLI integration
def presentation_control(speaker: str):
    try:
        # Load processed speaker data
        sections = load_speaker_sections(speaker)

        # Create and configure controller
        controller = PresentationController(
            sections=sections,
            start_section=sections[0]
        )

        # Provide user feedback
        print(f"Starting presentation control for '{speaker}'")
        print(f"    {len(sections)} sections loaded")
        print("    READY & LISTENING")

        # Start control session
        controller.control()

    except Exception as e:
        print(f"Control error: {e}")
        raise typer.Exit(1)
```

## Gerçek Zamanlı Geri Bildirim

The controller provides continuous feedback during operation:

```python
# Navigation feedback
print(f"\n[{target_section.section_index + 1}/{len(self.sections)}]")
print(f"Speech  -> {recent_speech}")
print(f"Match   -> {recent_match}")

# Manual control feedback
print(f"\n[Manual Next] {prev_idx + 1} → {current_idx + 1}")
print(f"\n[Paused]" if paused else "\n[Resumed]")
```

Bu kapsamlı geri bildirim, kullanıcıların sistem davranışını anlamalarına ve gerçek zamanlı olarak gezinme sorunlarını çözmelerine yardımcı olur.

PresentationController, konuşmacının sesine doğal bir şekilde yanıt verirken gerektiğinde tam manuel kontrolü sağlayan sorunsuz ve akıllı sunum gezinmesini sunmak için birlikte çalışan tüm sistem bileşenlerinin bir araya gelmesidir.