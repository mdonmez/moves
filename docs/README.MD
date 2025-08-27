# moves Technical Documentation

### moves - Presentation control, reimagined.

**moves** is an intelligent presentation management and control application. It leverages a sophisticated, multi-layered system to synchronize a speaker's live narration with the corresponding presentation slides, enabling automated, voice-driven navigation.

The system manages speaker profiles, performs AI-driven analysis of presentation and transcript documents, tracks live audio streams, and executes real-time slide transitions.

## Core System Pillars

- **Intelligent Content Analysis**: Utilizes a Large Language Model (LLM) to parse presentation slides and spoken transcripts, establishing a semantic map between them. This process generates structured `Section` data, which forms the basis for navigation.
- **Hybrid Similarity Matching**: Employs a dual-channel similarity algorithm that combines semantic (meaning-based) and phonetic (sound-based) analysis. This ensures robust and accurate matching between the live speech and the pre-processed `Section` content, even with variations in wording or speech-to-text inaccuracies.
- **Real-time Voice-to-Action Pipeline**: A low-latency pipeline captures microphone audio, performs streaming speech-to-text (STT), calculates similarity scores, and dispatches keyboard commands to control the presentation software.
- **Speaker-Centric Data Management**: Provides a clear system for managing speaker profiles, their source materials (presentations and transcripts), and the resulting processed data, ensuring modularity and reusability.

## Documentation

This repository contains comprehensive technical documentation detailing the system's architecture, algorithms, and data structures.

- For a high-level system summary, refer to the [Overview](overview.md).
- For a detailed breakdown of components and data flows, see the [Architecture](architecture.md) document.
- For in-depth explanations of specific algorithms and processes, explore the [About](about/) directory.

---

_In a nutshell, moves lets the speaker shine; while it manages the rest._