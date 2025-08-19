from typing import Optional
import typer
from pathlib import Path
from src.data.models import Section

# Initialize Typer CLI application
app = typer.Typer(
    help="moves CLI - Presentation control, reimagined.",
    add_completion=False,
)

# Subcommands for speaker, presentation, and settings management
speaker_app = typer.Typer(help="Manage speaker profiles and files")
presentation_app = typer.Typer(help="Control speaker presentations")
settings_app = typer.Typer(help="View and modify application settings")


def speaker_manager_instance():
    from src.core.speaker_manager import SpeakerManager

    return SpeakerManager()


def presentation_controller_instance(
    sections: list[Section], start_section: Section, selected_mic: int | None = None
):
    from src.core.presentation_controller import PresentationController

    return PresentationController(
        sections=sections,
        start_section=start_section,
        window_size=12,
        selected_mic=selected_mic,
    )


def settings_editor_instance():
    from src.core.settings_editor import SettingsEditor

    return SettingsEditor()


# SPEAKER COMMANDS
@speaker_app.command("add")
def speaker_add(
    name: str = typer.Argument(..., help="Speaker's name"),
    source_presentation: Path = typer.Argument(..., help="Path to presentation file"),
    source_transcript: Path = typer.Argument(..., help="Path to transcript file"),
):
    """Create a new speaker profile"""
    try:
        # Validate that both file paths exist and are accessible
        if not source_presentation.exists():
            typer.echo(
                f"Error: Presentation file not found: {source_presentation}", err=True
            )
            raise typer.Exit(1)

        if not source_transcript.exists():
            typer.echo(
                f"Error: Transcript file not found: {source_transcript}", err=True
            )
            raise typer.Exit(1)

        # Create speaker manager instance and add speaker
        speaker_manager = speaker_manager_instance()
        speaker = speaker_manager.add(name, source_presentation, source_transcript)

        # Display success message with created speaker information
        typer.echo("\n✓ Speaker profile created successfully:")
        typer.echo(f"  Name: {speaker.name}")
        typer.echo(f"  Speaker ID: {speaker.speaker_id}")
        typer.echo(f"  Presentation: {speaker.source_presentation}")
        typer.echo(f"  Transcript: {speaker.source_transcript}")
        typer.echo()

    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


@speaker_app.command("edit")
def speaker_edit(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
    source_presentation: Optional[str] = typer.Option(
        None, "--presentation", "-p", help="New presentation file path"
    ),
    source_transcript: Optional[str] = typer.Option(
        None, "--transcript", "-t", help="New transcript file path"
    ),
):
    """Update speaker's presentation or transcript file"""
    try:
        # Validate at least one update parameter is provided
        if not source_presentation and not source_transcript:
            typer.echo(
                "Error: At least one update parameter (--presentation or --transcript) must be provided",
                err=True,
            )
            raise typer.Exit(1)

        # Create speaker manager instance and resolve speaker
        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)

        # Handle speaker resolution results
        if isinstance(resolved_speaker, list):
            if len(resolved_speaker) == 0:
                typer.echo(f"Error: No speaker found matching '{speaker}'", err=True)
                raise typer.Exit(1)
            elif len(resolved_speaker) > 1:
                typer.echo(
                    f"Error: Multiple speakers found matching '{speaker}'. Be more specific:",
                    err=True,
                )
                for s in resolved_speaker:
                    typer.echo(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)
            else:
                resolved_speaker = resolved_speaker[0]

        # Convert string paths to Path objects and validate
        presentation_path = Path(source_presentation) if source_presentation else None
        transcript_path = Path(source_transcript) if source_transcript else None

        if presentation_path and not presentation_path.exists():
            typer.echo(
                f"Error: Presentation file not found: {presentation_path}", err=True
            )
            raise typer.Exit(1)

        if transcript_path and not transcript_path.exists():
            typer.echo(f"Error: Transcript file not found: {transcript_path}", err=True)
            raise typer.Exit(1)

        # Update speaker
        updated_speaker = speaker_manager.edit(
            resolved_speaker, presentation_path, transcript_path
        )

        # Display updated speaker information
        typer.echo("\n✓ Speaker profile updated successfully:")
        typer.echo(f"  Name: {updated_speaker.name}")
        typer.echo(f"  Speaker ID: {updated_speaker.speaker_id}")
        typer.echo(f"  Presentation: {updated_speaker.source_presentation}")
        typer.echo(f"  Transcript: {updated_speaker.source_transcript}")
        typer.echo()

    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


