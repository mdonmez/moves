# Yapılandırma

moves uses a template-based configuration system that provides sensible defaults while allowing full customization. Configuration covers LLM settings, system parameters, and runtime behavior.

## İçindekiler

- [Genel Bakış](#overview)
- [Yapılandırma Dosyaları](#configuration-files)
- [Ayar Şablonu](#settings-template)
- [LLM Yapılandırması](#llm-configuration)
- [Sistem Parametreleri](#system-parameters)
- [Çalışma Zamanı Yapılandırması](#runtime-configuration)
- [Ortam Değişkenleri](#environment-variables)
- [Yapılandırma Yönetimi](#configuration-management)

## Genel Bakış

moves yapılandırması hiyerarşik bir yaklaşım izler:

1. **Şablon Varsayılanları**: Mantıklı varsayılanlarla temel yapılandırma
2. **Kullanıcı Ayarları**: `~/.moves/settings.yaml` içinde depolanan kullanıcı geçersiz kılmaları
3. **Çalışma Zamanı Parametreleri**: Komut satırı argümanları ve kod düzeyinde yapılandırma

Bu katmanlı yaklaşım, sistemin her zaman çalışan varsayılanlara sahip olmasını sağlarken tam özelleştirmeye izin verir.

## Yapılandırma Dosyaları

### Ayar Şablonu

**Konum**: `src/data/settings_template.yaml`

```yaml
# LLM to be used for section generation based on transcript and presentation
# Available providers and models: https://models.litellm.ai/
model: gemini/gemini-2.0-flash

# API key for the LLM provider.
key: null
```

**Amaç**:

- Mevcut yapılandırma seçeneklerini tanımlar
- Tüm ayarlar için varsayılan değerler sağlar
- Yapılandırma seçenekleri için belge işlevi görür
- Doğrulama ve şema uygulaması için kullanılır

### Kullanıcı Ayarları Dosyası

**Konum**: `~/.moves/settings.yaml`

```yaml
model: gpt-4
key: sk-1234567890abcdef...
```

**Özellikler**:

- Ayarlar değiştirildiğinde otomatik olarak oluşturulur
- Yalnızca kullanıcı tarafından özelleştirilen değerleri içerir
- Çalışma zamanında şablon varsayılanları ile birleştirilir
- Kolay düzenleme için insan tarafından okunabilir YAML formatı

### Veri Dizini Yapısı

```
~/.moves/                           # User data directory
├── settings.yaml                   # User configuration overrides
├── logs/                          # Application logs
│   ├── speaker_manager.log
│   ├── presentation_controller.log
│   └── ...
└── speakers/                      # Speaker data
    └── {speaker-id}/              # Individual speaker directory
        ├── speaker.json           # Speaker metadata
        ├── presentation.pdf       # Local presentation copy
        ├── transcript.pdf         # Local transcript copy
        └── sections.json          # Generated navigation sections
```

## Ayar Şablonu

### Şablon Yapısı ve Belgeleri

```yaml
# LLM Model Configuration
# Specifies which Large Language Model to use for processing
# Format: provider/model-name
# Examples: gemini/gemini-2.0-flash, openai/gpt-4, anthropic/claude-3-opus
# Full list: https://models.litellm.ai/
model: gemini/gemini-2.0-flash

# API Key Configuration
# API key for the specified LLM provider
# Set to null by default (must be configured by user)
# Obtain from your LLM provider's dashboard
key: null
```

### Yapılandırma Doğrulama

Şablon, doğrulama için bir şema görevi görür:

```python
# Only template keys are allowed
valid_keys = ["model", "key"]

def set(self, key: str, value: str) -> bool:
    if key not in self.template_data:
        return False  # Invalid key rejected

    self._data[key] = value
    self._save()
    return True
```

**Doğrulama Yararları**:

- Yapılandırma anahtarlarındaki yazım hatalarını önler
- Tutarlı yapılandırma yapısını sağlar
- Geçersiz ayarlar için net hata mesajları sunar
- Sistem güncellemeleri arasında uyumluluğu korur

## LLM Yapılandırması

### Desteklenen Modeller ve Sağlayıcılar

#### Gemini (Google)

```yaml
# Recommended models
model: gemini/gemini-2.0-flash    # Fast, cost-effective (default)
model: gemini/gemini-pro          # Higher quality
model: gemini/gemini-1.5-pro      # Advanced capabilities
```

**API Anahtarı**: [Google AI Studio](https://aistudio.google.com/) adresinden alın

#### OpenAI

```yaml
model: gpt-4                      # High quality, higher cost
model: gpt-4-turbo               # Latest GPT-4 variant
model: gpt-3.5-turbo             # Cost-effective option
```

**API Anahtarı**: [OpenAI Dashboard](https://platform.openai.com/) adresinden alın

#### Anthropic

```yaml
model: claude-3-opus             # Highest quality
model: claude-3-sonnet           # Balanced performance
model: claude-3-haiku            # Fastest, most economical
```

**API Anahtarı**: [Anthropic Console](https://console.anthropic.com/) adresinden alın

#### Diğer Sağlayıcılar

moves, herhangi bir LiteLLM uyumlu sağlayıcıyı destekler:

```yaml
# Cohere
model: cohere/command-r-plus

# Mistral AI
model: mistral/mistral-large

# Azure OpenAI
model: azure/gpt-4

# Hugging Face
model: huggingface/microsoft/DialoGPT-medium
```

### Model Seçim Kriterleri

**Geliştirme/Test İçin**:

```yaml
model: gemini/gemini-2.0-flash # Fast, free tier available
```

**Üretim Kullanımı İçin**:

```yaml
model: gpt-4 # Consistent, high-quality results
```

**Bütçe Duyarlı Kullanım İçin**:

```yaml
model: gpt-3.5-turbo # Good quality, lower cost
```

**Gizlilik Odaklı Kullanım İçin**:

```yaml
# Consider local models via Ollama integration
model: ollama/llama2 # Self-hosted option
```

## Sistem Parametreleri

### Ses İşleme Yapılandırması

Bu parametreler şu anda sabit kodlu, ancak kaynakta değiştirilebilir:

```python
# In PresentationController.__init__()
self.frame_duration = 0.1          # 100ms frames
self.sample_rate = 16000           # 16kHz audio sampling
self.window_size = window_size     # 12 words by default
```

**Ayarlama Kılavuzları**:

- **frame_duration**: Daha düşük değerler = daha duyarlı, CPU kullanımı daha yüksek
- **sample_rate**: Konuşma tanıma için optimal 16kHz
- **window_size**: Daha büyük değerler = daha fazla bağlam, yanıt daha yavaş

### Konuşma Tanıma Yapılandırması

```python
# In PresentationController.__init__()
self.recognizer = OnlineRecognizer.from_transducer(
    tokens="src/core/components/ml_models/stt/tokens.txt",
    encoder="src/core/components/ml_models/stt/encoder.int8.onnx",
    decoder="src/core/components/ml_models/stt/decoder.int8.onnx",
    joiner="src/core/components/ml_models/stt/joiner.int8.onnx",
    num_threads=8,                 # Adjust based on CPU cores
    decoding_method="greedy_search"
)
```

### Benzerlik Hesaplama Yapılandırması

```python
# In SimilarityCalculator.__init__()
self.semantic_weight = 0.4         # 40% semantic similarity
self.phonetic_weight = 0.6         # 60% phonetic similarity
```

**Ağırlık Ayarı**:

- Anlam temelli eşleşme için `semantic_weight` artırın
- Konuşma tanıma hatası toleransı için `phonetic_weight` artırın

## Çalışma Zamanı Yapılandırması

### Sunum Kontrolcüsü Parametreleri

```python
def __init__(
    self,
    sections: list[Section],
    start_section: Section,
    window_size: int = 12,         # Configurable speech window
):
```

**Pencere Boyutu Kılavuzları**:

- **8-10**: Daha hızlı yanıt, daha az bağlam
- **12-15**: Dengeli (önerilir)
- **16-20**: Daha fazla bağlam, daha yavaş yanıt

### Parça Üretici Yapılandırması

```python
def generate_chunks(sections: list[Section], window_size: int = 12):
    # Window size should match PresentationController
```

### Benzerlik Hesaplayıcı Yapılandırması

```python
def __init__(self, semantic_weight: float = 0.4, phonetic_weight: float = 0.6):
    # Weights must sum to 1.0
```

## Ortam Değişkenleri

### Geliştirme Ortamı

```bash
# Optional: Override default data directory
export MOVES_DATA_DIR="/custom/path/to/moves/data"

# Optional: Debug logging
export MOVES_DEBUG=1

# Optional: Custom model cache location
export MOVES_MODEL_CACHE="/path/to/model/cache"
```

### Üretim Ortamı

```bash
# Recommended: Set data directory
export MOVES_DATA_DIR="/var/lib/moves"

# Recommended: Log level
export MOVES_LOG_LEVEL="INFO"

# Security: Restrict file permissions
umask 077
```

## Yapılandırma Yönetimi

### CLI (Komut Satırı) Yapılandırma Komutları

```bash
# View current settings
uv run python app.py settings list

# Update LLM model
uv run python app.py settings set model "gpt-4"

# Update API key
uv run python app.py settings set key "your-api-key"

# Reset to defaults
uv run python app.py settings unset model
uv run python app.py settings unset key
```

### Programatik Yapılandırma

```python
from src.core.settings_editor import SettingsEditor

# Initialize settings manager
settings_editor = SettingsEditor()

# Get current settings
settings = settings_editor.list()
print(f"Current model: {settings.model}")
print(f"API key configured: {'Yes' if settings.key else 'No'}")

# Update settings
settings_editor.set("model", "claude-3-opus")
settings_editor.set("key", "your-api-key")

# Reset settings
settings_editor.unset("model")  # Back to template default
```

### Yapılandırma Doğrulama

```python
def validate_configuration(settings_editor: SettingsEditor) -> tuple[bool, list[str]]:
    """Validate current configuration for completeness"""
    settings = settings_editor.list()
    issues = []

    # Check required settings
    if not settings.model:
        issues.append("LLM model not configured")

    if not settings.key:
        issues.append("API key not configured")

    # Validate model format
    if settings.model and "/" not in settings.model:
        issues.append("Model should be in format 'provider/model'")

    # Check API key format (basic validation)
    if settings.key and len(settings.key) < 10:
        issues.append("API key appears too short")

    return len(issues) == 0, issues
```

### Yapılandırma Yedekleme ve Göç

```python
import shutil
from datetime import datetime

def backup_configuration():
    """Create backup of current configuration"""
    settings_file = data_handler.DATA_FOLDER / "settings.yaml"
    if settings_file.exists():
        backup_name = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        backup_path = data_handler.DATA_FOLDER / backup_name
        shutil.copy2(settings_file, backup_path)
        print(f"Configuration backed up to {backup_path}")

def restore_configuration(backup_path: Path):
    """Restore configuration from backup"""
    settings_file = data_handler.DATA_FOLDER / "settings.yaml"
    shutil.copy2(backup_path, settings_file)
    print(f"Configuration restored from {backup_path}")
```

### Yapılandırma Örnekleri

#### Temel Kurulum

```bash
# Minimal configuration for getting started
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-gemini-api-key"
```

#### Üretim Kurulumu

```bash
# High-quality model for production use
uv run python app.py settings set model "gpt-4"
uv run python app.py settings set key "sk-your-openai-api-key"
```

#### Geliştirme Kurulumu

```bash
# Fast model for development and testing
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-development-api-key"
```

#### Maliyet Optimize Kurulum

```bash
# Budget-friendly model configuration
uv run python app.py settings set model "gpt-3.5-turbo"
uv run python app.py settings set key "sk-your-openai-api-key"
```

### Gelişmiş Yapılandırma

#### Özel Model Ağırlıkları

```python
# Create custom similarity calculator with adjusted weights
from src.core.components.similarity_calculator import SimilarityCalculator

# Favor semantic understanding over phonetic matching
custom_calculator = SimilarityCalculator(
    semantic_weight=0.7,  # Emphasize meaning
    phonetic_weight=0.3   # Reduce phonetic influence
)

# Use in presentation controller
controller = PresentationController(
    sections=sections,
    start_section=start_section,
    window_size=10  # Smaller window for faster response
)
controller.similarity_calculator = custom_calculator
```

#### Performans Ayarı

```python
# Tune for different hardware configurations

# High-end system: More threads, larger windows
recognizer_config = {
    "num_threads": 16,
    "window_size": 16
}

# Low-end system: Fewer threads, smaller windows
recognizer_config = {
    "num_threads": 4,
    "window_size": 8
}

# Battery-optimized: Reduce processing intensity
recognizer_config = {
    "num_threads": 2,
    "frame_duration": 0.2,  # Less frequent processing
    "window_size": 8
}
```

Yapılandırma sistemi, farklı kullanım senaryoları için esneklik sağlarken temel kullanım için sadeliği korur. Şablon tabanlı yaklaşım güvenilirlik sağlar ve özelleştirme için net rehberlik sunar.
