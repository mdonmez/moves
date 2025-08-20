# moves ile Başlarken

Bu rehber, moves adlı yapay zeka destekli sunum kontrol sistemini kurmanıza ve kullanmaya başlamanıza yardımcı olacaktır.

## İçindekiler

- [Önkoşullar](#prerequisites)
- [Kurulum](#installation)
- [İlk Yapılandırma](#initial-configuration)
- [İlk Konuşmacı Profilinizi Oluşturma](#creating-your-first-speaker-profile)
- [Sunum Verilerinin İşlenmesi](#processing-presentation-data)
- [Ses Kontrolüyle Navigasyonu Başlatma](#starting-voice-controlled-navigation)
- [Temel Kullanım İş Akışı](#basic-usage-workflow)
- [Sık Karşılaşılan Sorunlar](#common-issues)

## Önkoşullar

moves'u kurmadan önce şunların mevcut olduğundan emin olun:

### Sistem Gereksinimleri

- **Python 3.13+**: Tüm işlevsellik için gereklidir
- **İşletim Sistemi**: Windows, macOS veya Linux
- **Bellek**: Minimum 4 GB RAM (8 GB+ tavsiye edilir)
- **Depolama**: Modeller ve veriler için en az 2 GB boş alan
- **Ağ**: Yapay zeka işleme için internet bağlantısı

### Donanım Gereksinimleri

- **Mikrofon**: Konuşma tanıma için herhangi bir USB veya dahili mikrofon
- **Ses Sürücüleri**: Doğru yapılandırılmış ses giriş cihazı
- **Sunum Kurulumu**: Slayt gösterimi için ekran/projektör

### Yazılım Bağımlılıkları

- **uv**: Python paket yöneticisi (bağımlılıkları otomatik olarak yönetir)
- **PDF Okuyucu**: Sunum ve transkript dosyalarını hazırlamak için

## Kurulum

moves, bağımlılık yönetimi için `uv` kullanır; bu, kurulum sürecini basitleştirir.

### Adım 1: Kopyalama veya İndirme

```bash
# Git kullanıyorsanız
git clone <repository-url> moves
cd moves

# Veya proje dosyalarını indirip çıkartın
```

### Adım 2: Bağımlılıkları Yükleme

```bash
# Gerekli tüm paketleri yükleyin ve sanal ortamı oluşturun
uv sync
```

Bu komut:

- Sanal ortam oluşturur
- `pyproject.toml` dosyasından tüm bağımlılıkları yükler
- Gerekli ML modellerini indirir ve ayarlar

### Adım 3: Kurulumu Doğrulama

```bash
# CLI arayüzünü test edin
uv run python app.py --help
```

Ana yardım menüsü ve kullanılabilir komutları görmelisiniz.

## İlk Yapılandırma

### Adım 1: LLM Ayarlarını Yapılandırma

moves, sunumları işlemek için bir LLM (Büyük Dil Modeli) API'si gerektirir:

```bash
# Tercih ettiğiniz LLM modelini ayarlayın
uv run python app.py settings set model "gemini/gemini-2.0-flash"

# API anahtarınızı ayarlayın
uv run python app.py settings set key "your-api-key-here"
```

**Desteklenen Modeller:**

- Gemini: `gemini/gemini-2.0-flash`, `gemini/gemini-pro`
- OpenAI: `gpt-4`, `gpt-3.5-turbo`
- Anthropic: `claude-3-opus`, `claude-3-sonnet`
- Tam liste için [LiteLLM belgelerine](https://models.litellm.ai/) bakın

### Adım 2: Yapılandırmayı Doğrulama

```bash
# Mevcut ayarları kontrol edin
uv run python app.py settings list
```

Çıktı şöyle olmalıdır:

```
Application Settings.
    model (LLM Model) -> gemini/gemini-2.0-flash
    key (API Key) -> your-api-key-here
```

## İlk Konuşmacı Profilinizi Oluşturma

Bir konuşmacı profili, moves'un akıllı navigasyon için kullandığı sunum ve transkripti içerir.

### Adım 1: Dosyalarınızı Hazırlayın

İki PDF dosyasına ihtiyacınız var:

1. **Sunum PDF'i**: PDF olarak dışa aktarılmış slayt dosyanız
2. **Transkript PDF'i**: Konuşmanızın metni, her slayt için bir bölüm

**Transkript Formatı Örneği:**

```
Sayfa 1: AI teknolojisi üzerine sunumumuza hoş geldiniz.

Sayfa 2: Bugün üç ana konuyu ele alacağız: makine öğrenmesi, doğal dil işleme ve bilgisayarlı görü.

Sayfa 3: Makine öğrenmesi temelleriyle başlayalım.
```

### Adım 2: Konuşmacı Profilini Ekleyin

```bash
# Yeni bir konuşmacıyı dosyalarıyla ekleyin
uv run python app.py speaker add "John Doe" ./presentation.pdf ./transcript.pdf
```

**Başarı Çıktısı:**

```
Speaker 'John Doe' (john-doe-Ax9K2) added.
    ID -> john-doe-Ax9K2
    Presentation -> /path/to/presentation.pdf
    Transcript -> /path/to/transcript.pdf
```

### Adım 3: Konuşmacıları Listeleyin

```bash
# Kayıtlı tüm konuşmacıları görüntüleyin
uv run python app.py speaker list
```

**Çıktı:**

```
Registered Speakers (1)

ID              NAME    STATUS
─────────────── ──────  ──────────
john-doe-Ax9K2  John    Not Ready
```

**Durum Anlamları:**

- **Not Ready**: Konuşmacı eklendi fakat AI navigasyonu için işlenmedi
- **Ready**: Konuşmacı işlendi ve ses kontrollü sunumlar için hazır

## Sunum Verilerinin İşlenmesi

Sesli navigasyon kullanmadan önce moves, sunumunuzu AI ile işleyerek akıllı içerik eşlemeleri oluşturmalıdır.

### Adım 1: Konuşmacı Verisini İşleyin

```bash
# Belirli bir konuşmacıyı işleyin
uv run python app.py speaker process "John Doe"

# Veya tüm konuşmacıları işleyin
uv run python app.py speaker process --all
```

**İşleme Adımları:**

1. **PDF Çıkarımı**: Sunum ve transkriptten metin çıkarır
2. **AI Analizi**: LLM kullanarak transkript içeriğini slaytlarla hizalar
3. **Bölüm Oluşturma**: Ses kontrolü için gezilebilir bölümler üretir
4. **Veri Depolama**: Gerçek zamanlı navigasyon için işlenmiş veriyi kaydeder

**Başarı Çıktısı:**

```
Processing speaker 'John Doe' (john-doe-Ax9K2)...
Speaker 'John Doe' (john-doe-Ax9K2) processed.
    25 sections created.
```

### Adım 2: İşlemeyi Doğrulama

```bash
# Konuşmacı durumunu kontrol edin
uv run python app.py speaker show "John Doe"
```

**Çıktı:**

```
Showing details for speaker 'John Doe' (john-doe-Ax9K2)
    ID -> john-doe-Ax9K2
    Name -> John Doe
    Status -> Ready
    Presentation -> /path/to/presentation.pdf
    Transcript -> /path/to/transcript.pdf
```

## Ses Kontrolüyle Navigasyonu Başlatma

Konuşmacınız işlendiğinde, canlı ses kontrollü sunum navigasyonunu başlatabilirsiniz.

### Adım 1: Ortamınızı Hazırlayın

1. **Sunumu Açın**: Slayt dosyanızı sunum modunda başlatın
2. **Mikrofonu Konumlandırın**: Net bir ses girişi sağlayın
3. **Sesi Test Edin**: Mikrofon algılanıyor mu kontrol etmek için normal konuşun

### Adım 2: Ses Kontrolünü Başlatın

```bash
# Ses kontrollü navigasyonu başlatın
uv run python app.py presentation control "John Doe"
```

**Başlangıç Çıktısı:**

```
Starting presentation control for 'John Doe' (john-doe-Ax9K2).
    25 sections loaded
    READY & LISTENING

    Press Ctrl+C to exit.

Keyboard controls:
  → (Right Arrow): Next section
  ← (Left Arrow): Previous section
  Ins (Insert): Pause/Resume automatic navigation

Waiting for 12 words to first trigger, keep speaking...
```

### Adım 3: Sunuma Başlayın

1. **Konuşmaya Başlayın**: Sunumunuzu normal şekilde yürütün
2. **Otomatik Navigasyon**: moves, konuşmanıza göre slaytları geçirir
3. **Manuel Geçiş**: Gerekirse klavye kontrollerini kullanın
4. **Duraklat/Devam**: Otomatik navigasyonu Insert tuşuyla duraklatın veya devam ettirin

**Navigasyon Çıktısı:**

```
[3/25]
Speech  -> learning fundamentals of machine learning algorithms
Match   -> machine learning fundamentals and basic concepts overview
```

## Temel Kullanım İş Akışı

moves kullanırken tipik iş akışı aşağıdaki gibidir:

### 1. Hazırlık Aşaması

```bash
# Sistemi yapılandır
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-api-key"

# Konuşmacıyı ekle
uv run python app.py speaker add "Speaker Name" presentation.pdf transcript.pdf

# AI navigasyonu için işle
uv run python app.py speaker process "Speaker Name"
```

### 2. Sunum Aşaması

```bash
# Ses kontrolünü başlat
uv run python app.py presentation control "Speaker Name"

# Normal şekilde sunum yap - sistem otomatik olarak navigasyonu yönetir
# Gerekirse manuel geçiş için klavye kontrollerini kullan
```

### 3. Yönetim Aşaması

```bash
# Konuşmacı dosyalarını güncelle
uv run python app.py speaker edit "Speaker Name" --presentation new-presentation.pdf

# Değişikliklerden sonra yeniden işle
uv run python app.py speaker process "Speaker Name"

# İş bittiğinde temizle
uv run python app.py speaker delete "Speaker Name"
```

## Sık Karşılaşılan Sorunlar

### Ses Sorunları

**Problem**: Mikrofon algılanmıyor  
**Çözüm**:

- Sistem ses ayarlarını kontrol edin
- Mikrofon izinlerinin verildiğinden emin olun
- Önce başka bir ses uygulamasında deneyin

**Problem**: Konuşma tanıma düşük kalitede  
**Çözüm**:

- Net ve normal sesle konuşun
- Arka plan gürültüsünü azaltın
- Mikrofonu ağzınızdan 15‑30 cm uzaklıkta tutun

### İşleme Sorunları

**Problem**: LLM işleme başarısız oluyor  
**Çözüm**:

- API anahtarının doğru ve yeterli krediye sahip olduğunu kontrol edin
- Ağ bağlantısını gözden geçirin
- Mevcut model kullanılamıyorsa farklı bir model deneyin

**Problem**: PDF çıkarımı hataları  
**Çözüm**:

- PDF'lerin metin tabanlı (tarama değil) olduğundan emin olun
- PDF'leri orijinal kaynaktan yeniden dışa aktarın
- Dosya izinlerini ve yollarını kontrol edin

### Navigasyon Sorunları

**Problem**: Slaytlar yanlış geçiyor  
**Çözüm**:

- Transkriptin gerçek konuşmanızla yakından eşleştiğini doğrulayın
- Transkript iyileştirmelerinden sonra konuşmacıyı yeniden işleyin
- Gerekirse manuel klavye kontrollerini yedek olarak kullanın

**Problem**: Navigasyon çok hassas/ yavaş  
**Çözüm**:

- Konuşma hızınızı ve netliğinizi ayarlayın
- Daha iyi eşleşme için transkripti düzenleyin
- Geçişlerde duraklatma özelliğini kullanın

## Sonraki Adımlar

- **Daha Fazla Öğren**: moves'un nasıl çalıştığını anlamak için [Mimari Genel Bakış](./architecture.md) belgesini okuyun
- **Özelleştir**: Gelişmiş ayarlar için [Yapılandırma](./configuration.md) sayfasına bakın
- **Sorun Gider**: Ayrıntılı çözümler için [Sorun Giderme Kılavuzu](./troubleshooting.md)'na göz atın
- **Katkı Sağla**: moves işlevselliğini genişletmek için [Geliştirme Rehberi](./development.md)'ni inceleyin

## Yardım Alma

Bu rehberde yer almayan sorunlarla karşılaşırsanız:

1. [Sorun Giderme Kılavuzu](./troubleshooting.md) sayfasını kontrol edin
2. `~/.moves/logs/` içindeki günlük dosyalarına bakarak hata detaylarını inceleyin
3. Tüm önkoşul ve bağımlılıkların doğru kurulduğunu doğrulayın
4. Karmaşık sunumlar öncesinde basit bir sunumla test edin