@speaker_app.command("list")
def speaker_list():
    """List all registered speakers"""
    try:
        # Create speaker manager instance and get all speakers
        speaker_manager = speaker_manager_instance()
        speakers = speaker_manager.list()

        if not speakers:
            typer.echo("No speakers found.")
            return

        # Format and display speaker information in table format
        typer.echo("\nRegistered Speakers")
        typer.echo("═" * 80)

        # Header
        header = (
            f"{'Speaker ID':<15} {'Name':<20} {'Presentation':<25} {'Transcript':<25}"
        )
        typer.echo(header)
        typer.echo("─" * 80)

        # Speaker rows
        for speaker in speakers:
            presentation_name = (
                speaker.source_presentation.name
                if speaker.source_presentation
                else "N/A"
            )
            transcript_name = (
                speaker.source_transcript.name if speaker.source_transcript else "N/A"
            )

            row = f"{speaker.speaker_id:<15} {speaker.name:<20} {presentation_name:<25} {transcript_name:<25}"
            typer.echo(row)

        typer.echo("═" * 80)
        typer.echo(f"Total speakers: {len(speakers)}\n")

    except Exception as e:
        typer.echo(f"Error accessing speaker data: {str(e)}", err=True)
        raise typer.Exit(1)


@speaker_app.command("show")
def speaker_show(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
    """Display detailed speaker information"""
    try:
        # Create speaker manager instance and resolve speaker
        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)

        # Handle speaker resolution results
        if isinstance(resolved_speaker, list):
            if len(resolved_speaker) == 0:
                typer.echo(f"Error: No speaker found matching '{speaker}'", err=True)
                raise typer.Exit(1)
            elif len(resolved_speaker) > 1:
                typer.echo(
                    f"Error: Multiple speakers found matching '{speaker}'. Be more specific:",
                    err=True,
                )
                for s in resolved_speaker:
                    typer.echo(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)
            else:
                resolved_speaker = resolved_speaker[0]

        # Get paths for local files
        from src.utils import data_handler

        speaker_path = (
            data_handler.DATA_FOLDER / "speakers" / resolved_speaker.speaker_id
        )
        local_presentation = speaker_path / "presentation.pdf"
        local_transcript = speaker_path / "transcript.pdf"

        # Display detailed speaker information
        typer.echo("\nSpeaker Details")
        typer.echo("═" * 60)
        typer.echo(f"Name: {resolved_speaker.name}")
        typer.echo(f"Speaker ID: {resolved_speaker.speaker_id}")
        typer.echo()

        # Show source files information
        typer.echo("Source Files:")
        typer.echo(f"  Presentation: {resolved_speaker.source_presentation}")
        pres_exists = (
            "✓ EXISTS"
            if resolved_speaker.source_presentation.exists()
            else "✗ NOT FOUND"
        )
        typer.echo(f"     Status: {pres_exists}")

        typer.echo(f"  Transcript: {resolved_speaker.source_transcript}")
        trans_exists = (
            "✓ EXISTS" if resolved_speaker.source_transcript.exists() else "✗ NOT FOUND"
        )
        typer.echo(f"     Status: {trans_exists}")
        typer.echo()

        # Show local files information
        typer.echo("Local Files:")
        typer.echo(f"  Presentation: {local_presentation}")
        local_pres_exists = "✓ EXISTS" if local_presentation.exists() else "✗ NOT FOUND"
        typer.echo(f"     Status: {local_pres_exists}")

        typer.echo(f"  Transcript: {local_transcript}")
        local_trans_exists = "✓ EXISTS" if local_transcript.exists() else "✗ NOT FOUND"
        typer.echo(f"     Status: {local_trans_exists}")
        typer.echo()

    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


