# Presentation Controller

The `PresentationController` is the core component responsible for real-time voice-controlled presentation navigation. It integrates speech recognition, similarity matching, and slide navigation into a cohesive system that responds to speaker's voice in real-time.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Threading Model](#threading-model)
- [Audio Processing](#audio-processing)
- [Navigation Logic](#navigation-logic)
- [Manual Controls](#manual-controls)
- [Configuration](#configuration)
- [Performance Optimization](#performance-optimization)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

## Overview

**Location**: `src/core/presentation_controller.py`

The PresentationController manages the entire real-time presentation control session, from audio input to slide navigation. It operates as a multi-threaded system that continuously:

1. **Captures Audio**: Records microphone input with low latency
2. **Recognizes Speech**: Converts audio to text using local ONNX models
3. **Matches Content**: Compares speech against presentation sections
4. **Navigates Slides**: Automatically moves to appropriate slides
5. **Provides Feedback**: Shows real-time matching information

## Architecture

```python
class PresentationController:
    def __init__(self, sections, start_section, window_size=12):
        # Core components
        self.similarity_calculator = SimilarityCalculator()
        self.recognizer = OnlineRecognizer.from_transducer(...)

        # Navigation state
        self.sections = sections
        self.current_section = start_section
        self.chunks = chunk_producer.generate_chunks(sections, window_size)

        # Real-time processing
        self.recent_words = deque(maxlen=window_size)
        self.audio_queue = deque(maxlen=5)

        # Thread coordination
        self.shutdown_flag = threading.Event()
        self.navigator_working = False
        self.paused = False
```

### Key Components

#### 1. Speech Recognition Engine

- **Technology**: Sherpa-ONNX with local transducer models
- **Models**: INT8 quantized for optimal performance
- **Processing**: Real-time streaming recognition

#### 2. Similarity Calculator

- **Hybrid Approach**: Combines semantic and phonetic matching
- **Weights**: Configurable balance between similarity types
- **Performance**: Optimized for real-time operation

#### 3. Navigation Engine

- **State Management**: Tracks current position and target slides
- **Keyboard Simulation**: Programmatic slide navigation
- **Manual Override**: Seamless keyboard control integration

## Key Features

### 1. Real-Time Speech Processing

```python
def process_audio(self):
    while not self.shutdown_flag.is_set():
        if self.audio_queue:
            chunk = self.audio_queue.popleft()
            self.stream.accept_waveform(self.sample_rate, chunk)

            if text := self.recognizer.get_result(self.stream):
                normalized_text = text_normalizer.normalize_text(text)
                words = normalized_text.strip().split()[-self.window_size:]
                self.recent_words.extend(words)
```

**Features**:

- **Continuous Processing**: Non-blocking audio stream processing
- **Word Window**: Maintains sliding window of recent speech
- **Text Normalization**: Standardizes text for consistent matching

### 2. Intelligent Navigation

```python
def navigate_presentation(self):
    while not self.shutdown_flag.is_set():
        current_words = list(self.recent_words)

        if len(current_words) >= self.window_size and not self.paused:
            # Get candidate chunks near current position
            candidate_chunks = chunk_producer.get_candidate_chunks(
                self.current_section, self.chunks
            )

            # Calculate similarity scores
            input_text = " ".join(current_words)
            similarity_results = self.similarity_calculator.compare(
                input_text, candidate_chunks
            )

            # Navigate to best match
            best_chunk = similarity_results[0].chunk
            target_section = best_chunk.source_sections[-1]
            self._navigate_to_section(target_section)
```

**Navigation Logic**:

- **Contextual Matching**: Only considers slides near current position
- **Best Match Selection**: Chooses highest similarity score
- **Smooth Transitions**: Handles multi-slide jumps gracefully

### 3. Multi-Modal Control

The controller supports both automatic and manual navigation:

**Automatic Navigation**:

- Speech-driven slide transitions
- Real-time similarity matching
- Contextual positioning

**Manual Override**:

- **Right Arrow**: Next slide
- **Left Arrow**: Previous slide
- **Insert Key**: Pause/resume automatic navigation

## Threading Model

The PresentationController uses a sophisticated multi-threaded architecture:

```python
# Thread Structure
├── Main Thread (Audio Stream Management)
├── Audio Processing Thread (Speech Recognition)
├── Navigation Thread (Similarity & Navigation)
└── Keyboard Listener Thread (Manual Controls)
```

### Thread Coordination

```python
# Global coordination
self.shutdown_flag = threading.Event()  # Shutdown signal
self.navigator_working = False          # Navigation lock
self.paused = False                     # User pause state

# Thread startup
audio_thread = threading.Thread(target=self.process_audio, daemon=True)
self.navigator = threading.Thread(target=self.navigate_presentation, daemon=True)
self.keyboard_listener = Listener(on_press=self._on_key_press)

# Synchronized shutdown
self.shutdown_flag.set()
audio_thread.join(timeout=1.0)
self.navigator.join(timeout=1.0)
self.keyboard_listener.stop()
```

**Benefits**:

- **Responsiveness**: Audio and navigation processing run independently
- **Thread Safety**: Proper synchronization prevents race conditions
- **Clean Shutdown**: Graceful termination of all threads

## Audio Processing

### Audio Configuration

```python
# Audio parameters optimized for speech recognition
self.frame_duration = 0.1      # 100ms frames for low latency
self.sample_rate = 16000       # Standard speech recognition rate
self.selected_mic = sd.default.device[0]  # Auto-detect microphone
```

### Processing Pipeline

```python
# Audio capture → Queue → Recognition → Normalization → Word extraction
with sd.InputStream(
    samplerate=self.sample_rate,
    blocksize=int(self.sample_rate * self.frame_duration),
    callback=lambda indata, *_: self.audio_queue.append(indata[:, 0].copy())
):
    # Continuous audio stream processing
```

**Optimization Features**:

- **Low Latency**: 100ms frame processing for responsive recognition
- **Buffer Management**: Bounded queues prevent memory buildup
- **Device Flexibility**: Automatic microphone detection and configuration

## Navigation Logic

### Contextual Matching

The controller doesn't match against all slides, but uses contextual windows:

```python
def get_candidate_chunks(current_section, all_chunks):
    idx = int(current_section.section_index)
    start, end = idx - 2, idx + 3  # ±2-3 slide window

    return [chunk for chunk in all_chunks
            if all(start <= s.section_index <= end for s in chunk.source_sections)]
```

**Benefits**:

- **Performance**: Reduces computation by limiting search space
- **Accuracy**: Prevents jumping to unrelated distant slides
- **Context Preservation**: Maintains logical presentation flow

### Navigation Execution

```python
def _navigate_to_section(self, target_section):
    current_idx = self.current_section.section_index
    target_idx = target_section.section_index
    navigation_distance = target_idx - current_idx

    if navigation_distance != 0:
        key = Key.right if navigation_distance > 0 else Key.left

        # Execute multiple key presses for large jumps
        for _ in range(abs(navigation_distance)):
            self.keyboard_controller.press(key)
            self.keyboard_controller.release(key)
            if abs(navigation_distance) > 1:
                time.sleep(0.01)  # Brief delay between presses

    self.current_section = target_section
```

## Manual Controls

### Keyboard Integration

The controller seamlessly integrates manual keyboard controls:

```python
def _on_key_press(self, key):
    if key == Key.right:
        self._next_section()
    elif key == Key.left:
        self._prev_section()
    elif key == Key.insert:
        self._toggle_pause()

def _toggle_pause(self):
    self.paused = not self.paused
    print("\n[Paused]" if self.paused else "\n[Resumed]")
```

**Manual Controls**:

- **Arrow Keys**: Override automatic navigation
- **Insert Key**: Toggle automatic navigation on/off
- **Seamless Integration**: Manual controls update internal state

### State Management

```python
def _next_section(self):
    current_idx = self.current_section.section_index
    if current_idx < len(self.sections) - 1:
        self.current_section = self.sections[current_idx + 1]
        print(f"\n[Manual Next] {current_idx + 1} → {current_idx + 2}")
```

## Configuration

### Initialization Parameters

```python
def __init__(
    self,
    sections: list[Section],        # Processed presentation sections
    start_section: Section,         # Initial slide position
    window_size: int = 12,          # Speech window size (words)
):
```

### Runtime Configuration

```python
# Audio settings
self.frame_duration = 0.1       # Audio frame duration (seconds)
self.sample_rate = 16000        # Audio sampling rate (Hz)

# Recognition settings
num_threads=8,                  # ONNX model threads
decoding_method="greedy_search" # Recognition strategy

# Navigation settings
maxlen=window_size             # Word window size
maxlen=5                       # Audio queue size
```

**Tunable Parameters**:

- **Window Size**: Balance between context and responsiveness
- **Frame Duration**: Trade-off between latency and recognition accuracy
- **Queue Sizes**: Memory vs. processing buffer management

## Performance Optimization

### 1. Audio Processing Optimization

```python
# Efficient audio handling
self.audio_queue = deque(maxlen=5)        # Bounded queue
blocksize = int(self.sample_rate * self.frame_duration)  # Optimal block size
dtype="float32"                           # Efficient audio format
```

### 2. Recognition Optimization

```python
# Local ONNX models for zero network latency
self.recognizer = OnlineRecognizer.from_transducer(
    encoder="encoder.int8.onnx",    # Quantized for speed
    decoder="decoder.int8.onnx",
    joiner="joiner.int8.onnx",
    num_threads=8                   # Multi-threaded inference
)
```

### 3. Navigation Optimization

```python
# Prevent navigation conflicts
if not self.navigator_working:
    self.navigator_working = True
    try:
        # Navigation logic
        pass
    finally:
        self.navigator_working = False
```

**Performance Features**:

- **Thread Isolation**: Prevents blocking between audio and navigation
- **Efficient Data Structures**: Bounded collections for memory management
- **Local Processing**: No network dependency during presentations

## Error Handling

### Graceful Degradation

```python
def process_audio(self):
    while not self.shutdown_flag.is_set():
        try:
            # Audio processing
            pass
        except Exception as e:
            raise RuntimeError(f"Audio processing error: {e}") from e
```

### Resource Management

```python
def control(self):
    try:
        with sd.InputStream(...):
            # Presentation control loop
            pass
    except KeyboardInterrupt:
        pass  # Graceful exit on Ctrl+C
    finally:
        self.shutdown_flag.set()
        # Cleanup all threads
        if audio_thread.is_alive():
            audio_thread.join(timeout=1.0)
```

**Error Handling Strategy**:

- **Fail Fast**: Detect errors early and provide clear messages
- **Resource Cleanup**: Ensure proper thread and resource cleanup
- **User Experience**: Handle interruptions gracefully

## Usage Examples

### Basic Usage

```python
# Initialize with processed sections
controller = PresentationController(
    sections=processed_sections,
    start_section=processed_sections[0],
    window_size=12
)

# Start voice control session
controller.control()  # Blocks until Ctrl+C or error
```

### Custom Configuration

```python
# Custom window size for different speech patterns
controller = PresentationController(
    sections=sections,
    start_section=start_section,
    window_size=8  # Smaller window for faster speakers
)

# Access internal state
current_slide = controller.current_section.section_index
print(f"Currently on slide {current_slide + 1}")
```

### Integration Example

```python
# CLI integration
def presentation_control(speaker: str):
    try:
        # Load processed speaker data
        sections = load_speaker_sections(speaker)

        # Create and configure controller
        controller = PresentationController(
            sections=sections,
            start_section=sections[0]
        )

        # Provide user feedback
        print(f"Starting presentation control for '{speaker}'")
        print(f"    {len(sections)} sections loaded")
        print("    READY & LISTENING")

        # Start control session
        controller.control()

    except Exception as e:
        print(f"Control error: {e}")
        raise typer.Exit(1)
```

## Real-Time Feedback

The controller provides continuous feedback during operation:

```python
# Navigation feedback
print(f"\n[{target_section.section_index + 1}/{len(self.sections)}]")
print(f"Speech  -> {recent_speech}")
print(f"Match   -> {recent_match}")

# Manual control feedback
print(f"\n[Manual Next] {prev_idx + 1} → {current_idx + 1}")
print(f"\n[Paused]" if paused else "\n[Resumed]")
```

This comprehensive feedback helps users understand system behavior and troubleshoot navigation issues in real-time.

The PresentationController represents the culmination of all system components working together to provide seamless, intelligent presentation navigation that responds naturally to the speaker's voice while maintaining full manual control when needed.
