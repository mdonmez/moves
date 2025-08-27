# Utilities

The `src/utils/` directory contains several modules with helper functions that provide essential services throughout the application.

## `data_handler.py`

This module provides a centralized and safe way to interact with the file system. All file operations are relative to a `.moves` directory in the user's home folder. This ensures that the application's data is stored in a consistent and predictable location.

- **`write()`**: Writes text data to a file.
- **`read()`**: Reads text data from a file.
- **`list()`**: Lists the contents of a directory.
- **`rename()`**: Renames a file.
- **`delete()`**: Deletes a file or directory.
- **`copy()`**: Copies a file or directory.

## `id_generator.py`

This module is responsible for creating unique identifiers used within the application.

- **`generate_speaker_id()`**: Creates a unique, URL-safe ID for a speaker based on their name and a random suffix. For example, "John Doe" might become `john-doe-aB1cD`.
- **`generate_history_id()`**: Generates a timestamp-based ID for recording presentation history, such as `20250827_10-30-00`.

## `logger.py`

Provides a simple, pre-configured logging setup. It creates a rotating file logger that saves logs to the `.moves/logs` directory. The logger is named based on the module it's called from, making it easy to trace the source of log messages.

## `text_normalizer.py`

This module contains the `normalize_text` function, which is crucial for cleaning and standardizing text before it's used in similarity comparisons. The normalization process includes:

- Converting text to lowercase.
- Removing emojis and other special characters.
- Standardizing quotes and apostrophes.
- Converting numbers to words (e.g., `123` becomes "one hundred twenty-three").
- Removing punctuation.
- Collapsing multiple whitespace characters into a single space.