@speaker_app.command("process")
def speaker_process(
    speakers: Optional[list[str]] = typer.Argument(None, help="Speaker(s) to process"),
    all: bool = typer.Option(False, "--all", "-a", help="Process all speakers"),
):
    """Prepare speakers for live presentation control"""
    try:
        # Create speaker manager and settings editor instances
        speaker_manager = speaker_manager_instance()
        settings_editor = settings_editor_instance()

        # Get LLM configuration from settings
        settings = settings_editor.list()

        # Validate LLM settings are configured
        if not settings.llm_model:
            typer.echo(
                "Error: LLM model not configured. Use 'moves settings set llm_model <model>' to configure.",
                err=True,
            )
            raise typer.Exit(1)

        if not settings.llm_api_key:
            typer.echo(
                "Error: LLM API key not configured. Use 'moves settings set llm_api_key <key>' to configure.",
                err=True,
            )
            raise typer.Exit(1)

        # Resolve speakers
        if all:
            # Get all speakers
            speaker_list = speaker_manager.list()
            if not speaker_list:
                typer.echo("No speakers found to process.")
                return
        elif speakers:
            # Resolve each speaker from the list
            speaker_list = []

            for speaker_name in speakers:
                resolved = speaker_manager.resolve(speaker_name)

                if isinstance(resolved, list):
                    if len(resolved) == 0:
                        typer.echo(
                            f"Error: No speaker found matching '{speaker_name}'",
                            err=True,
                        )
                        raise typer.Exit(1)
                    elif len(resolved) > 1:
                        typer.echo(
                            f"Error: Multiple speakers found matching '{speaker_name}'. Be more specific:",
                            err=True,
                        )
                        for s in resolved:
                            typer.echo(f"  - {s.name} ({s.speaker_id})")
                        raise typer.Exit(1)
                    else:
                        speaker_list.append(resolved[0])
                else:
                    speaker_list.append(resolved)
        else:
            typer.echo(
                "Error: Either provide speaker names or use --all to process all speakers.",
                err=True,
            )
            raise typer.Exit(1)

        # Display processing start message
        typer.echo(
            f"\nProcessing {len(speaker_list)} speaker(s) with {settings.llm_model}..."
        )

        # Call speaker_manager.process with resolved speakers
        results = speaker_manager.process(
            speaker_list, settings.llm_model, settings.llm_api_key
        )

        # Display processing results
        typer.echo("\n✓ Processing completed successfully")
        typer.echo("═" * 60)

        for i, result in enumerate(results):
            speaker = speaker_list[i]
            typer.echo(f"Speaker: {speaker.name} ({speaker.speaker_id})")
            typer.echo(f"  Sections generated: {result.section_count}")
            typer.echo(f"  Transcript source: {result.transcript_from}")
            typer.echo(f"  Presentation source: {result.presentation_from}")
            typer.echo()

    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Processing error: {str(e)}", err=True)
        raise typer.Exit(1)


@speaker_app.command("delete")
def speaker_delete(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
    """Remove a speaker and their data"""
    try:
        # Create speaker manager instance and resolve speaker
        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)

        # Handle speaker resolution results
        if isinstance(resolved_speaker, list):
            if len(resolved_speaker) == 0:
                typer.echo(f"Error: No speaker found matching '{speaker}'", err=True)
                raise typer.Exit(1)
            elif len(resolved_speaker) > 1:
                typer.echo(
                    f"Error: Multiple speakers found matching '{speaker}'. Be more specific:",
                    err=True,
                )
                for s in resolved_speaker:
                    typer.echo(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)
            else:
                resolved_speaker = resolved_speaker[0]

        # Display confirmation and delete
        typer.echo(
            f"\nDeleting speaker: {resolved_speaker.name} ({resolved_speaker.speaker_id})"
        )

        success = speaker_manager.delete(resolved_speaker)

        if success:
            typer.echo("✓ Speaker and associated data deleted successfully\n")
        else:
            typer.echo("Error: Failed to delete speaker data.", err=True)
            raise typer.Exit(1)

    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


