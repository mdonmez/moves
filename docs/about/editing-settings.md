# Application Configuration Management

The `SettingsEditor` class provides a robust and safe mechanism for managing the application's configuration. It handles the interaction with the `settings.yaml` file, ensuring that the configuration is always valid and complete.

## Template Overlay System

The settings management employs a template overlay or merging strategy to ensure consistency and provide sensible defaults.

-   **Initialization**: When the `SettingsEditor` is instantiated, it performs a three-step process:
    1.  It first loads the default values from the `settings_template.yaml` file, which is bundled with the application.
    2.  It then loads the user's existing `settings.yaml` from the application's data directory (`.moves/`).
    3.  It merges the two, with the user's settings taking precedence over the template's defaults. This ensures that any settings defined by the user are respected, while any missing settings are filled in from the template.

-   **Saving**: After the merge, the combined data is immediately saved back to the user's `settings.yaml`. This guarantees that the configuration file on disk is always complete and up-to-date with all available settings.

## Core Functionality

-   **`set(key, value)`**: This method allows for the modification of a setting. It first validates that the `key` exists in the template data, preventing the addition of arbitrary or misspelled keys. It then updates the value in its internal data representation and triggers a save.

-   **`unset(key)`**: This method reverts a specific setting to its default value as defined in the `settings_template.yaml`. If the key exists in the template, its value is restored; otherwise, it is removed. This is followed by a save.

-   **`list()`**: This method returns a `Settings` Pydantic model, providing a type-safe, read-only view of the current configuration.

```mermaid
graph TD
    A[SettingsEditor.__init__] --> B{Load settings_template.yaml};
    A --> C{Load user's settings.yaml};
    B & C --> D{Merge Data (User > Template)};
    D --> E[Save merged data to user's settings.yaml];

    F[settings set command] --> G{SettingsEditor.set};
    G --> H[Update internal data];
    H --> I{Save to settings.yaml};

    J[settings unset command] --> K{SettingsEditor.unset};
    K --> L[Revert to template value];
    L --> I;

    M[settings list command] --> N{SettingsEditor.list};
    N --> O[Return Settings object];
```