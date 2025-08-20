# Komut Satırı Arayüzü (CLI)

moves, Typer ile inşa edilmiş kapsamlı bir komut satırı arayüzü sağlayarak konuşmacı yönetimi, sunum kontrolü ve sistem yapılandırması için sezgisel komutlar sunar. CLI, tutarlı desenler ve yardımcı geri bildirimlerle mantıksal alt komutlara organize edilmiştir.

## İçindekiler

- [Genel Bakış](#overview)
- [CLI Yapısı](#cli-structure)
- [Konuşmacı Yönetimi Komutları](#speaker-management-commands)
- [Sunum Kontrol Komutları](#presentation-control-commands)
- [Ayar Yönetimi Komutları](#settings-management-commands)
- [Komut Desenleri](#command-patterns)
- [Hata İşleme](#error-handling)
- [Kullanım Örnekleri](#usage-examples)

## Genel Bakış

**Konum**: `app.py`

CLI, Typer kullanılarak oluşturulmuş olup otomatik yardım üretimi, tip doğrulama ve zengin biçimlendirme sağlayan modern, kullanıcı dostu bir komut satırı deneyimi sunar. Tüm komutlar, argümanlar, seçenekler ve çıktı biçimlendirmesi için tutarlı desenleri izler.

```python
# Main CLI application
app = typer.Typer(
    help="moves CLI - AI-powered presentation control system for seamless slide navigation.",
    add_completion=False,
)

# Subcommand applications
speaker_app = typer.Typer(help="Manage speaker profiles, files, and processing")
presentation_app = typer.Typer(help="Live presentation control with voice navigation")
settings_app = typer.Typer(help="Configure system settings (model, API key)")
```

## CLI Yapısı

### Ana Komut Grupları

```
uv run python app.py
├── speaker          # Konuşmacı profili yönetimi
│   ├── add          # Yeni konuşmacı profili oluştur
│   ├── edit         # Konuşmacı dosyalarını güncelle
│   ├── list         # Tüm konuşmacıları göster
│   ├── show         # Konuşmacı detaylarını görüntüle
│   ├── process      # AI bölümleri oluştur
│   └── delete       # Konuşmacıyı kaldır
├── presentation     # Canlı sunum kontrolü
│   └── control      # Sesli gezinmeyi başlat
└── settings         # Sistem yapılandırması
    ├── list         # Mevcut ayarları göster
    ├── set          # Ayar değerini güncelle
    └── unset        # Varsayılana sıfırla
```

### Yardım Sistemi

```bash
# Ana yardım
uv run python app.py --help

# Alt komut yardımı
uv run python app.py speaker --help
uv run python app.py speaker add --help

# Komut‑spesifik yardım
uv run python app.py settings set --help
```

## Konuşmacı Yönetimi Komutları

### `speaker add` - Konuşmacı Profili Oluştur

```bash
uv run python app.py speaker add <NAME> <PRESENTATION_FILE> <TRANSCRIPT_FILE>
```

**Amaç**: Sunum ve transkript dosyalarıyla yeni bir konuşmacı profili oluşturur.

**Argümanlar**:

- `NAME`: Konuşmacının adı (kimlik ve ID üretimi için kullanılır)
- `PRESENTATION_FILE`: Sunum PDF dosyasının yolu
- `TRANSCRIPT_FILE`: Transkript PDF dosyasının yolu

**Örnekler**:

```bash
# Temel kullanım
uv run python app.py speaker add "Dr. Sarah Johnson" ./presentation.pdf ./transcript.pdf

# Dosya adlarında boşluklar
uv run python app.py speaker add "John Doe" "./My Presentation.pdf" "./My Transcript.pdf"

# Mutlak yollar kullanma
uv run python app.py speaker add "Prof. Smith" /Users/smith/slides.pdf /Users/smith/notes.pdf
```

**Çıktı**:

```
Speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) added.
    ID -> dr-sarah-johnson-Ax9K2
    Presentation -> /path/to/presentation.pdf
    Transcript -> /path/to/transcript.pdf
```

**Hata İşleme**:

```bash
# Eksik dosyalar
uv run python app.py speaker add "Test Speaker" missing.pdf transcript.pdf
# Output: Could not add speaker 'Test Speaker'.
#             Presentation file not found: missing.pdf

# İsim çakışmaları
uv run python app.py speaker add "dr-sarah-johnson-Ax9K2" presentation.pdf transcript.pdf
# Output: Could not add speaker 'dr-sarah-johnson-Ax9K2'.
#             Given name conflicts with existing speaker ID.
```

### `speaker edit` - Konuşmacı Dosyalarını Güncelle

```bash
uv run python app.py speaker edit <SPEAKER> [OPTIONS]
```

**Amaç**: Mevcut konuşmacının sunum veya transkript dosyalarını günceller.

**Argümanlar**:

- `SPEAKER`: Güncellenecek konuşmacı adı ya da ID

**Seçenekler**:

- `--presentation, -p`: Yeni sunum dosyası yolu
- `--transcript, -t`: Yeni transkript dosyası yolu

**Örnekler**:

```bash
# Yalnızca sunumu güncelle
uv run python app.py speaker edit "Dr. Sarah Johnson" --presentation ./new-presentation.pdf

# Yalnızca transkripti güncelle
uv run python app.py speaker edit "dr-sarah-johnson-Ax9K2" -t ./updated-transcript.pdf

# Her iki dosyayı da güncelle
uv run python app.py speaker edit "Dr. Sarah Johnson" -p ./new-slides.pdf -t ./new-notes.pdf
```

**Çıktı**:

```
Speaker 'Dr. Sarah Johnson' updated.
    Presentation -> /path/to/new-presentation.pdf
    Transcript -> /path/to/updated-transcript.pdf
```

### `speaker list` - Tüm Konuşmacıları Göster

```bash
uv run python app.py speaker list
```

**Amaç**: Kayıtlı tüm konuşmacıları ve durumlarını görüntüler.

**Çıktı**:

```
Registered Speakers (2)

ID              NAME         STATUS
─────────────── ──────────── ──────────
dr-sarah-johnson Sarah       Ready
john-doe-Xy5Z8  John         Not Ready
```

**Durum Anlamları**:

- **Ready**: Konuşmacı işlenmiş ve ses kontrolüne hazır
- **Not Ready**: Konuşmacı eklenmiş ancak AI gezinme için henüz işlenmemiş

### `speaker show` - Konuşmacı Detaylarını Görüntüle

```bash
uv run python app.py speaker show <SPEAKER>
```

**Amaç**: Belirli bir konuşmacı hakkında ayrıntılı bilgi gösterir.

**Argümanlar**:

- `SPEAKER`: Görüntülenecek konuşmacı adı ya da ID

**Örnekler**:

```bash
uv run python app.py speaker show "Dr. Sarah Johnson"
uv run python app.py speaker show "dr-sarah-johnson-Ax9K2"
```

**Çıktı**:

```
Showing details for speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2)
    ID -> dr-sarah-johnson-Ax9K2
    Name -> Dr. Sarah Johnson
    Status -> Ready
    Presentation -> /Users/sarah/presentation.pdf
    Transcript -> /Users/sarah/transcript.pdf
```

### `speaker process` - AI Bölümleri Oluştur

```bash
uv run python app.py speaker process [SPEAKERS...] [OPTIONS]
```

**Amaç**: Sunum ve transkriptten gezinilebilir bölümler üretmek için AI kullanır.

**Argümanlar**:

- `SPEAKERS`: İşlenecek isteğe bağlı konuşmacı adı/ID listesi

**Seçenekler**:

- `--all, -a`: Tüm kayıtlı konuşmacıları işle

**Örnekler**:

```bash
# Belirli konuşmacıyı işle
uv run python app.py speaker process "Dr. Sarah Johnson"

# Birden fazla konuşmacıyı işle
uv run python app.py speaker process "Sarah" "John Doe" "Prof. Smith"

# Tüm konuşmacıları işle
uv run python app.py speaker process --all
```

**Çıktı**:

```
Processing speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2)...
Speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) processed.
    25 sections created.
```

**Toplu İşleme Çıktısı**:

```
Processing 3 speakers...
3 speakers processed.
    'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) -> 25 sections created.
    'John Doe' (john-doe-Xy5Z8) -> 18 sections created.
    'Prof. Smith' (prof-smith-Ab3C4) -> 32 sections created.
```

### `speaker delete` - Konuşmacıyı Kaldır

```bash
uv run python app.py speaker delete <SPEAKER>
```

**Amaç**: Konuşmacı profilini ve ilişkili tüm verileri siler.

**Argümanlar**:

- `SPEAKER`: Silinecek konuşmacı adı ya da ID

**Örnekler**:

```bash
uv run python app.py speaker delete "Dr. Sarah Johnson"
uv run python app.py speaker delete "dr-sarah-johnson-Ax9K2"
```

**Çıktı**:

```
Speaker 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2) deleted.
```

## Sunum Kontrol Komutları

### `presentation control` - Sesli Gezintiyi Başlat

```bash
uv run python app.py presentation control <SPEAKER>
```

**Amaç**: Canlı ses kontrollü sunum gezinmesini başlatır.

**Argümanlar**:

- `SPEAKER`: İşlenmiş konuşmacı adı ya da ID

**Örnekler**:

```bash
uv run python app.py presentation control "Dr. Sarah Johnson"
uv run python app.py presentation control "dr-sarah-johnson-Ax9K2"
```

**Çıktı**:

```
Starting presentation control for 'Dr. Sarah Johnson' (dr-sarah-johnson-Ax9K2).
    25 sections loaded
    READY & LISTENING

    Press Ctrl+C to exit.

Keyboard controls:
  → (Right Arrow): Next section
  ← (Left Arrow): Previous section
  Ins (Insert): Pause/Resume automatic navigation

Waiting for 12 words to first trigger, keep speaking...
```

**Gerçek‑Zamanlı Geri Bildirim**:

```
[3/25]
Speech  -> learning fundamentals of machine learning algorithms
Match   -> machine learning fundamentals and basic concepts overview

[Manual Next] 3/25 -> 4/25

[Paused]

[Resumed]
```

**Çıkış**:

```
Control session ended.
```

## Ayar Yönetimi Komutları

### `settings list` - Mevcut Yapılandırmayı Göster

```bash
uv run python app.py settings list
```

**Amaç**: Mevcut sistem ayarlarını gösterir.

**Çıktı**:

```
Application Settings.
    model (LLM Model) -> gemini/gemini-2.0-flash
    key (API Key) -> your-api-key-here
```

**Yapılandırılmamış Çıktı**:

```
Application Settings.
    model (LLM Model) -> Not configured
    key (API Key) -> Not configured
```

### `settings set` - Ayar Değerini Güncelle

```bash
uv run python app.py settings set <KEY> <VALUE>
```

**Amaç**: LLM modeli ve API anahtarı gibi sistem ayarlarını yapılandırır.

**Argümanlar**:

- `KEY`: Ayar adı (`model` ya da `key`)
- `VALUE`: Yeni ayar değeri

**Örnekler**:

```bash
# LLM modelini ayarla
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set model "gpt-4"
uv run python app.py settings set model "claude-3-opus"

# API anahtarını ayarla
uv run python app.py settings set key "your-api-key-here"
uv run python app.py settings set key "sk-1234567890abcdef..."
```

**Çıktı**:

```
Setting 'model' updated.
    New Value -> gemini/gemini-2.0-flash
```

**Hata İşleme**:

```bash
# Geçersiz anahtar
uv run python app.py settings set invalid_key "value"
# Output: Error: Invalid setting key 'invalid_key'
#         Valid keys: model, key
```

### `settings unset` - Varsayılan Değere Sıfırla

```bash
uv run python app.py settings unset <KEY>
```

**Amaç**: Bir ayarı varsayılan şablon değerine sıfırlar.

**Argümanlar**:

- `KEY`: Sıfırlanacak ayar adı

**Örnekler**:

```bash
# Modeli varsayılana sıfırla
uv run python app.py settings unset model

# API anahtarını (null'a) sıfırla
uv run python app.py settings unset key
```

**Çıktı**:

```
Setting 'model' reset to default.
    New Value -> gemini/gemini-2.0-flash
```

## Komut Desenleri

### Tutarlı Argüman Desenleri

Tüm komutlar ortak işlemler için tutarlı desenleri izler:

**Konuşmacı Çözümlemesi**:

- Komutlar konuşmacı adı ya da konuşmacı ID'si kabul eder
- İsimler büyük/küçük harfe duyarlıdır
- Tek eşleşmeler için otomatik ayrım yapılır
- Belirsiz eşleşmelerde net hata mesajları verilir

**Dosya Yolu İşleme**:

- Göreli ve mutlak yollar desteklenir
- Otomatik yol çözümlemesi ve doğrulama yapılır
- Eksik dosyalar için net hata mesajları
- Dosya adlarındaki boşlukların doğru işlenmesi

**Çıktı Biçimlendirme**:

- Tutarlı “Doğrudan Özet” formatı
- Anahtar ayrıntılarla başarı onayları
- Eyleme dönük rehberlik içeren hata mesajları
- Uzun süren işlemler için ilerleme göstergeleri

### Seçenek Kuralları

```bash
# Kısa ve uzun seçenekler
--presentation, -p    # Dosya yolu seçenekleri
--transcript, -t     # Dosya yolu seçenekleri
--all, -a           # Boolean bayrakları

# Tutarlı yardım metni
--help              # Tüm komutlarda mevcuttur
```

### Dönüş Kodları

Tüm komutlar tutarlı çıkış kodları kullanır:

- **0**: Başarı
- **1**: Hata (dosya bulunamadı, doğrulama hatası, işleme hatası)

## Hata İşleme

### Doğrulama Hataları

```bash
# Gerekli argümanlar eksik
uv run python app.py speaker add
# Output: Error: Missing argument 'NAME'

# Geçersiz dosya yolları
uv run python app.py speaker add "Test" nonexistent.pdf transcript.pdf
# Output: Could not add speaker 'Test'.
#         Presentation file not found: nonexistent.pdf
```

### Yapılandırma Hataları

```bash
# LLM yapılandırılmamış
uv run python app.py speaker process "Test Speaker"
# Output: Error: LLM model not configured. Use 'moves settings set model <model>' to configure.

# API anahtarı yapılandırılmamış
uv run python app.py speaker process "Test Speaker"
# Output: Error: LLM API key not configured. Use 'moves settings set key <key>' to configure.
```

### İşleme Hataları

```bash
# Konuşmacı bulunamadı
uv run python app.py speaker show "Unknown Speaker"
# Output: Error: No speaker found matching 'Unknown Speaker'.

# Konuşmacı işlenmemiş
uv run python app.py presentation control "Unprocessed Speaker"
# Output: Error: Speaker 'Unprocessed Speaker' has not been processed yet.
#         Please run 'moves speaker process' first to generate sections.
```

### Ağ/API Hataları

```bash
# LLM işleme hatası
uv run python app.py speaker process "Test Speaker"
# Output: Processing error: LLM call failed: Invalid API key
```

## Kullanım Örnekleri

### Tam İş Akışı Örneği

```bash
# 1. Sistemi yapılandır
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-api-key"

# 2. Konuşmacı ekle
uv run python app.py speaker add "Dr. AI Expert" ./ai-presentation.pdf ./ai-transcript.pdf

# 3. Konuşmacı durumunu kontrol et
uv run python app.py speaker list
# "Not Ready" gösterir

# 4. AI gezinme için işle
uv run python app.py speaker process "Dr. AI Expert"

# 5. İşlenmeyi doğrula
uv run python app.py speaker show "Dr. AI Expert"
# "Ready" gösterir

# 6. Sunumu başlat
uv run python app.py presentation control "Dr. AI Expert"
# Ses kontrollü gezinme başlar
```

### Toplu İşlemler Örneği

```bash
# Birden fazla konuşmacı ekle
uv run python app.py speaker add "Speaker 1" ./pres1.pdf ./trans1.pdf
uv run python app.py speaker add "Speaker 2" ./pres2.pdf ./trans2.pdf
uv run python app.py speaker add "Speaker 3" ./pres3.pdf ./trans3.pdf

# Hepsini bir kerede işle
uv run python app.py speaker process --all

# Tüm konuşmacıları listele
uv run python app.py speaker list
```

### Ayar Yönetimi Örneği

```bash
# Mevcut ayarları kontrol et
uv run python app.py settings list

# Farklı modelleri dene
uv run python app.py settings set model "gpt-4"
uv run python app.py settings set model "claude-3-opus"

# Varsayılanlara sıfırla
uv run python app.py settings unset model
uv run python app.py settings unset key
```

### Hata Kurtarma Örneği

```bash
# Başlangıçtaki kurulumu takiben dosyaları güncelle
uv run python app.py speaker edit "Dr. AI Expert" --presentation ./updated-presentation.pdf

# Dosya değişikliklerinden sonra yeniden işle
uv run python app.py speaker process "Dr. AI Expert"

# İş bittiğinde temizle
uv run python app.py speaker delete "Dr. AI Expert"
```

CLI, karmaşık AI‑tabanlı sunum kontrolünü basit, tutarlı komutlarla erişilebilir kılan güçlü ve kullanıcı dostu bir arayüz sunar. Kapsamlı yardım sistemi, hata işleme ve geri bildirim mekanizmaları, kullanıcıların konuşmacıları yönetmesini, sunumları kontrol etmesini ve sistemi yapılandırmasını etkili bir şekilde yapmasını sağlar.
