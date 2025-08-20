# Troubleshooting Guide

## Overview

This guide helps diagnose and resolve common issues when using the Moves voice-controlled presentation system. Issues are organized by category with step-by-step solutions and prevention strategies.

## Quick Diagnostic Checklist

Before diving into specific issues, run through this quick checklist:

### System Requirements
- [ ] Python 3.13 or higher installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Microphone connected and working
- [ ] Internet connection available
- [ ] API key configured for LLM provider

### Basic Configuration  
- [ ] Settings configured: `python app.py settings list`
- [ ] Valid API key format for chosen provider
- [ ] Audio device accessible by Python
- [ ] Data directory writable: `~/.moves/`

### Test Commands
```bash
# Test CLI functionality
python app.py --help

# Test settings
python app.py settings list

# Test audio system
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test speech recognition
python -c "import sherpa_onnx; print('Speech recognition available')"
```

## Installation Issues

### Python Version Compatibility

#### Problem: "Python 3.13+ required" error
**Symptoms:**
- Package installation failures
- Import errors for type hints
- Syntax errors in source code

**Solution:**
```bash
# Check current Python version
python --version

# Install Python 3.13 if needed
# macOS with Homebrew:
brew install python@3.13

# Ubuntu/Debian:
sudo apt update
sudo apt install python3.13 python3.13-pip

# Windows: Download from python.org
```

**Prevention:**
- Use virtual environments to isolate Python versions
- Check version before installation: `python --version`

### Dependency Installation Failures

#### Problem: Package installation errors
**Symptoms:**
```
ERROR: Could not build wheels for package_name
Microsoft Visual C++ 14.0 is required
```

**Solutions:**

**Windows:**
```bash
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or install specific packages with pre-built wheels
pip install --only-binary=all package_name
```

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Use Homebrew for system dependencies
brew install portaudio
```

**Linux:**
```bash
# Install build dependencies
sudo apt update
sudo apt install build-essential python3-dev portaudio19-dev

# For CentOS/RHEL:
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel portaudio-devel
```

### Audio System Issues

#### Problem: Audio device not found
**Symptoms:**
```
PortAudioError: No default input device available
sounddevice._exceptions.PortAudioError: Invalid device
```

**Diagnostic:**
```bash
# List available audio devices
python -c "
import sounddevice as sd
print('Available devices:')
for i, device in enumerate(sd.query_devices()):
    if device['max_input_channels'] > 0:
        print(f'{i}: {device[\"name\"]} (input)')
"
```

**Solutions:**

**Windows:**
1. Check microphone permissions in Windows Settings
2. Set default recording device in Sound Settings
3. Restart audio services: `net stop audiosrv && net start audiosrv`

**macOS:**
1. Grant microphone permissions in System Preferences > Security & Privacy
2. Check Audio MIDI Setup for device recognition
3. Restart CoreAudio: `sudo killall coreaudiod`

**Linux:**
1. Check ALSA/PulseAudio configuration
2. Add user to audio group: `sudo usermod -a -G audio $USER`
3. Restart audio systems: `pulseaudio -k && pulseaudio --start`

## Configuration Issues

### API Key Problems

#### Problem: Authentication failures
**Symptoms:**
```
RuntimeError: LLM call failed: Authentication error - invalid API key
401 Unauthorized
Invalid API key provided
```

**Solutions:**

**OpenAI Keys:**
```bash
# Check key format (should start with 'sk-')
python app.py settings list

