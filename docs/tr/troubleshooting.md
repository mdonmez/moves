# Sorun Giderme Kılavuzu

Bu kılavuz, moves uygulamasını kullanırken karşılaşabileceğiniz yaygın sorunlar, hata mesajları ve performans problemleri için çözümler sunar.

## İçindekiler

- [Hızlı Tanı](#quick-diagnosis)
- [Kurulum Sorunları](#installation-issues)
- [Ses Sistemi Problemleri](#audio-system-problems)
- [Yapay Zeka Modeli Sorunları](#ai-model-issues)
- [Yapılandırma Problemleri](#configuration-problems)
- [Performans Sorunları](#performance-issues)
- [Yaygın Hata Mesajları](#common-error-messages)
- [Veri ve Dosya Sorunları](#data-and-file-issues)
- [Ağ ve API Sorunları](#network-and-api-issues)
- [İleri Düzey Hata Ayıklama](#advanced-debugging)

## Hızlı Tanı

### Sağlık Kontrol Komutu

```bash
# Run system health check
python app.py speaker --help  # Basic CLI functionality
python -c "from src.utils.logger import logger; logger.info('System check')"  # Logging
python -c "from src.core.settings_editor import SettingsEditor; print('Settings OK')"  # Configuration
```

### Yaygın Hızlı Çözümler

```bash
# 1. Clear cache and restart
rm -rf __pycache__ src/**/__pycache__
python app.py settings list

# 2. Reset configuration
rm ~/.moves/settings.yaml
python app.py settings list  # Will recreate with defaults

# 3. Check permissions
ls -la ~/.moves/
chmod 755 ~/.moves/
```

### Log Analizi

```bash
# View recent logs
tail -50 ~/.moves/logs/moves.log

# Search for errors
grep -i "error" ~/.moves/logs/moves.log
grep -i "exception" ~/.moves/logs/moves.log

# Filter by severity
grep "ERROR\|CRITICAL" ~/.moves/logs/moves.log
```

## Kurulum Sorunları

### Python Sürüm Problemleri

**Sorun**: `Python version 3.13+ required`

```bash
# Check Python version
python --version
python3 --version

# Solution: Install Python 3.13+
# On macOS with Homebrew:
brew install python@3.13

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.13 python3.13-venv

# On Windows: Download from python.org
```

### Bağımlılık Kurulum Hataları

**Sorun**: `Failed to install packages`

```bash
# Common solutions:

# 1. Clear pip cache
pip cache purge

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Use UV (recommended)
pip install uv
uv venv
uv sync

# 4. Install with verbose output to see errors
pip install -v -r requirements.txt
```

**Sorun**: `Microsoft Visual C++ 14.0 required` (Windows)

```bash
# Solution: Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Alternative: Install specific packages with pre-compiled wheels
pip install --only-binary=all package_name
```

### Sanal Ortam Sorunları

**Sorun**: `Virtual environment not activated`

```bash
# Check if venv is active
echo $VIRTUAL_ENV

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Verify activation
which python  # Should show path in .venv
```

## Ses Sistemi Problemleri

### Mikrofon Algılanmadı

**Sorun**: `AudioError: No audio input device found`

```bash
# Diagnose audio system
python -c "
import pyaudio
p = pyaudio.PyAudio()
print(f'Audio devices: {p.get_device_count()}')
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'Input device {i}: {info[\"name\"]}')
p.terminate()
"
```

**Çözümler:**

1. **Check system audio settings**
   - Ensure microphone is enabled
   - Check privacy settings (macOS/Windows)
   - Verify microphone permissions
2. **Install audio drivers**
   - Update audio drivers
   - Restart audio services
3. **Test with different microphone**
   - Try USB microphone
   - Try headset microphone

### Ses İzni Reddedildi

**Sorun**: `PermissionError: Audio access denied`

**macOS Çözümü**:

```bash
# Check microphone permissions
# System Preferences > Security & Privacy > Privacy > Microphone
# Ensure Terminal/Python has microphone access

# Reset permissions
sudo tccutil reset Microphone
```

**Linux Çözümü**:

```bash
# Check audio group membership
groups $USER | grep audio

# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again

# Check PulseAudio
pulseaudio --check
```

**Windows Çözümü**:

```powershell
# Check Windows privacy settings
# Settings > Privacy > Microphone
# Ensure "Allow apps to access your microphone" is enabled

# Reset audio drivers
# Device Manager > Audio inputs > Uninstall > Scan for hardware changes
```

### Kötü Ses Kalitesi

**Sorun**: Konuşma tanıma doğruluğu düşük

**Çözümler:**

1. **Check microphone placement**
   - Position 6-12 inches from mouth
   - Avoid background noise
   - Use directional microphone
2. **Adjust audio settings**
   ```bash
   python app.py settings set audio_sample_rate 44100  # Higher quality
   python app.py settings set audio_frame_duration 0.05  # More responsive
   ```
3. **Test audio quality**
   - Record test audio and check clarity

## Yapay Zeka Modeli Sorunları

### Konuşma‑Metin Modeli Problemleri

**Sorun**: `ModelLoadError: Failed to load STT model`

```bash
# Check model files
ls -la src/core/components/ml_models/stt/
# Should contain: encoder.int8.onnx, decoder.int8.onnx, joiner.int8.onnx, tokens.txt
```

- Re-download models if missing
- Models should be included in repository
- If missing, check git LFS or download separately
- Check file permissions
  ```bash
  chmod 644 src/core/components/ml_models/stt/*
  ```
- Verify ONNX runtime
  ```bash
  python -c "import onnxruntime; print(onnxruntime.__version__)"
  ```

**Sorun**: `RuntimeError: ONNX model execution failed`

**Çözümler:**

1. **Check available compute providers**
   ```bash
   python -c "
   import onnxruntime
   print('Available providers:', onnxruntime.get_available_providers())
   "
   ```
2. **Use CPU-only execution**
   ```bash
   python -c "
   import onnxruntime
   session = onnxruntime.InferenceSession('model.onnx', providers=['CPUExecutionProvider'])
   "
   ```
3. **Update ONNX runtime**
   ```bash
   pip install --upgrade onnxruntime
   ```

### Gömme Modeli Sorunları

**Sorun**: `Failed to load embedding model`

```bash
# Check embedding model
ls -la src/core/components/ml_models/embedding/
# Should contain model files and configuration
```

- Verify sentence-transformers
  ```bash
  python -c "
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer('src/core/components/ml_models/embedding')
  print('Model loaded successfully')
  "
  ```
- Clear transformers cache if corrupted
  ```bash
  rm -rf ~/.cache/huggingface/transformers/
  ```

### Büyük Dil Modeli API Sorunları

**Sorun**: `API key not configured`

```bash
# Check API key configuration
python app.py settings list | grep llm_api_key

# Set API key
python app.py settings set llm_api_key "your-api-key-here"

# Test API connectivity
python -c "
from litellm import completion
response = completion(
    model='gemini/gemini-2.0-flash',
    api_key='your-key',
    messages=[{'role': 'user', 'content': 'test'}],
    max_tokens=10
)
print('API test successful')
"
```

**Sorun**: `Rate limit exceeded`

**Çözümler:**

1. Wait for rate limit reset
2. Switch to different model/provider
   ```bash
   python app.py settings set llm_model "gpt-3.5-turbo"
   ```
3. Implement exponential backoff in code  
   (Already implemented in section_producer.py)

## Yapılandırma Problemleri

### Ayarlar Dosyası Sorunları

**Sorun**: `Settings file corrupted or invalid`

```bash
# Backup current settings
cp ~/.moves/settings.yaml ~/.moves/settings.yaml.backup

# Reset to defaults
rm ~/.moves/settings.yaml
python app.py settings list  # Recreates with defaults

# Validate settings format
python -c "
import yaml
with open('~/.moves/settings.yaml') as f:
    settings = yaml.safe_load(f)
    print('Settings file is valid YAML')
"
```

**Sorun**: `SettingNotFoundError: Setting key not found`

```bash
# List all available settings
python app.py settings list

# Check setting name spelling
python app.py settings list | grep -i "setting_name"

# Use exact key name from template
cat src/data/settings_template.yaml
```

### Ortam Değişkenleri

**Sorun**: Ortam değişkenleri tanınmıyor

```bash
# Check environment variables
env | grep -E "(GEMINI|OPENAI|ANTHROPIC)_API_KEY"

# Set environment variables
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Make permanent (add to shell profile)
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

## Performans Sorunları

### Yavaş Konuşma Tanıma

**Sorun**: Konuşma tanıma gecikmesi yüksek

```bash
# Diagnose performance
python -c "
import time
from src.core.presentation_controller import PresentationController

sections = ['test section']
controller = PresentationController(sections)

# Time model loading
start = time.time()
# controller initialization happens here
print(f'Model loading time: {time.time() - start:.2f}s')
"
```

**Çözümler:**

1. Reduce audio processing load
   ```bash
   python app.py settings set audio_frame_duration 0.2  # Less frequent processing
   ```
2. Optimize thread count
   ```bash
   python app.py settings set stt_threads 4  # Match CPU cores
   ```
3. Check CPU usage  
   `htop` # or Task Manager on Windows

### Yüksek Bellek Kullanımı

**Sorun**: Uygulama aşırı bellek tüketiyor

```bash
# Monitor memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

**Çözümler:**

1. Reduce batch sizes
   - Edit similarity calculation batch sizes
2. Clear caches periodically
   - Implement cache cleanup in long-running sessions
3. Use memory profiler
   ```bash
   pip install memory-profiler
   python -m memory_profiler your_script.py
   ```

### Yavaş Benzerlik Hesaplama

**Sorun**: Navigasyon yanıtı yavaş

```bash
# Profile similarity calculation
python -c "
import time
from src.core.components.similarity_calculator import SimilarityCalculator
from src.data.models import Chunk

# Create test data
chunks = [Chunk(f'chunk_{i}', 0, f'test content {i}', 0, 100) for i in range(100)]
calculator = SimilarityCalculator()

# Time calculation
start = time.time()
results = calculator.calculate_similarity('test input', chunks)
print(f'Similarity calculation time: {time.time() - start:.2f}s')
"
```

**Çözümler:**

1. Adjust similarity weights
   ```bash
   python app.py settings set similarity_semantic_weight 0.8
   python app.py settings set similarity_phonetic_weight 0.2
   ```
2. Reduce chunk count
   - Use smaller window size when processing presentations
3. Enable GPU acceleration (if available)
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Yaygın Hata Mesajları

### `FileNotFoundError`

**Hata**: `FileNotFoundError: [Errno 2] No such file or directory: '~/.moves/...'`

```bash
# Solution: Create missing directories
mkdir -p ~/.moves/logs
mkdir -p ~/.moves/speakers

# Check file permissions
ls -la ~/.moves/
chmod 755 ~/.moves/
```

### `ImportError`

**Hata**: `ImportError: No module named 'module_name'`

```bash
# Solution: Install missing dependencies
pip install module_name

# Or reinstall all dependencies
pip install -r requirements.txt

# Check virtual environment activation
which python  # Should show venv path
```

### `ValidationError`

**Hata**: `ValidationError: Setting value validation failed`

```bash
# Check setting type requirements
python app.py settings list | grep "setting_name"

# Use correct data type
python app.py settings set setting_name "string_value"
python app.py settings set numeric_setting 42
python app.py settings set boolean_setting true
```

### `ProcessingError`

**Hata**: `ProcessingError: PDF processing failed`

```bash
# Check PDF file accessibility
ls -la path/to/pdf/file.pdf

# Verify PDF is not corrupted
python -c "
import PyPDF2
with open('file.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    print(f'PDF has {len(reader.pages)} pages')
"
# Try with different PDF file
# Ensure PDF contains extractable text (not scanned images)
```

## Veri ve Dosya Sorunları

### Bozuk Veri Dosyaları

**Sorun**: Konuşmacı veya sunum verileri bozuk

```bash
# Check data file integrity
python -c "
import json
from pathlib import Path

data_dir = Path.home() / '.moves'
for json_file in data_dir.rglob('*.json'):
    try:
        with open(json_file) as f:
            json.load(f)
        print(f'✓ {json_file}')
    except json.JSONDecodeError as e:
        print(f'✗ {json_file}: {e}')
"
# Backup and recreate corrupted files
cp ~/.moves/speaker_id/presentation.json ~/.moves/speaker_id/presentation.json.backup
# Reprocess the presentation to recreate data
```

### Disk Alanı Sorunları

**Sorun**: Disk alanı yetersiz

```bash
# Check available space
df -h ~/.moves/

# Clean up old data
# Remove unused speakers
python app.py speaker delete unused_speaker_id

# Clean up logs
rm ~/.moves/logs/*.log.*

# Compress old data
tar -czf backup.tar.gz ~/.moves/old_speaker_data/
rm -rf ~/.moves/old_speaker_data/
```

### Dosya İzin Sorunları

**Sorun**: Dosyalara erişim izni reddedildi

```bash
# Fix permissions
chmod -R 755 ~/.moves/
chown -R $USER:$USER ~/.moves/

# On Windows, check file properties and security settings
```

## Ağ ve API Sorunları

### Bağlantı Zaman Aşımı

**Sorun**: `ConnectionError: API request timed out`

```bash
# Check internet connectivity
ping google.com
curl -I https://api.openai.com/v1/models

# Solutions:

# 1. Increase timeout settings
# Edit timeout values in section_producer.py

# 2. Check firewall settings
# Ensure outbound HTTPS (port 443) is allowed

# 3. Try different DNS servers
# Switch to 8.8.8.8 or 1.1.1.1
```

### SSL/TLS Sorunları

**Sorun**: `SSLError: certificate verify failed`

```bash
# Update certificates
pip install --upgrade certifi

# Check system time (SSL certificates are time-sensitive)
date

# Temporary workaround (not recommended for production)
export SSL_VERIFY=false
```

### API Kimlik Doğrulama Sorunları

**Sorun**: `AuthenticationError: Invalid API key`

```bash
# Verify API key format
echo $GEMINI_API_KEY | wc -c  # Should be reasonable length

# Test API key directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Check for invisible characters
echo $API_KEY | hexdump -C
```

## İleri Düzey Hata Ayıklama

### Hata Ayıklama Modu

Ayrıntılı hata ayıklamayı etkinleştir:

```bash
# Set debug logging level
export MOVES_LOG_LEVEL=DEBUG

# Run with debug output
python app.py --debug speaker list

# Enable Python debugging
export PYTHONPATH=src:$PYTHONPATH
python -m pdb app.py speaker list
```

### Bellek Hata Ayıklama

```bash
# Install memory debugging tools
pip install memory-profiler objgraph

# Monitor memory usage
python -c "
import objgraph
objgraph.show_most_common_types(limit=10)
"

# Track memory leaks
python -m memory_profiler your_script.py
```

### Performans Profilleme

```bash
# Profile application performance
python -m cProfile -s cumulative app.py speaker list

# Line-by-line profiling
pip install line_profiler
kernprof -l -v your_script.py
```

### Ağ Hata Ayıklama

```bash
# Monitor network requests
export PYTHONPATH=src:$PYTHONPATH
python -c "
import logging
import requests
import urllib3

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
requests.get('https://api.openai.com/v1/models',
             headers={'Authorization': 'Bearer your-key'})
"
```

- Wireshark for detailed packet analysis
- curl -v for HTTP debugging
- tcpdump for low-level network analysis

### Sistem Bilgisi Toplama

Bir hata raporu oluştur:

```bash
# Create system info script
cat << 'EOF' > debug_info.py
#!/usr/bin/env python3
import platform
import sys
import pkg_resources
from pathlib import Path

print("=== System Information ===")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Architecture: {platform.architecture()}")

print("\n=== Installed Packages ===")
for pkg in pkg_resources.working_set:
    print(f"{pkg.key}=={pkg.version}")

print("\n=== File System ===")
moves_dir = Path.home() / ".moves"
if moves_dir.exists():
    print(f"Data directory size: {sum(f.stat().st_size for f in moves_dir.rglob('*') if f.is_file())} bytes")
    print(f"Speaker count: {len(list(moves_dir.glob('speaker_*')))}")

print("\n=== Configuration ===")
try:
    from src.core.settings_editor import SettingsEditor
    editor = SettingsEditor()
    settings = editor.list_settings()
    for key, value in settings.items():
        print(f"{key}: {type(value['value']).__name__}")
except Exception as e:
    print(f"Configuration check failed: {e}")
EOF

python debug_info.py > debug_report.txt
```

Bu kılavuzda ele alınmayan bir sorunla karşılaşırsanız, lütfen:

1. **Logları kontrol edin**: `~/.moves/logs/moves.log`
2. **Bir hata raporu oluşturun**: Yukarıdaki debug bilgi betiğini kullanın
3. **Mevcut sorunları ara**: Benzer problemler için GitHub issue'larını kontrol edin
4. **Ayrıntılı bir bug raporu oluşturun**: Hata mesajlarını, debug raporunu ve yeniden üretme adımlarını ekleyin

Unutmayın: Çoğu sorun, doğru kurulum, yapılandırma ve dosya izinlerinin sağlanmasıyla çözülebilir. İleri düzey hata ayıklama tekniklerine geçmeden önce hızlı tanı adımlarıyla başlayın.
