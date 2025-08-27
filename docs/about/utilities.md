# System Utilities

The `src/utils/` directory contains a collection of independent modules that provide essential, cross-cutting services to the rest of the application.

## `data_handler.py`

This module provides a centralized and secure facade for all file system interactions. It abstracts file operations and confines them to the application's data directory (`~/.moves/`), preventing accidental file access elsewhere on the system.

-   **Core Functions**: Provides atomic functions for `write`, `read`, `list`, `rename`, `delete`, and `copy`.
-   **Path Abstraction**: All paths are handled relative to the application's root data folder, simplifying file access for other modules.
-   **Error Handling**: Wraps all file I/O operations in `try...except` blocks, raising custom `RuntimeError` exceptions with detailed context upon failure.

## `id_generator.py`

This module is responsible for creating unique, standardized identifiers.

-   **`generate_speaker_id()`**: Creates a unique ID for a speaker. The process involves:
    1.  Normalizing the speaker's name to ASCII (`NFKD` normalization).
    2.  Converting to lowercase.
    3.  Replacing whitespace with hyphens.
    4.  Removing any remaining non-alphanumeric characters.
    5.  Appending a cryptographically secure, 5-character random suffix using `secrets.choice` to prevent collisions.
    Example: "Dr. Özgür Can" -> `dr-ozgur-can-aB1cD`.

-   **`generate_history_id()`**: Generates a simple, timestamp-based ID for logging or tracking presentation sessions, formatted as `YYYYMMDD_HH-MM-SS`.

## `logger.py`

Provides a pre-configured, singleton-like logging setup using Python's standard `logging` library.

-   **Dynamic Naming**: The logger is automatically named based on the module from which it is instantiated, using the `inspect` module to determine the caller's filename. This allows for granular, module-level logging.
-   **Rotating Files**: It configures a `RotatingFileHandler` that saves logs to the `.moves/logs` directory. Logs are rotated when they reach 5MB, with up to 5 backup files kept.
-   **Standard Formatting**: Log messages are formatted to include a timestamp, log level, and the message.

## `text_normalizer.py`

This module contains the `normalize_text` function, which is critical for ensuring that text is in a clean, consistent format before being used in similarity comparisons. The multi-step normalization pipeline includes:

1.  Unicode normalization (`NFC`).
2.  Conversion to lowercase.
3.  Removal of emojis and other special symbols.
4.  Standardization of quotation marks and apostrophes.
5.  Conversion of all numerical digits to their word equivalents using the `num2words` library (e.g., `42` -> "forty-two").
6.  Removal of all remaining punctuation.
7.  Collapsing of multiple whitespace characters into a single space.