# PRESENTATION COMMANDS
@presentation_app.command("control")
def presentation_control(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
    """Start live control of a speaker's presentation"""
    try:
        import json
        from src.utils import data_handler
        from src.core.components import section_producer

        # Create speaker manager and settings editor instances
        speaker_manager = speaker_manager_instance()
        settings_editor = settings_editor_instance()

        # Get microphone setting
        settings = settings_editor.list()
        selected_mic = settings.selected_mic

        # Resolve speaker
        resolved_speaker = speaker_manager.resolve(speaker)

        # Handle speaker resolution results
        if isinstance(resolved_speaker, list):
            if len(resolved_speaker) == 0:
                typer.echo(f"Error: No speaker found matching '{speaker}'", err=True)
                raise typer.Exit(1)
            elif len(resolved_speaker) > 1:
                typer.echo(
                    f"Error: Multiple speakers found matching '{speaker}'. Be more specific:",
                    err=True,
                )
                for s in resolved_speaker:
                    typer.echo(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)
            else:
                resolved_speaker = resolved_speaker[0]

        # Check for processed sections data
        speaker_path = (
            data_handler.DATA_FOLDER / "speakers" / resolved_speaker.speaker_id
        )
        sections_file = speaker_path / "sections.json"

        if not sections_file.exists():
            typer.echo(
                f"Error: Speaker '{resolved_speaker.name}' has not been processed yet.",
                err=True,
            )
            typer.echo("Please run 'moves speaker process' first to generate sections.")
            raise typer.Exit(1)

        # Load sections data
        try:
            sections_data = json.loads(data_handler.read(sections_file))
            sections = section_producer.convert_to_objects(sections_data)
        except Exception as e:
            typer.echo(f"Error: Failed to load sections data: {str(e)}", err=True)
            raise typer.Exit(1)

        if not sections:
            typer.echo("Error: No sections found in processed data.", err=True)
            raise typer.Exit(1)

        # Determine starting section (first section)
        start_section = sections[0]

        # Create and start presentation controller
        typer.echo(f"\nStarting presentation control for: {resolved_speaker.name}")
        typer.echo(f"Loaded {len(sections)} sections")
        if selected_mic is not None:
            typer.echo(f"Using microphone index: {selected_mic}")
        else:
            typer.echo("Using default microphone")
        typer.echo("═" * 50)

        controller = presentation_controller_instance(
            sections, start_section, selected_mic
        )
        controller.control()

    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except KeyboardInterrupt:
        typer.echo("\nPresentation control stopped.")
    except Exception as e:
        typer.echo(f"Presentation control error: {str(e)}", err=True)
        raise typer.Exit(1)


# SETTINGS COMMANDS
@settings_app.command("list")
def settings_list():
    """Show all current application settings"""
    try:
        # Create settings editor instance
        settings_editor = settings_editor_instance()
        settings = settings_editor.list()

        typer.echo("\nApplication Settings")
        typer.echo("═" * 50)

        # Display LLM configuration
        typer.echo(
            f"LLM Model: {settings.llm_model if settings.llm_model else 'Not configured'}"
        )

        # Mask API key for security
        if settings.llm_api_key:
            masked_key = (
                settings.llm_api_key[:8] + "..." + settings.llm_api_key[-4:]
                if len(settings.llm_api_key) > 12
                else "***"
            )
            typer.echo(f"LLM API Key: {masked_key}")
        else:
            typer.echo("LLM API Key: Not configured")

        # Display microphone settings
        try:
            # Try to import sounddevice to query audio devices
            import sounddevice as sd

            # Get available input devices
            input_devices = sd.query_devices(kind="input")

            typer.echo(
                f"\nSelected Microphone: {settings.selected_mic if settings.selected_mic is not None else 'Default'}"
            )
            typer.echo("\nAvailable Input Devices:")
            typer.echo("─" * 30)

            typer.echo(input_devices)

        except ImportError:
            typer.echo(
                f"\nSelected Microphone: {settings.selected_mic if settings.selected_mic is not None else 'Default'}"
            )
            typer.echo(
                "Audio device querying not available (sounddevice not installed)"
            )
        except Exception as e:
            typer.echo(
                f"\nSelected Microphone: {settings.selected_mic if settings.selected_mic is not None else 'Default'}"
            )
            typer.echo(f"Error querying audio devices: {str(e)}")

    except Exception as e:
        typer.echo(f"Error accessing settings: {str(e)}", err=True)
        raise typer.Exit(1)


@settings_app.command("set")
def settings_set(
    key: str = typer.Argument(..., help="Setting name to update"),
    value: str = typer.Argument(..., help="New setting value"),
):
    """Change the value of an application setting"""
    try:
        # Create settings editor instance
        settings_editor = settings_editor_instance()

        # Valid setting keys
        valid_keys = ["llm_model", "llm_api_key", "selected_mic"]

        if key not in valid_keys:
            typer.echo(f"Error: Invalid setting key '{key}'", err=True)
            typer.echo(f"Valid keys: {', '.join(valid_keys)}")
            raise typer.Exit(1)

        # Special handling for selected_mic (convert to int)
        if key == "selected_mic":
            try:
                value = str(int(value))
            except ValueError:
                typer.echo(
                    f"Error: selected_mic must be an integer, got '{value}'", err=True
                )
                raise typer.Exit(1)

        # Update setting
        success = settings_editor.set(key, value)

        if success:
            # Display confirmation (mask API key in output)
            if key == "llm_api_key":
                display_value = (
                    value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                )
                typer.echo(f"✓ Setting updated: {key} = {display_value}")
            else:
                typer.echo(f"✓ Setting updated: {key} = {value}")
        else:
            typer.echo(f"Error: Failed to update setting '{key}'", err=True)
            raise typer.Exit(1)

    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


@settings_app.command("unset")
def settings_unset(
    key: str = typer.Argument(..., help="Setting name to reset"),
):
    """Reset a setting to its default value"""
    try:
        # Create settings editor instance
        settings_editor = settings_editor_instance()

        # Check if key exists in template
        valid_keys = ["llm_model", "llm_api_key", "selected_mic"]
        if key not in valid_keys:
            typer.echo(f"Error: Invalid setting key '{key}'", err=True)
            typer.echo(f"Valid keys: {', '.join(valid_keys)}")
            raise typer.Exit(1)

        # Get the template value to show what it will be reset to
        template_value = settings_editor.template_data.get(key)

        # Reset setting
        success = settings_editor.unset(key)

        if success:
            if key in settings_editor.template_data:
                # Display confirmation showing the reset value
                if (
                    key == "llm_api_key"
                    and template_value
                    and template_value != "null"
                    and template_value is not None
                ):
                    display_value = (
                        str(template_value)[:8] + "..." + str(template_value)[-4:]
                        if len(str(template_value)) > 12
                        else "***"
                    )
                    typer.echo(f"✓ Setting reset: {key} = {display_value} (default)")
                else:
                    display_value = (
                        "Not configured"
                        if template_value is None
                        else str(template_value)
                    )
                    typer.echo(f"✓ Setting reset: {key} = {display_value} (default)")
            else:
                # Key was removed (not in template)
                typer.echo(f"✓ Setting removed: {key}")
        else:
            typer.echo(f"Error: Failed to reset setting '{key}'", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


# Register subcommands
app.add_typer(speaker_app, name="speaker")
app.add_typer(presentation_app, name="presentation")
app.add_typer(settings_app, name="settings")

if __name__ == "__main__":
    app()
