# Development Guide

## Overview

This guide provides comprehensive information for developers who want to contribute to, extend, or understand the internals of the Moves project. It covers development setup, architecture patterns, testing strategies, and contribution guidelines.

## Development Environment Setup

### Prerequisites

- **Python 3.13+**: Required for modern type hints and language features
- **Git**: For version control and collaboration
- **Code Editor**: VS Code, PyCharm, or similar with Python support
- **Virtual Environment**: Isolated Python environment for development

### Initial Setup

#### 1. Fork and Clone Repository
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/moves.git
cd moves

# Add upstream remote
git remote add upstream https://github.com/mdonmez/moves.git
```

#### 2. Create Development Environment
```bash
# Create virtual environment
python -m venv moves-dev
source moves-dev/bin/activate  # Linux/macOS
# or
moves-dev\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Dependencies
```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e .  # Editable installation
pip install pytest black isort mypy flake8 pre-commit
```

#### 4. Configure Development Tools

**Pre-commit hooks:**
```bash
# Setup pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

**VS Code configuration (.vscode/settings.json):**
```json
{
    "python.defaultInterpreterPath": "./moves-dev/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true
}
```

## Code Architecture and Patterns

### Project Structure

```
moves/
├── app.py                         # CLI entry point
├── src/                          # Source code
│   ├── core/                     # Core business logic
│   │   ├── components/           # Modular components
│   │   │   ├── chunk_producer.py
│   │   │   ├── section_producer.py
│   │   │   ├── similarity_calculator.py
│   │   │   └── similarity_units/
│   │   │       ├── semantic.py
│   │   │       └── phonetic.py
│   │   ├── presentation_controller.py
│   │   ├── speaker_manager.py
│   │   └── settings_editor.py
│   ├── data/                     # Data models and schemas
│   │   ├── models.py
│   │   ├── llm_instruction.md
│   │   └── settings_template.yaml
│   └── utils/                    # Utility functions
│       ├── data_handler.py
│       ├── id_generator.py
│       ├── logger.py
│       └── text_normalizer.py
├── docs/                         # Documentation
├── tests/                        # Test suite (to be created)
├── pyproject.toml               # Project configuration
└── requirements.txt             # Dependencies
```

### Design Patterns

#### 1. Component-Based Architecture
Each major feature is implemented as a self-contained component with clear interfaces:

```python
# Example component structure
class SimilarityCalculator:
    """
    Component responsible for content similarity calculation
    - Single responsibility
    - Clear input/output interfaces
    - Minimal external dependencies
    """
    
    def __init__(self, semantic_weight: float, phonetic_weight: float):
        self.semantic = Semantic()      # Composition over inheritance
        self.phonetic = Phonetic()
        
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        # Well-defined public interface
        pass
```

#### 2. Dependency Injection
Components receive dependencies through constructor injection:

```python
class PresentationController:
    def __init__(self, sections: list[Section], start_section: Section, 
                 window_size: int = 12):
        # Dependencies injected from outside
        self.similarity_calculator = SimilarityCalculator()
        self.chunks = chunk_producer.generate_chunks(sections, window_size)
```

#### 3. Factory Pattern
Factory functions create configured instances:

```python
def presentation_controller_instance(sections: list[Section], 
                                   start_section: Section) -> PresentationController:
    return PresentationController(
        sections=sections,
        start_section=start_section,
        window_size=12,  # Configuration handled in factory
    )
```

#### 4. Strategy Pattern
Multiple similarity engines implement common interface:

```python
# Common interface
class SimilarityEngine:
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        raise NotImplementedError

# Concrete implementations
class Semantic(SimilarityEngine):
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        # Semantic similarity implementation
        pass

class Phonetic(SimilarityEngine):
    def compare(self, input_str: str, candidates: list[Chunk]) -> list[SimilarityResult]:
        # Phonetic similarity implementation
        pass
```

### Coding Standards

#### Code Style
- **Formatter**: Black with default settings
- **Import Sorting**: isort with profile="black"
- **Line Length**: 88 characters (Black default)
- **Docstrings**: Google style

#### Type Hints
```python
from typing import Optional, Union, List, Dict, Any
from pathlib import Path

