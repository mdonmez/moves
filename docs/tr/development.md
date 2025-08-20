# Development Guide

Bu kılavuz, moves uygulamasına katkıda bulunmak, genişletmek veya özelleştirmek isteyen geliştiriciler için kapsamlı bilgiler sağlar. Kurulum prosedürlerini, geliştirme iş akışlarını, test stratejilerini ve en iyi uygulamaları kapsar.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Contributing Guidelines](#contributing-guidelines)
- [Extension Development](#extension-development)
- [Performance Optimization](#performance-optimization)
- [Debugging](#debugging)
- [Release Process](#release-process)

## Development Environment Setup

### Prerequisites

```bash
# Required software
- Python 3.13+
- Git
- A code editor (VS Code recommended)
- Audio drivers and microphone access

# Optional but recommended
- UV package manager (faster than pip)
- Docker (for containerized testing)
- Pre-commit hooks
```

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd moves

# Create virtual environment (using UV)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync

# Install development dependencies
uv add --dev pytest pytest-asyncio black isort mypy pre-commit

# Install pre-commit hooks
pre-commit install

# Verify installation
python -m pytest tests/
python app.py --help
```

### Environment Configuration

```bash
# Create development settings file
cp src/data/settings_template.yaml ~/.moves/settings.yaml

# Set required environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"  # Optional
export ANTHROPIC_API_KEY="your-anthropic-api-key"  # Optional

# Verify configuration
python -c "from src.core.settings_editor import SettingsEditor; s=SettingsEditor(); print(s.list_settings())"
```

### IDE Configuration

#### VS Code Setup

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.linting.pylintEnabled": false,
  "python.sortImports.path": "isort",
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

#### Recommended Extensions

- Python
- Pylance
- Python Docstring Generator
- GitLens
- Better Comments

## Project Structure

### Directory Organization

```
moves/
├── app.py                          # Main CLI application
├── pyproject.toml                  # Project configuration
├── README.md                       # Project overview
├── uv.lock                        # Dependency lock file
│
├── src/                           # Source code
│   ├── core/                      # Core application logic
│   │   ├── presentation_controller.py
│   │   ├── speaker_manager.py
│   │   ├── settings_editor.py
│   │   └── components/            # Processing components
│   │       ├── chunk_producer.py
│   │       ├── section_producer.py
│   │       ├── similarity_calculator.py
│   │       ├── ml_models/         # ML model files
│   │       └── similarity_units/  # Similarity algorithms
│   │
│   ├── data/                      # Data models and templates
│   │   ├── models.py
│   │   ├── settings_template.yaml
│   │   └── llm_instruction.md
│   │
│   └── utils/                     # Utility modules
│       ├── data_handler.py
│       ├── logger.py
│       ├── text_normalizer.py
│       └── id_generator.py
│
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── fixtures/                 # Test fixtures
│   └── conftest.py              # Pytest configuration
│
├── docs/                         # Documentation
├── scripts/                      # Development scripts
└── .github/                      # GitHub workflows
```

### Code Organization Principles

#### Module Dependencies

```
┌─────────────────────────────────────────────────────────┐
│                    app.py (CLI)                         │
├─────────────────────────────────────────────────────────┤
│                 Core Modules                            │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │Presentation │ │   Speaker    │ │    Settings      │  │
│  │ Controller  │ │   Manager    │ │     Editor       │  │
│  └─────────────┘ └──────────────┘ └──────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                  Components                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │   Chunk     │ │   Section    │ │   Similarity     │  │
│  │  Producer   │ │   Producer   │ │   Calculator     │  │
│  └─────────────┘ └──────────────┘ └──────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    Utilities                            │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │    Data     │ │    Logger    │ │      Text        │  │
│  │   Handler   │ │              │ │   Normalizer     │  │
│  └─────────────┘ └──────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Dependency Rules**:

1. CLI sadece Core modüllerine bağımlıdır
2. Core modülleri Components ve Utilities’e bağımlı olabilir
3. Components yalnızca Utilities’e bağımlı olabilir
4. Utilities’in iç bağımlılıkları yoktur
5. Dairesel bağımlılık yoktur

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/voice-navigation-improvements

# 2. Make changes following code style
# Edit relevant files...

# 3. Add tests for new functionality
# Create test files in tests/

# 4. Run quality checks
python -m black src/ tests/
python -m isort src/ tests/
python -m mypy src/
python -m pytest tests/

# 5. Commit with descriptive message
git add .
git commit -m "feat: improve voice navigation accuracy with hybrid similarity"

# 6. Push and create pull request
git push origin feature/voice-navigation-improvements
```

### Commit Message Convention

```bash
# Format: <type>(<scope>): <description>
#
# Types:
# feat: New feature
# fix: Bug fix
# docs: Documentation changes
# style: Code style changes (formatting, etc.)
# refactor: Code refactoring
# test: Adding or updating tests
# chore: Maintenance tasks

# Examples:
git commit -m "feat(similarity): add phonetic similarity calculation"
git commit -m "fix(audio): resolve microphone initialization race condition"
git commit -m "docs(api): update similarity calculator documentation"
git commit -m "test(core): add unit tests for speaker manager"
```

### Code Review Process

1. **Self-Review**: Gönderimden önce değişikliklerinizi gözden geçirin
2. **Automated Checks**: Tüm CI kontrollerinin geçtiğinden emin olun
3. **Peer Review**: En az bir ekip üyesi değişiklikleri incelesin
4. **Documentation**: İlgili dokümantasyonu güncelleyin
5. **Testing**: İşlevlerin beklendiği gibi çalıştığını doğrulayın

## Testing

### Test Structure

```
tests/
├── unit/                          # Unit tests (isolated components)
│   ├── test_presentation_controller.py
│   ├── test_speaker_manager.py
│   ├── test_similarity_calculator.py
│   └── utils/
│       ├── test_text_normalizer.py
│       └── test_data_handler.py
│
├── integration/                   # Integration tests (component interaction)
│   ├── test_voice_navigation.py
│   ├── test_pdf_processing.py
│   └── test_settings_management.py
│
├── fixtures/                      # Test data and fixtures
│   ├── sample_presentation.pdf
│   ├── test_audio.wav
│   └── mock_settings.yaml
│
└── conftest.py                   # Pytest configuration and fixtures
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit/          # Unit tests only
python -m pytest tests/integration/   # Integration tests only

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_similarity_calculator.py

# Run with verbose output
python -m pytest -v

# Run tests matching pattern
python -m pytest -k "similarity"
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/test_similarity_calculator.py
import pytest
from src.core.components.similarity_calculator import SimilarityCalculator
from src.data.models import Chunk

class TestSimilarityCalculator:

    @pytest.fixture
    def calculator(self):
        """Create similarity calculator instance."""
        return SimilarityCalculator(semantic_weight=0.7, phonetic_weight=0.3)

    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing."""
        return [
            Chunk("chunk_1", 0, "introduction to artificial intelligence", 0, 50),
            Chunk("chunk_2", 0, "machine learning fundamentals", 51, 100),
            Chunk("chunk_3", 1, "neural network architecture", 0, 45)
        ]

    def test_calculate_similarity_basic(self, calculator, sample_chunks):
        """Test basic similarity calculation."""
        results = calculator.calculate_similarity("AI introduction", sample_chunks)

        assert len(results) > 0
        assert all(0 <= result.similarity_score <= 1 for result in results)
        assert results[0].similarity_score >= results[-1].similarity_score  # Sorted

    def test_calculate_similarity_empty_input(self, calculator, sample_chunks):
        """Test similarity calculation with empty input."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            calculator.calculate_similarity("", sample_chunks)

    @pytest.mark.asyncio
    async def test_async_similarity_calculation(self, calculator, sample_chunks):
        """Test asynchronous similarity calculation."""
        # Example of testing async functionality
        pass

    @pytest.mark.parametrize("semantic_weight,phonetic_weight", [
        (0.8, 0.2),
        (0.5, 0.5),
        (0.3, 0.7)
    ])
    def test_weight_combinations(self, semantic_weight, phonetic_weight, sample_chunks):
        """Test different weight combinations."""
        calculator = SimilarityCalculator(semantic_weight, phonetic_weight)
        results = calculator.calculate_similarity("test input", sample_chunks)
        assert len(results) > 0
```

#### Integration Test Example

```python
# tests/integration/test_voice_navigation.py
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from src.core.presentation_controller import PresentationController

class TestVoiceNavigation:

    @pytest.fixture
    def presentation_sections(self):
        """Sample presentation sections."""
        return [
            "Introduction to the topic and overview",
            "First main point with detailed explanation",
            "Second main point with examples",
            "Conclusion and summary"
        ]

    @pytest.fixture
    def controller(self, presentation_sections):
        """Create presentation controller."""
        return PresentationController(presentation_sections, start_section=0)

    @patch('src.core.presentation_controller.OnlineRecognizer')
    def test_voice_navigation_workflow(self, mock_recognizer, controller):
        """Test complete voice navigation workflow."""
        # Mock speech recognition
        mock_stream = Mock()
        mock_recognizer.return_value.create_stream.return_value = mock_stream
        mock_recognizer.return_value.get_result.return_value = "first main point"

        # Test navigation
        controller.start_listening()
        # Simulate voice recognition triggering navigation
        # Assert section changed correctly
        controller.stop_listening()

    def test_section_navigation_accuracy(self, controller):
        """Test navigation accuracy with various inputs."""
        test_cases = [
            ("introduction", 0),
            ("first main", 1),
            ("second point", 2),
            ("conclusion", 3)
        ]

        for input_text, expected_section in test_cases:
            # Test direct navigation
            success = controller.navigate_to_section(expected_section)
            assert success
            assert controller.get_current_section() == expected_section
```

### Test Fixtures and Utilities

```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path
from src.utils.data_handler import get_user_moves_dir

@pytest.fixture
def temp_data_dir(monkeypatch):
    """Create temporary data directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())

    # Mock the user data directory
    monkeypatch.setattr('src.utils.data_handler.get_user_moves_dir', lambda: temp_dir)

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_pdf_file():
    """Create sample PDF file for testing."""
    # Create minimal PDF for testing
    pdf_path = Path("tests/fixtures/sample.pdf")
    if not pdf_path.exists():
        # Create minimal PDF or use existing test file
        pass
    return pdf_path

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response."""
    return {
        "sections": [
            {"section_index": 0, "content": "Introduction section content"},
            {"section_index": 1, "content": "Main content section"},
            {"section_index": 2, "content": "Conclusion section content"}
        ]
    }
```

### Performance Testing

```python
# tests/performance/test_similarity_performance.py
import time
import pytest
from src.core.components.similarity_calculator import SimilarityCalculator

class TestSimilarityPerformance:

    @pytest.fixture
    def large_chunk_set(self):
        """Create large set of chunks for performance testing."""
        return [
            Chunk(f"chunk_{i}", i % 10, f"content for chunk {i}", 0, 100)
            for i in range(1000)
        ]

    def test_similarity_calculation_performance(self, large_chunk_set):
        """Test similarity calculation performance with large dataset."""
        calculator = SimilarityCalculator()

        start_time = time.time()
        results = calculator.calculate_similarity("test input", large_chunk_set)
        end_time = time.time()

        calculation_time = end_time - start_time

        # Assert reasonable performance (adjust threshold as needed)
        assert calculation_time < 2.0  # Should complete within 2 seconds
        assert len(results) > 0

    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        # Test multiple inputs processed together
        pass
```

## Code Quality

### Code Style Standards

The project follows these code style standards:

#### Python Style Guide

- **PEP 8** compliance with 88-character line length
- **Black** for automatic code formatting
- **isort** for import sorting
- **Type hints** for all public functions
- **Google-style docstrings** for documentation

#### Formatting Configuration

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py313']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

### Static Analysis

```bash
# Type checking
python -m mypy src/

# Code formatting
python -m black src/ tests/

# Import sorting
python -m isort src/ tests/

# Linting (optional)
python -m flake8 src/ tests/
```

### Documentation Standards

```python
def calculate_similarity(
    self,
    input_text: str,
    chunks: list[Chunk],
    top_k: int = 5
) -> list[SimilarityResult]:
    """Calculate similarity scores for input against chunks.

    Uses hybrid approach combining semantic embeddings and phonetic
    matching to provide robust similarity scoring for voice navigation.

    Args:
        input_text: Input text to match against chunks
        chunks: List of chunks to compare with input
        top_k: Maximum number of results to return

    Returns:
        List of SimilarityResult objects ordered by descending similarity
        score. Contains at most top_k results.

    Raises:
        ValueError: If input_text is empty or chunks list is empty
        ModelError: If embedding model fails to load or process text

    Example:
        >>> calculator = SimilarityCalculator()
        >>> chunks = [Chunk("1", 0, "AI introduction", 0, 50)]
        >>> results = calculator.calculate_similarity("artificial intelligence", chunks)
        >>> print(f"Best match: {results[0].chunk.partial_content}")
        Best match: AI introduction
    """
```

## Contributing Guidelines

### Before Contributing

1. **Read Documentation**: Understand the project architecture and goals
2. **Check Issues**: Look for existing issues or feature requests
3. **Discuss First**: For major changes, open an issue to discuss approach
4. **Follow Standards**: Adhere to coding standards and commit conventions

### Pull Request Process

1. **Fork Repository**: Create your own fork
2. **Feature Branch**: Create branch from main
3. **Make Changes**: Implement your feature or fix
4. **Add Tests**: Include comprehensive tests
5. **Update Documentation**: Update relevant docs
6. **Quality Checks**: Run all quality checks
7. **Submit PR**: Create pull request with clear description

### Pull Request Template

```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No breaking changes (or marked as such)
```

### Code Review Checklist

**For Reviewers**:

- [ ] Code is readable and well-documented
- [ ] Tests are comprehensive and pass
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Error handling is appropriate
- [ ] API changes are backwards compatible

## Extension Development

### Creating Custom Similarity Units

```python
# src/core/components/similarity_units/custom_similarity.py
from typing import Protocol
from src.data.models import Chunk, SimilarityResult

class CustomSimilarity:
    """Custom similarity calculation implementation."""

    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        """Implement custom similarity logic.

        Args:
            input_str: User input text
            candidates: Chunks to compare against

        Returns:
            List of similarity results with custom scoring
        """
        results = []

        for chunk in candidates:
            # Implement your custom similarity algorithm
            score = self._calculate_custom_score(input_str, chunk.partial_content)

            result = SimilarityResult(
                chunk=chunk,
                similarity_score=score,
                similarity_type="custom",
                metadata={"algorithm": "custom_implementation"}
            )
            results.append(result)

        return sorted(results, key=lambda r: r.similarity_score, reverse=True)

    def _calculate_custom_score(self, input_text: str, chunk_text: str) -> float:
        """Calculate custom similarity score."""
        # Your custom algorithm implementation
        # Return score between 0.0 and 1.0
        pass
```

### Adding Custom Audio Processors

```python
# src/core/components/audio/custom_processor.py
from typing import Protocol
import numpy as np

class CustomAudioProcessor:
    """Custom audio processing implementation."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.is_processing = False

    def start_processing(self) -> None:
        """Start custom audio processing."""
        self.is_processing = True
        # Initialize your audio processing pipeline

    def stop_processing(self) -> None:
        """Stop audio processing."""
        self.is_processing = False
        # Cleanup resources

    def process_audio_chunk(self, audio_data: np.ndarray) -> str:
        """Process audio chunk and return recognized text.

        Args:
            audio_data: Audio data array

        Returns:
            Recognized text string
        """
        # Implement your audio processing logic
        return "recognized text"
```

### Custom Configuration Handlers

```python
# src/core/config/custom_handler.py
from src.core.settings_editor import SettingsEditor

class CustomConfigHandler:
    """Handle custom configuration requirements."""

    def __init__(self):
        self.settings_editor = SettingsEditor()

    def add_custom_settings(self):
        """Add custom settings to template."""
        custom_settings = {
            "custom_feature_enabled": {
                "type": bool,
                "default": False,
                "description": "Enable custom feature"
            },
            "custom_threshold": {
                "type": float,
                "default": 0.5,
                "description": "Custom algorithm threshold"
            }
        }

        # Extend settings template with custom settings
        # Implementation depends on your needs
```

## Performance Optimization

### Profiling

```python
# scripts/profile_similarity.py
import cProfile
import pstats
from src.core.components.similarity_calculator import SimilarityCalculator

def profile_similarity_calculation():
    """Profile similarity calculation performance."""
    # Create test data
    calculator = SimilarityCalculator()

    # Profile the calculation
    profiler = cProfile.Profile()
    profiler.enable()

    # Run your code
    # results = calculator.calculate_similarity(...)

    profiler.disable()

    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

if __name__ == "__main__":
    profile_similarity_calculation()
```

### Memory Optimization

```python
# Use memory profiling
# pip install memory-profiler

@profile
def memory_intensive_function():
    """Profile memory usage of function."""
    # Your code here
    pass

# Run with: python -m memory_profiler script.py
```

### Async Optimization

```python
# Use async/await for I/O-bound operations
import asyncio

class AsyncSpeakerManager:
    """Async version of speaker manager for better performance."""

    async def process_multiple_pdfs(self, pdf_files: list[Path]) -> list[str]:
        """Process multiple PDFs concurrently."""
        tasks = [self.process_single_pdf(pdf) for pdf in pdf_files]
        results = await asyncio.gather(*tasks)
        return results

    async def process_single_pdf(self, pdf_file: Path) -> str:
        """Process single PDF asynchronously."""
        # Async PDF processing implementation
        pass
```

## Debugging

### Logging for Development

```python
# Enable debug logging
import logging
logging.getLogger('moves').setLevel(logging.DEBUG)

# Add temporary debug logging
from src.utils.logger import logger

def debug_similarity_calculation(input_text: str, chunks: list[Chunk]):
    """Debug similarity calculation process."""
    logger.debug(f"Input text: {input_text}")
    logger.debug(f"Number of chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks[:5]):  # Log first 5 chunks
        logger.debug(f"Chunk {i}: {chunk.partial_content[:50]}...")
```

### Interactive Debugging

```python
# Use breakpoint() for debugging (Python 3.7+)
def problematic_function():
    """Function with potential issues."""
    # ... some code ...

    breakpoint()  # Execution will pause here

    # ... more code ...
```

### Testing Audio Components

```python
# scripts/test_audio.py
"""Script to test audio components in isolation."""

from src.core.presentation_controller import PresentationController

def test_audio_system():
    """Test audio system without full application."""
    # Create minimal test setup
    sections = ["Test section one", "Test section two"]
    controller = PresentationController(sections)

    print("Testing audio system...")
    print("Say something to test recognition:")

    try:
        controller.start_listening()
        input("Press Enter to stop...")
        controller.stop_listening()
    except Exception as e:
        print(f"Audio test failed: {e}")

if __name__ == "__main__":
    test_audio_system()
```

## Release Process

### Version Management

```bash
# Version numbering follows Semantic Versioning (SemVer)
# MAJOR.MINOR.PATCH
# Example: 1.2.3

# Update version in pyproject.toml
[project]
version = "1.2.3"

# Tag release
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

### Pre-Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Dependencies reviewed
- [ ] Security scan completed
- [ ] Performance benchmarks acceptable

### Release Notes Template

```markdown
# Release v1.2.3

## New Features

- Feature 1 description
- Feature 2 description

## Bug Fixes

- Fix 1 description
- Fix 2 description

## Improvements

- Improvement 1 description
- Improvement 2 description

## Breaking Changes

- Breaking change 1 (if any)

## Migration Guide

Steps to migrate from previous version (if applicable).

## Known Issues

- Issue 1 (if any)
```

Bu geliştirme kılavuzu, moves uygulamasına katkı sağlamak ve uygulamayı genişletmek için kapsamlı bir temel sunar. Bu yönergeleri izlemek, kod kalitesini, sürdürülebilirliği ve proje genelindeki tutarlılığı garanti eder.
