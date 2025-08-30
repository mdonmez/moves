# moves

_Presentation control, reimagined._

[![moves](https://img.shields.io/badge/moves-003399?style=flat-square&color=003399&logoColor=ffffff)](https://github.com/mdonmez/moves)
[![Python](https://img.shields.io/badge/python-3.13-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-d32f2f?style=flat-square&logo=gnu&logoColor=white)](https://www.gnu.org/licenses/gpl-3.0)

`moves` is a smart presentation management system that leverages offline speech recognition and a hybrid similarity engine to control your slide transitions automatically. Speak naturally, and `moves` advances your slides for you, creating a seamless, hands-free presentation experience.

---

### Table of Contents

- [✨ Features](#-features)
- [⏬ Installation](#-installation)
- [🖱️ Usage](#-usage)
  - [Get Started in 3 Steps](#get-started-in-3-steps)
  - [Command Overview](#command-overview)
- [📚 Documentation](#-documentation)
- [🧪 Tests](#-tests)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## ✨ Features

- **🙌 Hands-Free:** Speak naturally and let your slides advance automatically. Maintain smooth pacing without interruptions, keeping your audience engaged throughout.
- **🧠 Intelligent:** Advanced AI analyzes your transcript, segments it into meaningful sections, and maps them accurately to your slides for seamless navigation.
- **🔒 Private:** All processing—speech-to-text conversion and similarity matching—happens locally on your device. No internet is required, ensuring full privacy and minimal latency.
- **🎯 Accurate:** Combines semantic (meaning-based) and phonetic (sound-based) analysis to align your speech precisely with slides. Handles mispronunciations, minor deviations, and homophones effortlessly.
- **⌨️ Controlled:** Full keyboard override lets you pause, resume, or manually navigate slides anytime, giving you complete command over your presentation.
- **⚙️ Configurable:** Clean and intuitive CLI allows easy management of speaker profiles, processing of presentation data, and adjustment of settings for both simple and advanced workflows.

## ⏬ Installation

Follow these steps to get `moves` up and running.

#### 1. Prerequisites

- [Python 3.13+](https://www.python.org/)
- [Git LFS](https://git-lfs.com/) for downloading the required machine learning models.
- [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver).

#### 2. Clone the Repository

Clone this repository to your local machine.

```bash
git clone https://github.com/your-username/moves.git
cd moves
```

#### 3. Download ML Models

The required speech-to-text models are stored using Git LFS. Make sure it's installed, then pull the model files.

```bash
git lfs install
git lfs pull
```

#### 4. Install Dependencies

Create a virtual environment and install all required packages using `uv`.

```bash
# Create and activate a virtual environment
uv venv

# Install dependencies from uv.lock
uv sync
```

You are now ready to use `moves`!

## 🖱️ Usage

Using `moves` involves three simple steps: configuring your AI, processing your presentation, and starting the control session.

### Get Started in 3 Steps

#### 1. Configure Your AI Model

First, tell `moves` which Large Language Model (LLM) to use for processing your script. You'll also need to provide an API key.

> **Note:** Find a list of compatible models at [LiteLLM Supported Models](https://models.litellm.ai/).

```bash
# Set the desired model (e.g., OpenAI's GPT-4o Mini)
moves settings set model openai/gpt-4o-mini

# Set your API key
moves settings set key YOUR_API_KEY_HERE
```

#### 2. Add and Process a Speaker

Next, create a "speaker" profile by providing your presentation and transcript files (both must be in PDF format). Then, process them to prepare for AI control.

```bash
# Add a speaker with their presentation and transcript
moves speaker add "John Doe" ./path/to/presentation.pdf ./path/to/transcript.pdf

# Process the speaker's data
moves speaker process "John Doe"
```

This step uses the configured LLM to align your transcript with your slides and may take a few moments.

#### 3. Start the Presentation

Finally, open your presentation in fullscreen and run the control command.

```bash
moves presentation control "John Doe"
```

`moves` will start listening. As you speak, it will automatically press the `Right Arrow` key to advance your slides at the right moments.

### Command Overview

`moves` provides a simple but powerful CLI for managing your presentations.

| Command              | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `moves speaker`      | Manage speaker profiles, files, and AI processing.   |
| `moves presentation` | Start a live, voice-controlled presentation session. |
| `moves settings`     | Configure the LLM model and API key.                 |

For more details please refer to the [CLI Commands](./docs/cli_commands.md).

## 📚 Documentation

For a deeper dive into the system's architecture, components, and design decisions, please refer to the [Documentation](./docs/README.md) that covers:

- **[Architecture](./docs/architecture.md):** A high-level overview of the system's structure.
- **[Technical Details](./docs/about/README.md):** In-depth explanations of key components like the similarity engine, data models, and STT pipeline.

## 🧪 Tests

> [!NOTE]  
> Tests are currently under development and will be available soon.

## 🤝 Contributing

Contributions are welcome! If you'd like to help improve `moves`, please follow these steps:

1.  **Fork** the repository on GitHub.
2.  **Clone** your fork locally.
3.  **Create a new branch** for your feature or bug fix (`git checkout -b feature/my-new-feature`).
4.  **Set up the environment** using `uv venv` and `uv sync`.
5.  **Make your changes** and commit them with a clear message.
6.  **Push** your branch to your fork (`git push origin feature/my-new-feature`).
7.  **Open a pull request** to the main repository.

## 📜 License

This project is licensed under the terms of the GNU General Public License v3.0. For more details, see the [LICENSE](./LICENSE) file.