def process_files(
    presentation_path: Path, 
    transcript_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> List[Section]:
    """
    Process presentation files and return sections.
    
    Args:
        presentation_path: Path to presentation PDF
        transcript_path: Path to transcript PDF  
        options: Optional processing configuration
        
    Returns:
        List of generated Section objects
        
    Raises:
        FileNotFoundError: If input files don't exist
        RuntimeError: If processing fails
    """
    pass
```

#### Error Handling
```python
# Specific exceptions with context
def load_speaker(speaker_id: str) -> Speaker:
    try:
        speaker_path = SPEAKERS_PATH / speaker_id / "speaker.json"
        data = json.loads(speaker_path.read_text())
        return Speaker(**data)
    except FileNotFoundError:
        raise ValueError(f"Speaker '{speaker_id}' not found")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid speaker data for '{speaker_id}': {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load speaker '{speaker_id}': {e}")
```

## Testing Strategy

### Test Structure

```
tests/
├── unit/                         # Unit tests
│   ├── test_similarity_calculator.py
│   ├── test_chunk_producer.py
│   └── test_text_normalizer.py
├── integration/                  # Integration tests
│   ├── test_speaker_processing.py
│   └── test_presentation_control.py
├── e2e/                         # End-to-end tests
│   └── test_full_workflow.py
├── fixtures/                    # Test data
│   ├── sample_presentation.pdf
│   ├── sample_transcript.pdf
│   └── expected_sections.json
└── conftest.py                  # Pytest configuration
```

### Unit Testing

#### Test Framework: pytest
```python
import pytest
from unittest.mock import Mock, patch
from src.core.components.similarity_calculator import SimilarityCalculator

class TestSimilarityCalculator:
    @pytest.fixture
    def calculator(self):
        return SimilarityCalculator(semantic_weight=0.4, phonetic_weight=0.6)
    
    @pytest.fixture
    def sample_chunks(self):
        return [
            Chunk(partial_content="machine learning algorithms", source_sections=[]),
            Chunk(partial_content="data processing methods", source_sections=[])
        ]
    
    def test_compare_returns_sorted_results(self, calculator, sample_chunks):
        results = calculator.compare("machine learning", sample_chunks)
        
        assert len(results) == len(sample_chunks)
        assert all(isinstance(r, SimilarityResult) for r in results)
        # Results should be sorted by score (descending)
        assert results[0].score >= results[1].score
    
    def test_compare_empty_candidates(self, calculator):
        results = calculator.compare("test input", [])
        assert results == []
    
    @patch('src.core.components.similarity_calculator.Semantic')
    @patch('src.core.components.similarity_calculator.Phonetic')
    def test_compare_with_mocked_engines(self, mock_phonetic, mock_semantic, calculator):
        # Mock engine responses
        mock_semantic.return_value.compare.return_value = [
            SimilarityResult(chunk=Mock(), score=0.8)
        ]
        mock_phonetic.return_value.compare.return_value = [
            SimilarityResult(chunk=Mock(), score=0.9)
        ]
        
        results = calculator.compare("test", [Mock()])
        
        # Verify engines were called
        mock_semantic.return_value.compare.assert_called_once()
        mock_phonetic.return_value.compare.assert_called_once()
```

#### Testing Utilities
```python
# tests/utils.py
import tempfile
from pathlib import Path
from src.data.models import Section, Speaker

def create_test_speaker(name: str = "Test Speaker") -> Speaker:
    """Create a test speaker with temporary files"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pres:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as trans:
            return Speaker(
                name=name,
                speaker_id=f"test_{name.lower().replace(' ', '_')}",
                source_presentation=Path(pres.name),
                source_transcript=Path(trans.name)
            )

def create_test_sections(count: int = 3) -> list[Section]:
    """Create test sections for testing"""
    return [
        Section(
            content=f"Test section content {i}",
            section_index=i
        )
        for i in range(count)
    ]
```

### Integration Testing

```python
# tests/integration/test_speaker_processing.py
import pytest
from unittest.mock import patch
from src.core.speaker_manager import SpeakerManager

class TestSpeakerProcessing:
    @pytest.fixture
    def speaker_manager(self):
        return SpeakerManager()
    
    @patch('src.core.components.section_producer.generate_sections')
    def test_process_single_speaker(self, mock_generate, speaker_manager):
        # Mock section generation
        mock_generate.return_value = create_test_sections(5)
        
        speaker = create_test_speaker("Integration Test")
        results = speaker_manager.process([speaker], "test/model", "test-key")
        
        assert len(results) == 1
        assert results[0].section_count == 5
        mock_generate.assert_called_once()
```

### Mocking External Dependencies

#### LLM API Calls
```python
@pytest.fixture
def mock_llm_response():
    return {
        "sections": [
            {"section_index": 0, "content": "Mocked section 1"},
            {"section_index": 1, "content": "Mocked section 2"}
        ]
    }

@patch('src.core.components.section_producer._call_llm')
def test_section_generation(mock_call_llm, mock_llm_response):
    mock_call_llm.return_value = [s["content"] for s in mock_llm_response["sections"]]
    
    sections = generate_sections(
        Path("test_presentation.pdf"),
        Path("test_transcript.pdf"),
        "test/model",
        "test-key"
    )
    
    assert len(sections) == 2
    assert sections[0].content == "Mocked section 1"
```

#### Audio System
```python
@pytest.fixture
def mock_audio_system():
    with patch('sounddevice.InputStream'), \
         patch('sounddevice.default.device', [0, 1]):
        yield

def test_presentation_control_with_mocked_audio(mock_audio_system):
    controller = PresentationController(sections, start_section)
    # Test without requiring actual audio hardware
```

### Continuous Integration

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black isort mypy
    
    - name: Lint with black
      run: black --check src/ tests/
    
    - name: Sort imports
      run: isort --check-only src/ tests/
    
    - name: Type check
      run: mypy src/
    
    - name: Run tests
      run: pytest tests/ --cov=src/ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Performance Optimization

### Profiling and Benchmarking

#### Performance Testing
```python
import time
import cProfile
from src.core.components.similarity_calculator import SimilarityCalculator

def benchmark_similarity_calculation():
    """Benchmark similarity calculation performance"""
    calculator = SimilarityCalculator()
    
    # Setup test data
    input_text = "machine learning algorithms for data processing"
    candidates = create_large_chunk_list(1000)  # 1000 test chunks
    
    # Warm up
    calculator.compare(input_text, candidates[:10])
    
    # Benchmark
    start_time = time.time()
    results = calculator.compare(input_text, candidates)
    end_time = time.time()
    
    print(f"Processed {len(candidates)} candidates in {end_time - start_time:.3f}s")
    print(f"Average: {(end_time - start_time) * 1000 / len(candidates):.2f}ms per candidate")

def profile_similarity_calculation():
    """Profile similarity calculation to find bottlenecks"""
    pr = cProfile.Profile()
    pr.enable()
    
    benchmark_similarity_calculation()
    
    pr.disable()
    pr.dump_stats('similarity_profile.prof')
    
    # Analyze with: python -m pstats similarity_profile.prof
```

#### Memory Profiling
```python
import tracemalloc
from src.core.presentation_controller import PresentationController

def profile_memory_usage():
    """Profile memory usage during presentation control"""
    tracemalloc.start()
    
    controller = PresentationController(sections, start_section)
    
    # Simulate usage
    for _ in range(100):
        controller.recent_words.append("test")
        controller.navigate_presentation()
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current: {current / 1024 / 1024:.2f} MB")
    print(f"Peak: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
```

### Optimization Strategies

#### Caching
```python
from functools import lru_cache
from typing import Dict, Any

class OptimizedSimilarityCalculator:
    def __init__(self):
        self._embedding_cache: Dict[str, Any] = {}
    
    @lru_cache(maxsize=512)  # Cache phonetic codes
    def _get_phonetic_code(self, text: str) -> str:
        return metaphone(text)
    
    def _get_cached_embedding(self, text: str):
        """Cache embeddings to avoid recomputation"""
        if text not in self._embedding_cache:
            self._embedding_cache[text] = self.model.encode(text)
        return self._embedding_cache[text]
```

#### Batch Processing
```python
async def process_speakers_batch(speakers: list[Speaker], 
                               batch_size: int = 3) -> list[ProcessResult]:
    """Process speakers in batches to avoid rate limits"""
    results = []
    
    for i in range(0, len(speakers), batch_size):
        batch = speakers[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process_single_speaker(speaker) for speaker in batch]
        )
        results.extend(batch_results)
        
        # Rate limiting delay between batches
        if i + batch_size < len(speakers):
            await asyncio.sleep(2.0)
    
    return results
```

## Extension Points

### Adding New Similarity Engines

#### 1. Implement SimilarityEngine Interface
```python
# src/core/components/similarity_units/custom_engine.py
from typing import List
from ...data.models import Chunk, SimilarityResult

class CustomSimilarityEngine:
    """Custom similarity engine implementation"""
    
    def __init__(self, config: dict):
        self.config = config
        # Initialize custom algorithm
    
    def compare(self, input_str: str, candidates: List[Chunk]) -> List[SimilarityResult]:
        """
        Implement custom similarity calculation
        
        Args:
            input_str: Input text to match
            candidates: Candidate chunks to compare
            
        Returns:
            List of similarity results sorted by score
        """
        results = []
        
        for candidate in candidates:
            # Implement your similarity algorithm here
            score = self._calculate_similarity(input_str, candidate.partial_content)
            results.append(SimilarityResult(chunk=candidate, score=score))
        
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Custom similarity calculation logic"""
        # Your algorithm here
        pass
```

#### 2. Integrate with SimilarityCalculator
```python
# Modify similarity_calculator.py to support new engine
class ExtendedSimilarityCalculator:
    def __init__(self, semantic_weight: float = 0.3, 
                 phonetic_weight: float = 0.4, 
                 custom_weight: float = 0.3):
        self.semantic = Semantic()
        self.phonetic = Phonetic()
        self.custom = CustomSimilarityEngine(config={})
        
        self.weights = {
            'semantic': semantic_weight,
            'phonetic': phonetic_weight,
            'custom': custom_weight
        }
    
    def compare(self, input_str: str, candidates: List[Chunk]) -> List[SimilarityResult]:
        # Get results from all engines
        semantic_results = self.semantic.compare(input_str, candidates)
        phonetic_results = self.phonetic.compare(input_str, candidates)
        custom_results = self.custom.compare(input_str, candidates)
        
        # Combine with weighted scoring
        return self._combine_results(semantic_results, phonetic_results, custom_results)
```

### Adding New LLM Providers

#### 1. Extend LiteLLM Configuration
```python
# src/core/components/llm_providers/custom_provider.py
def configure_custom_provider(api_key: str, model_name: str) -> dict:
    """Configure custom LLM provider"""
    return {
        'model': f'custom/{model_name}',
        'api_key': api_key,
        'base_url': 'https://api.custom-provider.com/v1',
        'headers': {
            'Authorization': f'Bearer {api_key}',
            'Custom-Header': 'value'
        }
    }

# Integrate with section_producer.py
def _call_llm_with_custom_provider(presentation_data: str, transcript_data: str,
                                 llm_model: str, llm_api_key: str) -> list[str]:
    if llm_model.startswith('custom/'):
        config = configure_custom_provider(llm_api_key, llm_model.split('/')[1])
        # Use custom configuration
    
    # Proceed with standard liteLLM call
```

### Plugin Architecture (Future Enhancement)

#### Plugin Interface
```python
# src/core/plugins/base.py
from abc import ABC, abstractmethod

class MovePlugin(ABC):
    """Base class for Moves plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @abstractmethod
    def initialize(self, config: dict) -> None:
        """Initialize plugin with configuration"""
        pass
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Main plugin processing method"""
        pass

# Example plugin implementation
class CustomProcessingPlugin(MovePlugin):
    @property
    def name(self) -> str:
        return "custom-processing"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: dict) -> None:
        self.config = config
    
    def process(self, sections: list[Section]) -> list[Section]:
        # Custom section processing logic
        return modified_sections
```

## Contributing Guidelines

### Contribution Workflow

#### 1. Planning and Discussion
- **Create an issue** for new features or bugs
- **Discuss approach** before implementing large changes
- **Review existing code** to understand patterns

#### 2. Development Process
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes with frequent commits
git add .
git commit -m "feat: add new similarity engine"

# Keep branch up to date
git fetch upstream
git rebase upstream/master

# Push and create PR
git push origin feature/your-feature-name
```

#### 3. Code Review Process
- **Self-review** code before submitting
- **Add tests** for new functionality
- **Update documentation** as needed
- **Respond to feedback** promptly

#### 4. Commit Message Convention
```bash
# Format: type(scope): description
feat(similarity): add custom similarity engine
fix(audio): resolve microphone detection issue
docs(api): update similarity calculator documentation
test(integration): add speaker processing tests
refactor(core): simplify section producer interface
```

### Pull Request Guidelines

#### PR Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changes tested locally

## Related Issues
Fixes #(issue number)
```

#### Review Criteria
- **Functionality**: Code works as intended
- **Testing**: Adequate test coverage
- **Documentation**: Updated and clear
- **Performance**: No significant performance regression
- **Security**: No security vulnerabilities introduced

## Release Process

### Versioning Strategy
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Checklist
```bash
# 1. Update version numbers
# 2. Update CHANGELOG.md
# 3. Run full test suite
pytest tests/

# 4. Create release branch
git checkout -b release/v1.2.0

# 5. Tag release
git tag -a v1.2.0 -m "Release version 1.2.0"

# 6. Push tag
git push origin v1.2.0

# 7. Create GitHub release with notes
# 8. Update documentation
```

This development guide provides the foundation for contributing to and extending the Moves project. It emphasizes code quality, testing, and maintainable architecture to ensure the project's long-term success.