# Verify key validity
curl -H "Authorization: Bearer sk-your-key" https://api.openai.com/v1/models
```

**Anthropic Keys:**
```bash
# Check key format (starts with different prefix)
curl -H "x-api-key: your-key" https://api.anthropic.com/v1/messages
```

**Google Keys:**
```bash
# Test Gemini API access
curl "https://generativelanguage.googleapis.com/v1/models?key=your-key"
```

**Prevention:**
- Double-check key when copying from provider dashboard
- Test keys immediately after configuration
- Use environment variables for sensitive keys

#### Problem: Model not found errors
**Symptoms:**
```
RuntimeError: LLM call failed: Model 'gpt-5' not found
Invalid model specified
```

**Solution:**
```bash
# Check valid model names for each provider
python app.py settings set model "openai/gpt-4"        # OpenAI
python app.py settings set model "anthropic/claude-3-sonnet"  # Anthropic  
python app.py settings set model "gemini/gemini-2.0-flash"    # Google
```

**Valid Model Reference:**
| Provider | Valid Models |
|----------|--------------|
| OpenAI | `gpt-4`, `gpt-3.5-turbo` |
| Anthropic | `claude-3-sonnet`, `claude-3-haiku` |
| Google | `gemini-2.0-flash`, `gemini-pro` |

### Permission and File System Issues

#### Problem: Cannot write to ~/.moves/ directory
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/home/user/.moves/settings.yaml'
RuntimeError: Failed to save settings: Permission denied
```

**Solution:**
```bash
# Check directory permissions
ls -la ~/.moves/

# Fix permissions
chmod 755 ~/.moves/
chmod 644 ~/.moves/settings.yaml

# If directory doesn't exist, create it
mkdir -p ~/.moves/
chmod 755 ~/.moves/
```

#### Problem: PDF files cannot be read
**Symptoms:**
```
FileNotFoundError: Presentation file not found: /path/to/file.pdf  
RuntimeError: PDF extraction failed: Invalid PDF format
```

**Solutions:**
```bash
# Check file existence and permissions
ls -la /path/to/file.pdf

# Verify PDF format
file /path/to/file.pdf  # Should show "PDF document"

# Test PDF accessibility
python -c "
import pymupdf
doc = pymupdf.open('/path/to/file.pdf')
print(f'Pages: {doc.page_count}')
doc.close()
"
```

## Processing Issues

### Speaker Processing Failures

#### Problem: Section generation fails
**Symptoms:**
```
RuntimeError: LLM processing failed: Request timed out
Processing error: Connection timeout
Speaker 'John Smith' could not be processed
```

**Diagnostic Steps:**

1. **Check network connectivity:**
```bash
# Test API endpoints
ping api.openai.com
ping api.anthropic.com
ping generativelanguage.googleapis.com
```

2. **Verify content size:**
```bash
# Check PDF sizes (large files may timeout)
ls -lh presentation.pdf transcript.pdf

# Large files (>50MB) may need optimization
```

3. **Test with minimal content:**
```bash
# Create simple test PDFs to isolate issue
# Single slide presentation + short transcript
```

**Solutions:**

**Timeout Issues:**
```bash
# Reduce content size or split large presentations
# Use higher timeout in code (advanced users)
# Try different LLM provider (some are faster)
```

**Content Issues:**
```bash
# Ensure PDFs contain extractable text (not just images)
# Verify transcript matches presentation language
# Check for corrupted PDF files
```

#### Problem: Empty or invalid sections generated
**Symptoms:**
```
Generated sections are empty
Section content: "Content unavailable"
Only 5 sections for 20-slide presentation
```

**Diagnostic:**
```bash
# Check generated sections file
cat ~/.moves/speakers/{speaker_id}/sections.json

# Verify original PDFs have content
python -c "
import pymupdf
with pymupdf.open('presentation.pdf') as doc:
    for i, page in enumerate(doc):
        text = page.get_text()
        print(f'Slide {i}: {len(text)} characters')
"
```

**Solutions:**
1. **Improve PDF quality:**
   - Use text-based PDFs (not scanned images)
   - Ensure clean formatting without excessive graphics
   - Remove headers/footers that add noise

2. **Optimize transcript:**
   - Write complete sentences that match slide topics
   - Include key terminology from slides
   - Maintain same language as presentation

