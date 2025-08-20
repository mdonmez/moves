# Yardımcı Araçlar

Yardımcı araçlar modülü, moves uygulaması için temel destek fonksiyonlarını sağlar. Bu yardımcı araçlar, veri yönetimi, günlük tutma, metin işleme ve benzersiz kimlik oluşturma gibi ortak görevleri yönetir.

## İçindekiler

- [Genel Bakış](#overview)
- [Veri İşleyici](#data-handler)
- [Günlük Kaydedici](#logger)
- [Metin Normalleştirici](#text-normalizer)
- [Kimlik Üreteci](#id-generator)
- [Entegrasyon Kalıpları](#integration-patterns)
- [Hata Yönetimi](#error-handling)
- [Test Yardımcıları](#testing-utilities)

## Genel Bakış

Yardımcı araçlar `src/utils/` içinde bulunur ve temel yetenekleri sunar:

```
src/utils/
├── data_handler.py      # Dosya sistemi işlemleri ve veri yönetimi
├── logger.py           # Merkezi günlük kaydetme sistemi
├── text_normalizer.py  # Metin temizleme ve standartlaştırma
└── id_generator.py     # Benzersiz tanımlayıcı oluşturma
```

**Mimari Kalıp**:

```
┌─────────────────────────────────────────────────────────┐
│                  Çekirdek Uygulama                       │
├─────────────────────────────────────────────────────────┤
│                     Yardımcı Araçlar                     │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────────┐  │
│  │ Veri İşleyici│ │   Günlük   │ │ Metin Normalleştirici │  │
│  └──────────────┘ └─────────────┘ └──────────────────┘  │
│                    ┌─────────────┐                      │
│                    │Kimlik Üreteci│                      │
│                    └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## Veri İşleyici

**Konum**: `src/utils/data_handler.py`

Veri işleyici, moves uygulaması için dosya sistemi işlemlerini ve veri kalıcılığını yönetir.

### Temel Fonksiyonlar

#### Dizin Yönetimi

```python
def get_user_moves_dir() -> Path:
    """Get user's moves data directory (~/.moves)"""
    moves_dir = Path.home() / ".moves"
    moves_dir.mkdir(exist_ok=True)
    return moves_dir

def ensure_speaker_dir(speaker_id: str) -> Path:
    """Ensure speaker directory exists and return path"""
    speaker_dir = get_user_moves_dir() / speaker_id
    speaker_dir.mkdir(exist_ok=True)
    return speaker_dir

def ensure_presentation_dir(speaker_id: str, presentation_id: str) -> Path:
    """Ensure presentation directory exists within speaker directory"""
    presentation_dir = ensure_speaker_dir(speaker_id) / presentation_id
    presentation_dir.mkdir(exist_ok=True)
    return presentation_dir
```

**Oluşturulan Dizin Yapısı**:

```
~/.moves/
├── speaker_1/
│   ├── presentation_1/
│   │   ├── sections.json
│   │   ├── chunks.json
│   │   └── source_files/
│   └── presentation_2/
│       ├── sections.json
│       └── chunks.json
└── speaker_2/
    └── presentation_3/
        ├── sections.json
        └── chunks.json
```

#### Dosya İşlemleri

```python
def save_data_to_file(data: Any, file_path: Path, encoding: str = "utf-8") -> None:
    """Save data to file with proper encoding"""
    try:
        if isinstance(data, (dict, list)):
            # JSON serialization for structured data
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            # Text serialization for strings
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(str(data))
    except Exception as e:
        logger.error(f"Failed to save data to {file_path}: {e}")
        raise

def load_data_from_file(file_path: Path, encoding: str = "utf-8") -> Any:
    """Load data from file with automatic format detection"""
    try:
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read().strip()

        # Try JSON parsing first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Return as plain text
            return content

    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {e}")
        return None
```

#### Veri Doğrulama

```python
def validate_data_structure(data: Any, expected_type: type) -> bool:
    """Validate data matches expected structure"""
    try:
        if expected_type == list:
            return isinstance(data, list)
        elif expected_type == dict:
            return isinstance(data, dict)
        elif expected_type == str:
            return isinstance(data, str)
        else:
            return isinstance(data, expected_type)
    except Exception:
        return False

def backup_file(file_path: Path, backup_suffix: str = ".backup") -> Path:
    """Create backup of existing file before modification"""
    if not file_path.exists():
        return file_path

    backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
    backup_path.write_bytes(file_path.read_bytes())
    return backup_path
```

### Kullanım Örnekleri

```python
from src.utils.data_handler import (
    get_user_moves_dir,
    ensure_speaker_dir,
    save_data_to_file,
    load_data_from_file
)

# Uygulama veri dizinini al
data_dir = get_user_moves_dir()  # ~/.moves

# Konuşmacı dizininin var olduğunu garanti et
speaker_dir = ensure_speaker_dir("speaker_123")

# Yapılandırılmış veriyi kaydet
sections_data = [{"index": 0, "content": "Introduction"}]
save_data_to_file(sections_data, speaker_dir / "sections.json")

# Otomatik biçim algılamasıyla veriyi yükle
loaded_sections = load_data_from_file(speaker_dir / "sections.json")
```

## Günlük Kaydedici

**Konum**: `src/utils/logger.py`

Konfigüre edilebilir seviyeler ve çıktı formatlamasıyla merkezi bir günlük sistemi.

### Günlük Kaydedici Yapılandırması

```python
import logging
from pathlib import Path

def setup_logger(name: str = "moves", level: str = "INFO") -> logging.Logger:
    """Setup centralized logger with file and console output"""

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    log_dir = Path.home() / ".moves" / "logs"
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(log_dir / "moves.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logger()
```

### Günlük Seviyeleri ve Kullanım

```python
# Import the configured logger
from src.utils.logger import logger

# Different logging levels
logger.debug("Detailed debugging information")        # Development only
logger.info("General information about program flow")  # Normal operation
logger.warning("Warning about potential issues")       # Concerning but not critical
logger.error("Error that doesn't stop execution")      # Recoverable errors
logger.critical("Critical error requiring attention")  # System-level issues

# Contextual logging with variables
logger.info(f"Processing speaker: {speaker_id}")
logger.error(f"Failed to load presentation {presentation_id}: {error}")

# Exception logging with stack traces
try:
    risky_operation()
except Exception as e:
    logger.exception(f"Unexpected error in operation: {e}")
```

### Günlük Dosyası Yönetimi

```python
def rotate_logs(max_size_mb: int = 10) -> None:
    """Rotate log files when they exceed size limit"""
    log_file = Path.home() / ".moves" / "logs" / "moves.log"

    if not log_file.exists():
        return

    size_mb = log_file.stat().st_size / (1024 * 1024)

    if size_mb > max_size_mb:
        # Create numbered backup
        backup_file = log_file.with_suffix(f".log.{int(time.time())}")
        log_file.rename(backup_file)

        # Keep only last 5 backups
        log_dir = log_file.parent
        backups = sorted(log_dir.glob("*.log.*"))
        for old_backup in backups[:-5]:
            old_backup.unlink()

def get_recent_logs(lines: int = 100) -> list[str]:
    """Get recent log entries for debugging"""
    log_file = Path.home() / ".moves" / "logs" / "moves.log"

    if not log_file.exists():
        return []

    with open(log_file, 'r', encoding='utf-8') as f:
        return f.readlines()[-lines:]
```

## Metin Normalleştirici

**Konum**: `src/utils/text_normalizer.py`

Uygulama genelinde tutarlı işleme sağlamak için metin temizleme ve standartlaştırma sunar.

### Temel Normalleştirme Fonksiyonları

```python
import re
import unicodedata
from typing import Optional

class TextNormalizer:
    """Text normalization and cleaning utilities"""

    def __init__(self):
        # Common abbreviation patterns
        self.abbreviations = {
            "dr.": "doctor",
            "mr.": "mister",
            "mrs.": "missus",
            "ms.": "miss",
            "prof.": "professor",
            "vs.": "versus",
            "etc.": "etcetera"
        }

        # Number word mappings
        self.numbers = {
            "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
            "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"
        }

    def normalize_text(self, text: str) -> str:
        """Complete text normalization pipeline"""
        if not text or not isinstance(text, str):
            return ""

        # Step 1: Unicode normalization
        text = self.normalize_unicode(text)

        # Step 2: Case normalization
        text = text.lower()

        # Step 3: Expand abbreviations
        text = self.expand_abbreviations(text)

        # Step 4: Normalize numbers
        text = self.normalize_numbers(text)

        # Step 5: Clean punctuation and whitespace
        text = self.clean_punctuation(text)

        # Step 6: Normalize whitespace
        text = self.normalize_whitespace(text)

        return text.strip()

    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters to standard form"""
        # NFD normalization (canonical decomposition)
        text = unicodedata.normalize('NFD', text)

        # Remove combining characters (accents, etc.)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

        return text

    def expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations to full words"""
        words = text.split()
        expanded = []

        for word in words:
            # Check for abbreviations (case-insensitive)
            lower_word = word.lower()
            if lower_word in self.abbreviations:
                expanded.append(self.abbreviations[lower_word])
            else:
                expanded.append(word)

        return ' '.join(expanded)

    def normalize_numbers(self, text: str) -> str:
        """Convert single digits to word form for better speech processing"""
        words = text.split()
        normalized = []

        for word in words:
            # Handle simple single digits
            if word.isdigit() and len(word) == 1:
                normalized.append(self.numbers.get(word, word))
            else:
                normalized.append(word)

        return ' '.join(normalized)

    def clean_punctuation(self, text: str) -> str:
        """Clean and standardize punctuation"""
        # Remove common punctuation except apostrophes in contractions
        text = re.sub(r'[^\w\s\']', ' ', text)

        # Handle contractions properly
        text = re.sub(r"(\w)'(\w)", r"\1\2", text)  # don't -> dont

        # Remove standalone apostrophes
        text = re.sub(r"\s+'\s+", ' ', text)
        text = re.sub(r"^'\s+", '', text)
        text = re.sub(r"\s+'$", '', text)

        return text

    def normalize_whitespace(self, text: str) -> str:
        """Normalize all whitespace to single spaces"""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def remove_filler_words(self, text: str) -> str:
        """Remove common filler words that don't affect meaning"""
        filler_words = {
            'um', 'uh', 'er', 'ah', 'hmm', 'well', 'like', 'you know',
            'actually', 'basically', 'literally', 'obviously', 'clearly'
        }

        words = text.split()
        filtered = [word for word in words if word.lower() not in filler_words]
        return ' '.join(filtered)
```

### Özelleştirilmiş Normalleştirme

```python
def normalize_for_similarity(self, text: str) -> str:
    """Normalize text specifically for similarity comparison"""
    # Basic normalization
    text = self.normalize_text(text)

    # Remove filler words
    text = self.remove_filler_words(text)

    # Additional similarity-specific cleaning
    # Remove very short words (articles, prepositions)
    words = text.split()
    meaningful_words = [word for word in words if len(word) > 2]

    return ' '.join(meaningful_words)

def normalize_for_search(self, text: str) -> str:
    """Normalize text for search operations"""
    # Basic normalization but preserve more structure
    text = self.normalize_unicode(text)
    text = text.lower()

    # Less aggressive punctuation removal for search
    text = re.sub(r'[^\w\s\-\']', ' ', text)
    text = self.normalize_whitespace(text)

    return text.strip()
```

### Kullanım Örnekleri

```python
from src.utils.text_normalizer import TextNormalizer

normalizer = TextNormalizer()

# Basic normalization
raw_text = "Dr. Smith's presentation #1: It's REALLY good!"
normalized = normalizer.normalize_text(raw_text)
print(normalized)  # "doctor smiths presentation one its really good"

# For similarity comparison
similarity_text = normalizer.normalize_for_similarity(raw_text)
print(similarity_text)  # "doctor smiths presentation one really good"

# For search operations
search_text = normalizer.normalize_for_search(raw_text)
print(search_text)  # "doctor smith's presentation one its really good"
```

## Kimlik Üreteci

**Konum**: `src/utils/id_generator.py`

Konuşmacılar, sunumlar ve diğer varlıklar için benzersiz tanımlayıcılar üretir.

### Temel Kimlik Oluşturma

```python
import uuid
import hashlib
import time
from typing import Optional

class IDGenerator:
    """Generates various types of unique identifiers"""

    @staticmethod
    def generate_uuid() -> str:
        """Generate a standard UUID4"""
        return str(uuid.uuid4())

    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate a shorter, readable ID"""
        full_uuid = str(uuid.uuid4()).replace('-', '')
        return full_uuid[:length]

    @staticmethod
    def generate_timestamp_id() -> str:
        """Generate ID based on current timestamp"""
        timestamp = str(int(time.time() * 1000))  # Milliseconds
        random_suffix = str(uuid.uuid4())[:8]
        return f"{timestamp}_{random_suffix}"

    @staticmethod
    def generate_hash_id(content: str, length: int = 16) -> str:
        """Generate ID based on content hash"""
        hash_object = hashlib.sha256(content.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        return hash_hex[:length]

    @staticmethod
    def generate_readable_id(prefix: str = "", suffix: str = "") -> str:
        """Generate human-readable ID with optional prefix/suffix"""
        middle = str(uuid.uuid4())[:8]
        parts = [part for part in [prefix, middle, suffix] if part]
        return '_'.join(parts)
```

### Özelleştirilmiş Kimlik Türleri

```python
def generate_speaker_id(name: Optional[str] = None) -> str:
    """Generate speaker-specific ID"""
    if name:
        # Use name-based hash with timestamp for uniqueness
        name_hash = IDGenerator.generate_hash_id(name.lower().strip(), 6)
        timestamp = str(int(time.time()))[-4:]  # Last 4 digits
        return f"speaker_{name_hash}_{timestamp}"
    else:
        return f"speaker_{IDGenerator.generate_short_id()}"

def generate_presentation_id(title: Optional[str] = None) -> str:
    """Generate presentation-specific ID"""
    if title:
        # Clean title for ID generation
        clean_title = re.sub(r'[^\w\s]', '', title.lower())
        words = clean_title.split()[:3]  # First 3 words
        title_part = '_'.join(words) if words else "presentation"

        timestamp = str(int(time.time()))[-6:]  # Last 6 digits
        return f"{title_part}_{timestamp}"
    else:
        return f"presentation_{IDGenerator.generate_short_id()}"

def generate_chunk_id(section_index: int, chunk_index: int) -> str:
    """Generate chunk-specific ID"""
    return f"chunk_{section_index:03d}_{chunk_index:03d}"

def generate_session_id() -> str:
    """Generate session ID for tracking"""
    return f"session_{IDGenerator.generate_timestamp_id()}"
```

### Kimlik Doğrulama ve Yardımcı Fonksiyonlar

```python
def validate_id_format(id_string: str, pattern: str) -> bool:
    """Validate ID matches expected pattern"""
    import re
    try:
        return bool(re.match(pattern, id_string))
    except Exception:
        return False

def is_valid_uuid(id_string: str) -> bool:
    """Check if string is valid UUID"""
    try:
        uuid.UUID(id_string)
        return True
    except ValueError:
        return False

def extract_timestamp_from_id(id_string: str) -> Optional[int]:
    """Extract timestamp from timestamp-based ID"""
    try:
        if '_' in id_string:
            timestamp_part = id_string.split('_')[1]
            return int(timestamp_part)
    except (ValueError, IndexError):
        pass
    return None
```

### Kullanım Örnekleri

```python
from src.utils.id_generator import (
    IDGenerator,
    generate_speaker_id,
    generate_presentation_id,
    generate_chunk_id
)

# Basic ID generation
uuid_id = IDGenerator.generate_uuid()           # "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
short_id = IDGenerator.generate_short_id()      # "a1b2c3d4"
timestamp_id = IDGenerator.generate_timestamp_id()  # "1703123456789_a1b2c3d4"

# Specialized IDs
speaker_id = generate_speaker_id("John Doe")    # "speaker_abc123_4567"
presentation_id = generate_presentation_id("AI Overview")  # "ai_overview_123456"
chunk_id = generate_chunk_id(0, 1)              # "chunk_000_001"

# Content-based ID
content_id = IDGenerator.generate_hash_id("Important content")  # "f8e7d6c5b4a39281"
```

## Entegrasyon Kalıpları

### Çapraz-Yardımcı Koordinasyon

```python
# Common usage pattern across the application
from src.utils.logger import logger
from src.utils.data_handler import save_data_to_file, load_data_from_file
from src.utils.text_normalizer import TextNormalizer
from src.utils.id_generator import generate_speaker_id

class UtilityIntegration:
    """Example of coordinated utility usage"""

    def __init__(self):
        self.normalizer = TextNormalizer()
        logger.info("Utility integration initialized")

    def process_speaker_data(self, name: str, content: dict) -> str:
        """Process speaker data using multiple utilities"""

        # Generate unique ID
        speaker_id = generate_speaker_id(name)
        logger.info(f"Generated speaker ID: {speaker_id}")

        # Normalize text content
        if 'description' in content:
            content['description'] = self.normalizer.normalize_text(content['description'])

        # Save processed data
        file_path = get_user_moves_dir() / f"{speaker_id}.json"
        save_data_to_file(content, file_path)

        logger.info(f"Saved speaker data for {speaker_id}")
        return speaker_id
```

### Hata Yönetimi Kalıpları

```python
from src.utils.logger import logger

def safe_utility_operation(operation_func, *args, **kwargs):
    """Wrapper for safe utility operations with consistent error handling"""
    try:
        return operation_func(*args, **kwargs)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return None
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error in {operation_func.__name__}: {e}")
        return None

# Usage example
data = safe_utility_operation(load_data_from_file, file_path)
if data is None:
    logger.warning("Failed to load data, using defaults")
    data = default_data
```

## Hata Yönetimi

### Yaygın Hata Kalıpları

```python
# File system errors
try:
    data = load_data_from_file(file_path)
except FileNotFoundError:
    logger.warning(f"File not found: {file_path}, creating new")
    data = create_default_data()
except PermissionError:
    logger.error(f"Permission denied accessing: {file_path}")
    raise

# Text processing errors
try:
    normalized = normalizer.normalize_text(raw_text)
except Exception as e:
    logger.error(f"Text normalization failed: {e}")
    normalized = raw_text  # Fallback to original

# ID generation errors
try:
    new_id = generate_speaker_id(name)
except Exception as e:
    logger.error(f"ID generation failed: {e}")
    new_id = IDGenerator.generate_uuid()  # Fallback to UUID
```

## Test Yardımcıları

### Birim Test Yardımcıları

```python
import tempfile
import shutil
from pathlib import Path

class TestUtilities:
    """Testing utilities for utility modules"""

    def __init__(self):
        self.temp_dir = None
        self.normalizer = TextNormalizer()

    def setup_temp_directory(self) -> Path:
        """Create temporary directory for testing"""
        self.temp_dir = Path(tempfile.mkdtemp())
        return self.temp_dir

    def cleanup_temp_directory(self):
        """Clean up temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_test_data(self, data_type: str = "speaker") -> dict:
        """Create test data for various entity types"""
        if data_type == "speaker":
            return {
                "id": generate_speaker_id("Test Speaker"),
                "name": "Test Speaker",
                "description": "A test speaker for unit tests"
            }
        elif data_type == "presentation":
            return {
                "id": generate_presentation_id("Test Presentation"),
                "title": "Test Presentation",
                "sections": ["Introduction", "Body", "Conclusion"]
            }
        return {}

    def assert_normalized_text(self, input_text: str, expected: str):
        """Assert text normalization produces expected result"""
        result = self.normalizer.normalize_text(input_text)
        assert result == expected, f"Expected '{expected}', got '{result}'"

# Usage in tests
def test_data_handler():
    test_utils = TestUtilities()
    temp_dir = test_utils.setup_temp_directory()

    try:
        # Test file operations
        test_data = test_utils.create_test_data("speaker")
        file_path = temp_dir / "test.json"

        save_data_to_file(test_data, file_path)
        loaded_data = load_data_from_file(file_path)

        assert loaded_data == test_data
    finally:
        test_utils.cleanup_temp_directory()
```

Yardımcı araçlar modülü, moves uygulamasının diğer tüm bileşenlerini destekleyen temel katmanı sağlar. Bu yardımcı araçlar, güvenilir, verimli ve kolay test edilebilir olacak şekilde tasarlanmıştır; böylece sistem genelinde tutarlı davranış sağlanır.
