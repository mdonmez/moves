"""Common test fixtures and utilities."""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_data_folder(temp_dir):
    """Mock the DATA_FOLDER to use a temporary directory."""
    with patch("utils.data_handler.DATA_FOLDER", temp_dir):
        yield temp_dir


@pytest.fixture
def sample_text():
    """Sample text for testing text processing functions."""
    return "Hello, World! This is a test with numbers 123 and special chars: @#$%"


@pytest.fixture
def sample_speaker_data():
    """Sample speaker data for testing."""
    return {
        "name": "John Doe",
        "speaker_id": "john-doe-abc12",
        "source_presentation": "/path/to/presentation.pdf",
        "source_transcript": "/path/to/transcript.pdf"
    }


@pytest.fixture
def sample_pdf_content():
    """Sample PDF text content for testing."""
    return """Slide 1: Introduction
Welcome to our presentation about AI and machine learning.

Slide 2: Overview
Today we will cover the basics of neural networks.

Slide 3: Deep Learning
Deep learning is a subset of machine learning."""