3. **Retry processing:**
   ```bash
   # Re-process with same or different model
   python app.py speaker process "Speaker Name"
   ```

## Live Control Issues

### Voice Recognition Problems

#### Problem: Speech not recognized
**Symptoms:**
- No word buffer updates during speech
- System doesn't respond to voice input
- Console shows no recognition output

**Diagnostic:**
```bash
# Test microphone manually
python -c "
import sounddevice as sd
import numpy as np
print('Recording 3 seconds...')
recording = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
sd.wait()
print(f'Recorded {len(recording)} samples')
print(f'Max amplitude: {np.max(np.abs(recording))}')
"
```

**Solutions:**

**No Audio Input:**
1. Check microphone connection and permissions
2. Verify default input device: `python -c "import sounddevice as sd; print(sd.default.device)"`
3. Test with system audio recorder first

**Low Recognition Quality:**
1. **Improve microphone setup:**
   - Position 6-12 inches from mouth
   - Reduce background noise
   - Use directional microphone if possible

2. **Adjust speech patterns:**
   - Speak clearly at normal pace
   - Include key words from slides
   - Don't pause too long between sentences

3. **Check word buffer:**
   ```bash
   # Enable debug output (modify code)
   # Add print statements in process_audio() method
   ```

#### Problem: Navigation not working
**Symptoms:**
- Words are recognized but slides don't advance
- Similarity scores too low
- Manual navigation works but voice doesn't

**Diagnostic:**
```bash
# Check current section and chunks
# Add debug output in navigate_presentation() method
# Monitor similarity scores and thresholds
```

**Solutions:**

**Content Mismatch:**
1. **Improve transcript alignment:**
   - Speak more closely to your written transcript
   - Include exact phrases from slide content
   - Practice with key sections first

2. **Adjust similarity weights:**
   ```python
   # For technical content, increase semantic weight
   calculator = SimilarityCalculator(semantic_weight=0.6, phonetic_weight=0.4)
   
   # For noisy environments, increase phonetic weight
   calculator = SimilarityCalculator(semantic_weight=0.3, phonetic_weight=0.7)
   ```

3. **Modify window size:**
   ```python
   # Smaller window for more responsive navigation
   window_size = 8
   
   # Larger window for more context
   window_size = 16
   ```

### Performance Issues

#### Problem: High latency or lag
**Symptoms:**
- Delay between speech and navigation
- Audio processing consuming high CPU
- System becomes unresponsive

**Diagnostic:**
```bash
# Monitor system resources
top -p $(pgrep -f "python app.py")

# Check memory usage
ps -o pid,vsz,rss,comm -p $(pgrep -f "python app.py")
```

**Solutions:**

**Reduce Latency:**
1. **Optimize audio settings:**
   ```python
   # Reduce frame duration for faster processing
   self.frame_duration = 0.05  # 50ms instead of 100ms
   
   # Reduce audio queue size
   self.audio_queue = deque(maxlen=3)
   ```

2. **Model optimization:**
   ```bash
   # Use faster LLM models during processing
   python app.py settings set model "anthropic/claude-3-haiku"
   ```

**Reduce Memory Usage:**
1. **Close unnecessary applications**
2. **Reduce cache sizes:**
   ```python
   # Reduce phonetic cache size
   @lru_cache(maxsize=100)  # Instead of 350
   ```

3. **Monitor model memory:**
   ```bash
   # Check if models are loading efficiently
   # Consider using smaller embedding models
   ```

## Network and API Issues

### Connection Problems

#### Problem: Network timeouts
**Symptoms:**
```
requests.exceptions.ConnectTimeout: HTTPSConnectionPool
Connection timeout after 30 seconds
LLM request timed out
```

**Solutions:**

**Network Configuration:**
```bash
# Test direct connectivity
curl -v https://api.openai.com
telnet api.openai.com 443

# Configure proxy if needed
export HTTPS_PROXY=http://proxy:8080
export HTTP_PROXY=http://proxy:8080
```

