"""Tests for utils.id_generator module."""
import pytest
import re
from datetime import datetime
from unittest.mock import patch

from utils import id_generator


def test_generate_speaker_id_creates_valid_format():
    """Test generate_speaker_id creates IDs with correct format."""
    name = "John Doe"
    speaker_id = id_generator.generate_speaker_id(name)
    
    # Should be in format: slug-XXXXX where XXXXX is 5 random chars
    pattern = r"^[a-z0-9-]+-[0-9A-Za-z]{5}$"
    assert re.match(pattern, speaker_id)
    assert speaker_id.startswith("john-doe-")


def test_generate_speaker_id_handles_special_characters():
    """Test generate_speaker_id handles special characters properly."""
    name = "Jean-François Müller"
    speaker_id = id_generator.generate_speaker_id(name)
    
    # Should normalize unicode and remove special chars
    assert speaker_id.startswith("jean-francois-muller-")
    assert re.match(r"^[a-z0-9-]+-[0-9A-Za-z]{5}$", speaker_id)


def test_generate_speaker_id_handles_numbers_and_spaces():
    """Test generate_speaker_id handles numbers and multiple spaces."""
    name = "Speaker  123   Test"
    speaker_id = id_generator.generate_speaker_id(name)
    
    assert speaker_id.startswith("speaker-123-test-")
    assert re.match(r"^[a-z0-9-]+-[0-9A-Za-z]{5}$", speaker_id)


def test_generate_speaker_id_removes_leading_trailing_dashes():
    """Test generate_speaker_id removes leading/trailing dashes from slug."""
    name = "---Test Name---"
    speaker_id = id_generator.generate_speaker_id(name)
    
    assert speaker_id.startswith("test-name-")
    assert not speaker_id.startswith("---")
    assert not speaker_id.endswith("---")


def test_generate_speaker_id_handles_empty_slug():
    """Test generate_speaker_id handles names that result in empty slugs."""
    name = "!!!"  # Only special characters
    speaker_id = id_generator.generate_speaker_id(name)
    
    # Should still generate a valid ID with random suffix
    pattern = r"^-[0-9A-Za-z]{5}$"  # May start with dash if slug is empty
    assert re.match(pattern, speaker_id) or re.match(r"^[0-9A-Za-z]{5}$", speaker_id)


def test_generate_speaker_id_uniqueness():
    """Test generate_speaker_id generates unique IDs for same name."""
    name = "Test User"
    
    ids = [id_generator.generate_speaker_id(name) for _ in range(10)]
    
    # All IDs should be unique due to random suffix
    assert len(set(ids)) == 10
    # All should start with same slug
    for speaker_id in ids:
        assert speaker_id.startswith("test-user-")


@pytest.mark.parametrize("name,expected_slug", [
    ("Simple Name", "simple-name"),
    ("CamelCase", "camelcase"),
    ("UPPERCASE", "uppercase"),
    ("With-Dashes", "with-dashes"),
    ("Numbers123", "numbers123"),
    ("Café", "cafe"),
    ("naïve", "naive"),
    ("résumé", "resume"),
])
def test_generate_speaker_id_slug_generation(name, expected_slug):
    """Test generate_speaker_id creates correct slugs for various inputs."""
    speaker_id = id_generator.generate_speaker_id(name)
    assert speaker_id.startswith(f"{expected_slug}-")


def test_generate_speaker_id_uses_correct_alphabet():
    """Test generate_speaker_id uses the expected alphabet for random suffix."""
    name = "Test"
    expected_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    
    # Generate multiple IDs to test alphabet usage
    for _ in range(20):
        speaker_id = id_generator.generate_speaker_id(name)
        suffix = speaker_id.split("-")[-1]
        
        assert len(suffix) == 5
        for char in suffix:
            assert char in expected_alphabet


def test_generate_history_id_format():
    """Test generate_history_id creates IDs with correct format."""
    history_id = id_generator.generate_history_id()
    
    # Should be in format: YYYYMMDD_HH-MM-SS
    pattern = r"^\d{8}_\d{2}-\d{2}-\d{2}$"
    assert re.match(pattern, history_id)


def test_generate_history_id_uses_current_datetime():
    """Test generate_history_id uses current datetime."""
    mock_datetime = datetime(2023, 12, 25, 14, 30, 45)
    
    with patch("utils.id_generator.datetime") as mock_dt:
        mock_dt.now.return_value = mock_datetime
        
        history_id = id_generator.generate_history_id()
        assert history_id == "20231225_14-30-45"


def test_generate_history_id_uniqueness_over_time():
    """Test generate_history_id generates different IDs at different times."""
    # This test relies on the fact that datetime changes between calls
    id1 = id_generator.generate_history_id()
    
    # Mock a slightly different time
    with patch("utils.id_generator.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2023, 12, 25, 14, 30, 46)
        id2 = id_generator.generate_history_id()
    
    assert id1 != id2


def test_generate_speaker_id_with_mocked_secrets():
    """Test generate_speaker_id with mocked random generation for determinism."""
    name = "Test User"
    
    with patch("utils.id_generator.secrets.choice", side_effect=["A", "B", "C", "D", "E"]):
        speaker_id = id_generator.generate_speaker_id(name)
        assert speaker_id == "test-user-ABCDE"


def test_speaker_id_type_annotation():
    """Test that generate_speaker_id returns the correct type."""
    from data.models import SpeakerId
    
    result = id_generator.generate_speaker_id("Test")
    assert isinstance(result, str)  # SpeakerId is just a str alias


def test_history_id_type_annotation():
    """Test that generate_history_id returns the correct type."""
    from data.models import HistoryId
    
    result = id_generator.generate_history_id()
    assert isinstance(result, str)  # HistoryId is just a str alias