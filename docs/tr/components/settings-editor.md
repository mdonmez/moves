# Ayarlar Düzenleyicisi

`SettingsEditor`, varsayılan değerler sağlayan ve kullanıcı özelleştirmesine izin veren şablon‑tabanlı bir yaklaşımla sistem yapılandırmasını yönetir. LLM modeli seçimi, API anahtarı yönetimi ve diğer sistem ayarlarını otomatik doğrulama ve yedekleme mekanizmalarıyla ele alır.

## İçindekiler

- [Genel Bakış](#overview)
- [Şablon Tabanlı Yapılandırma](#template-based-configuration)
- [Yapılandırma Yönetimi](#configuration-management)
- [Ayar İşlemleri](#settings-operations)
- [Veri Kalıcılığı](#data-persistence)
- [Doğrulama ve Hata Yönetimi](#validation-and-error-handling)
- [Kullanım Örnekleri](#usage-examples)

## Genel Bakış

**Konum**: `src/core/settings_editor.py`

SettingsEditor, varsayılan şablonları kullanıcı özelleştirmeleriyle birleştiren sağlam bir yapılandırma yönetim sistemi sunar. Yedek varsayılanları korurken yapılandırılabilir parametreler üzerinde tam kullanıcı kontrolüne izin vererek sistem güvenilirliğini sağlar.

```python
class SettingsEditor:
    template = Path("src/data/settings_template.yaml")
    settings = data_handler.DATA_FOLDER / Path("settings.yaml")

    def __init__(self):
        # Load template defaults
        self.template_data = yaml.load(self.template.read_text()) or {}

        # Load user settings
        user_data = yaml.load(data_handler.read(self.settings)) or {}

        # Merge template + user settings
        self._data = {**self.template_data, **user_data}
```

## Şablon Tabanlı Yapılandırma

### Şablon Yapısı

**Konum**: `src/data/settings_template.yaml`

```yaml
# LLM to be used for section generation based on transcript and presentation
# Available providers and models: https://models.litellm.ai/
model: gemini/gemini-2.0-flash

# API key for the LLM provider.
key: null
```

### Şablon Yükleme Stratejisi

```python
def __init__(self):
    try:
        # Load template with error handling
        self.template_data = yaml.load(self.template.read_text(encoding="utf-8")) or {}
    except Exception:
        # Graceful fallback for missing/corrupted template
        self.template_data = {}

    try:
        # Load existing user settings
        user_data = yaml.load(data_handler.read(self.settings)) or {}
    except Exception:
        # Handle missing user settings file
        user_data = {}

    # Template provides defaults, user settings override
    self._data = ({**self.template_data, **user_data}
                  if isinstance(self.template_data, dict) else user_data)
```

**Şablon Özellikleri**:

- **Varsayılan Değerler**: Tüm ayarlar için mantıklı varsayılanlar sağlar
- **Belgelendirme**: Her ayarı açıklayan yorumlar içerir
- **Genişletilebilirlik**: Yeni yapılandırma seçenekleri eklemek kolaydır
- **Doğrulama**: Geçerli yapılandırma anahtarları için şema işlevi görür

## Yapılandırma Yönetimi

### Ayarlar Hiyerarşisi

SettingsEditor, üç seviyeli bir yapılandırma hiyerarşisi uygular:

```
1. Şablon Varsayılanları (en düşük öncelik)
   ↓
2. Kullanıcı Ayarları (orta öncelik)
   ↓
3. Çalışma Zamanı Değerleri (en yüksek öncelik)
```

### Veri Birleştirme Mantığı

```python
# Configuration merge priority:
self._data = {**self.template_data, **user_data}

# Template provides structure and defaults:
template_data = {
    "model": "gemini/gemini-2.0-flash",
    "key": None
}

# User overrides specific values:
user_data = {
    "model": "gpt-4",
    "key": "user-api-key"
}

# Result combines both:
final_data = {
    "model": "gpt-4",           # User override
    "key": "user-api-key"       # User override
}
```

### Otomatik Başlatma

```python
def __init__(self):
    # Load and merge configurations
    # ...

    try:
        # Automatically save merged configuration
        self._save()
    except Exception:
        # Non-fatal: continue with in-memory config
        pass
```

## Ayar İşlemleri

### Değer Ayarlama

```python
def set(self, key: str, value: str) -> bool:
    # Validate key exists in template
    if key not in self.template_data:
        return False

    # Update in-memory data
    self._data[key] = value

    try:
        # Persist to disk
        self._save()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to set key '{key}': {e}") from e
```

**Ayar Süreci**:

1. **Doğrulama**: Anahtarın şablon şemasında bulunduğunu doğrula
2. **Bellek Güncellemesi**: Bellekteki yapılandırmayı güncelle
3. **Kalıcı Kılma**: Diskte kaydet, hata yönetimi uygula
4. **Sonuç**: Başarı/başarısızlık durumunu döndür

### Değer Kaldırma (Varsayılanına Sıfırlama)

```python
def unset(self, key: str) -> bool:
    if key in self.template_data:
        # Reset to template default
        self._data[key] = self.template_data[key]
    else:
        # Remove non-template key
        self._data.pop(key, None)

    try:
        self._save()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to unset key '{key}': {e}") from e
```

**Kaldırma Mantığı**:

- **Şablon Anahtarları**: Şablon varsayılan değerine sıfırla
- **Şablon Dışı Anahtarlar**: Yapılandırmadan tamamen kaldır
- **Kalıcı Kılma**: Değişiklikleri diske kaydet

### Ayarları Getirme

```python
def list(self) -> Settings:
    return Settings(**self._data)
```

`list()` yöntemi, yapılandırma verileri için yapı ve doğrulama sağlayan güçlü tiplenmiş bir `Settings` nesnesi döndürür.

## Veri Kalıcılığı

### Dosya Biçimi ve Konumu

- **Biçim**: İnsan tarafından okunabilir ve düzenlenebilir olması için YAML
- **Konum**: `~/.moves/settings.yaml`
- **Kodlama**: Uluslararası karakter desteği için UTF-8

### Kaydetme İşlemi

```python
def _save(self) -> bool:
    try:
        # Ensure data directory exists
        self.settings.parent.mkdir(parents=True, exist_ok=True)

        # Create node based on template structure
        node = copy.deepcopy(self.template_data) if isinstance(self.template_data, dict) else {}

        # Update with current values
        for key in node.keys():
            if key in self._data:
                node[key] = self._data[key]

        # Write to file
        with self.settings.open("w", encoding="utf-8") as f:
            yaml.dump(node, f)
        return True

    except Exception as e:
        raise RuntimeError(f"Failed to save settings: {e}") from e
```

**Kaydetme Özellikleri**:

- **Dizin Oluşturma**: Veri dizinlerini otomatik olarak oluşturur
- **Şablon Yapısı**: Şablon formatını ve sırasını korur
- **Atomik İşlemler**: Mümkün olduğunda dosya işlemleri atomiktir
- **Hata Yönetimi**: Kapsamlı hata raporlaması sağlar

### Örnek Kaydedilmiş Yapılandırma

```yaml
# ~/.moves/settings.yaml
model: gpt-4
key: sk-1234567890abcdef...
```

## Doğrulama ve Hata Yönetimi

### Anahtar Doğrulama

```python
def set(self, key: str, value: str) -> bool:
    if key not in self.template_data:
        return False  # Invalid key
    # Proceed with setting
```

SettingsEditor, şablon şemasına karşı tüm ayar anahtarlarını doğrular; geçersiz yapılandırmaların önüne geçilir.

### Hata Kurtarma

```python
def __init__(self):
    try:
        self.template_data = yaml.load(self.template.read_text()) or {}
    except Exception:
        # Graceful fallback to empty template
        self.template_data = {}

    try:
        user_data = yaml.load(data_handler.read(self.settings)) or {}
    except Exception:
        # Handle missing or corrupted user settings
        user_data = {}
```

**Kurtarma Stratejileri**:

- **Şablon Yedekleme**: Yükleme başarısız olursa boş şablonla devam eder
- **Kullanıcı Ayarları Yedekleme**: Kullanıcı ayarları bozuksa varsayılanları kullanır
- **Zarif Azalma**: Sistem minimal yapılandırma ile işlevsel kalır

### Hata Yayma

```python
def set(self, key: str, value: str) -> bool:
    try:
        self._save()
        return True
    except Exception as e:
        # Provide context-aware error messages
        raise RuntimeError(f"Failed to set key '{key}': {e}") from e
```

## Kullanım Örnekleri

### Temel Ayar İşlemleri

```python
# Initialize settings editor
settings_editor = SettingsEditor()

# Check current settings
settings = settings_editor.list()
print(f"Model: {settings.model}")
print(f"API Key: {settings.key}")

# Update LLM model
success = settings_editor.set("model", "gpt-4")
if success:
    print("Model updated successfully")

# Update API key
settings_editor.set("key", "sk-1234567890abcdef...")

# Reset to defaults
settings_editor.unset("model")  # Back to gemini/gemini-2.0-flash
```

### CLI Entegrasyonu

```python
@settings_app.command("set")
def settings_set(key: str, value: str):
    try:
        settings_editor = SettingsEditor()

        # Validate key
        valid_keys = ["model", "key"]
        if key not in valid_keys:
            typer.echo(f"Error: Invalid setting key '{key}'", err=True)
            typer.echo(f"Valid keys: {', '.join(valid_keys)}", err=True)
            raise typer.Exit(1)

        # Update setting
        success = settings_editor.set(key, value)
        if success:
            typer.echo(f"Setting '{key}' updated.")
            typer.echo(f"    New Value -> {value}")
        else:
            typer.echo(f"Could not update setting '{key}'.", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)
```

### Ayar Görüntüleme

```python
@settings_app.command("list")
def settings_list():
    try:
        settings_editor = SettingsEditor()
        settings = settings_editor.list()

        typer.echo("Application Settings.")

        # Display with formatting
        model_value = settings.model if settings.model else "Not configured"
        typer.echo(f"    model (LLM Model) -> {model_value}")

        if settings.key:
            typer.echo(f"    key (API Key) -> {settings.key}")
        else:
            typer.echo("    key (API Key) -> Not configured")

    except Exception as e:
        typer.echo(f"Error accessing settings: {str(e)}", err=True)
        raise typer.Exit(1)
```

### Yapılandırma Doğrulama

```python
def validate_settings(settings_editor: SettingsEditor) -> tuple[bool, list[str]]:
    """Validate current settings for completeness"""
    settings = settings_editor.list()
    issues = []

    if not settings.model:
        issues.append("LLM model not configured")

    if not settings.key:
        issues.append("API key not configured")

    return len(issues) == 0, issues

# Usage in processing workflow
settings_editor = SettingsEditor()
valid, issues = validate_settings(settings_editor)

if not valid:
    for issue in issues:
        print(f"Configuration issue: {issue}")
    print("Please configure settings before processing speakers.")
```

### Gelişmiş Şablon Yönetimi

```python
# Access template information
settings_editor = SettingsEditor()
template_keys = list(settings_editor.template_data.keys())
print(f"Available settings: {template_keys}")

# Check if setting has default
for key in template_keys:
    default_value = settings_editor.template_data[key]
    current_value = settings_editor._data[key]

    if default_value != current_value:
        print(f"{key}: {default_value} -> {current_value} (customized)")
    else:
        print(f"{key}: {current_value} (default)")
```

### Hata Yönetimi Örnekleri

```python
try:
    settings_editor = SettingsEditor()

    # Attempt invalid key
    success = settings_editor.set("invalid_key", "value")
    if not success:
        print("Invalid configuration key")

    # Valid operation
    settings_editor.set("model", "claude-3-opus")

except RuntimeError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

SettingsEditor, esnekliği güvenilirlikle dengeleyen sağlam ve kullanıcı dostu bir yapılandırma yönetim sistemi sunar. Şablon‑tabanlı yaklaşımı, sistemin her zaman mantıklı varsayılanlara sahip olmasını sağlarken kullanıcı tercihlerini tam anlamıyla özelleştirmeye olanak tanır.