**Firewall Issues:**
```bash
# Check if ports are blocked
# Standard HTTPS (443) should be open
# Contact IT if corporate firewall blocks API access
```

#### Problem: Rate limiting
**Symptoms:**
```
429 Too Many Requests
Rate limit exceeded
Please retry after 20 seconds
```

**Solutions:**
```bash
# Wait and retry
# For batch processing, use delays between requests
# Consider upgrading API plan for higher limits
```

### API Quota Issues

#### Problem: Quota exceeded
**Symptoms:**
```
402 Payment Required
Usage quota exceeded
Insufficient credits
```

**Solutions:**
1. **Check usage on provider dashboard**
2. **Add billing method or increase limits**
3. **Switch to cheaper model temporarily:**
   ```bash
   python app.py settings set model "gemini/gemini-2.0-flash"  # Very low cost
   ```

## Data and File Issues

### Corrupted Data

#### Problem: Invalid JSON in sections file
**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting ',' delimiter
Could not load sections data
Invalid sections file format
```

**Solution:**
```bash
# Check sections file
cat ~/.moves/speakers/{speaker_id}/sections.json

# If corrupted, re-process speaker
python app.py speaker process "Speaker Name"

# Manual fix (advanced)
# Edit JSON file to fix syntax errors
```

#### Problem: Missing speaker data
**Symptoms:**
```
FileNotFoundError: speaker.json not found
Speaker directory missing
No speakers found
```

**Solution:**
```bash
# Check data directory structure
ls -la ~/.moves/speakers/

# Re-add speaker if data lost
python app.py speaker add "Name" presentation.pdf transcript.pdf

# Restore from backup if available
cp backup/speakers/* ~/.moves/speakers/
```

## Advanced Troubleshooting

### Debug Mode

Enable detailed logging for diagnosis:

```python
# Add to presentation_controller.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints in key methods
def process_audio(self):
    while not self.shutdown_flag.is_set():
        if self.audio_queue:
            print(f"Processing audio frame: {len(self.audio_queue)}")
            # ... existing code
```

### Performance Profiling

Profile system performance:

```python
import cProfile
import pstats

def profile_similarity_calculation():
    pr = cProfile.Profile()
    pr.enable()
    
    # Run similarity calculation
    results = calculator.compare(input_text, candidates)
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('tottime')
    stats.print_stats(10)  # Top 10 functions
```

### Memory Analysis

Monitor memory usage:

```python
import tracemalloc

tracemalloc.start()
# ... run operations
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
```

## Getting Help

### Log Collection

When reporting issues, collect relevant information:

```bash
# System information
python --version
pip list | grep -E "(instructor|sounddevice|sherpa|sentence)"

# Error logs
python app.py presentation control "Speaker" 2>&1 | tee error.log

# Configuration
python app.py settings list

# Audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Common Error Patterns

#### Pattern: Import Errors
```python
ModuleNotFoundError: No module named 'module_name'
```
**Solution:** Check virtual environment and reinstall dependencies

#### Pattern: Permission Errors
```python
PermissionError: [Errno 13] Permission denied
```
**Solution:** Fix file permissions or run with appropriate privileges

#### Pattern: Network Errors
```python
requests.exceptions.ConnectionError
```
**Solution:** Check network connectivity and proxy settings

### Community Support

1. **Search existing issues** on GitHub repository
2. **Create detailed bug reports** with:
   - System information
   - Error messages
   - Steps to reproduce
   - Configuration details
3. **Join discussions** for troubleshooting help
4. **Check documentation** for configuration examples

### Professional Support

For enterprise or critical use cases:
- Consider professional consulting services
- Custom deployment assistance
- Priority bug fixes and features
- Service-level agreements

This troubleshooting guide covers the most common issues encountered when using Moves. Most problems can be resolved by following these systematic diagnostic and solution steps.