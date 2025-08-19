from typing import Optional
import typer
from pathlib import Path
from src.data.models import Section


def speaker_manager_instance():
    """Get a SpeakerManager instance"""
    from src.core.speaker_manager import SpeakerManager

    return SpeakerManager()


def presentation_controller_instance(sections: list[Section], start_section: Section):
    """Get a PresentationController instance"""
    from src.core.presentation_controller import PresentationController

    return PresentationController(
        sections=sections,
        start_section=start_section,
        window_size=12,
    )


def settings_editor_instance():
    """Get a SettingsEditor instance"""
    from src.core.settings_editor import SettingsEditor

    return SettingsEditor()


def validate_speaker_resolution(resolved_speaker, speaker_name: str):
    """Helper function to validate and handle speaker resolution results"""
    if isinstance(resolved_speaker, list):
        if len(resolved_speaker) == 0:
            typer.echo(f"Error: No speaker found matching '{speaker_name}'", err=True)
            raise typer.Exit(1)
        elif len(resolved_speaker) > 1:
            typer.echo(
                f"Error: Multiple speakers found matching '{speaker_name}'. Be more specific:",
                err=True,
            )
            for s in resolved_speaker:
                typer.echo(f"    {s.name} ({s.speaker_id})", err=True)
            raise typer.Exit(1)
        else:
            return resolved_speaker[0]
    return resolved_speaker


# Initialize Typer CLI application
app = typer.Typer(
    help="moves CLI - AI-powered presentation control system for seamless slide navigation.",
    add_completion=False,
)

# Subcommands for speaker, presentation, and settings management
speaker_app = typer.Typer(help="Manage speaker profiles, files, and processing")
presentation_app = typer.Typer(help="Live presentation control with voice navigation")
settings_app = typer.Typer(help="Configure system settings (model, API key)")


# =============================================================================
# SPEAKER COMMANDS
# =============================================================================
@speaker_app.command("add")
def speaker_add(
    name: str = typer.Argument(..., help="Speaker's name"),
    source_presentation: Path = typer.Argument(..., help="Path to presentation file"),
    source_transcript: Path = typer.Argument(..., help="Path to transcript file"),
):
    """Create a new speaker profile with presentation and transcript files"""
    # Validate that both file paths exist and are accessible
    if not source_presentation.exists():
        typer.echo(f"Could not add speaker '{name}'.", err=True)
        typer.echo(f"    Presentation file not found: {source_presentation}", err=True)
        raise typer.Exit(1)

    if not source_transcript.exists():
        typer.echo(f"Could not add speaker '{name}'.", err=True)
        typer.echo(f"    Transcript file not found: {source_transcript}", err=True)
        raise typer.Exit(1)

    try:
        # Create speaker manager instance and add speaker
        speaker_manager = speaker_manager_instance()
        speaker = speaker_manager.add(name, source_presentation, source_transcript)

        # Display success message in Direct Summary format
        typer.echo(f"Speaker '{speaker.name}' ({speaker.speaker_id}) added.")
        typer.echo(f"    ID -> {speaker.speaker_id}")
        typer.echo(f"    Presentation -> {speaker.source_presentation}")
        typer.echo(f"    Transcript -> {speaker.source_transcript}")

    except ValueError as e:
        typer.echo(f"Could not add speaker '{name}'.", err=True)
        typer.echo(f"    {str(e)}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Could not add speaker '{name}'.", err=True)
        typer.echo(f"    Unexpected error: {str(e)}", err=True)
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
    """Update speaker's source files (presentation or transcript paths)"""
    # Validate at least one update parameter is provided
    if not source_presentation and not source_transcript:
        typer.echo(
            "Error: At least one update parameter (--presentation or --transcript) must be provided",
            err=True,
        )
        raise typer.Exit(1)

    try:
        # Create speaker manager instance and resolve speaker
        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)
        resolved_speaker = validate_speaker_resolution(resolved_speaker, speaker)

        # Convert string paths to Path objects and validate
        presentation_path = Path(source_presentation) if source_presentation else None
        transcript_path = Path(source_transcript) if source_transcript else None

        if presentation_path and not presentation_path.exists():
            typer.echo(f"Could not update speaker '{resolved_speaker.name}'.", err=True)
            typer.echo(
                f"    Presentation file not found: {presentation_path}", err=True
            )
            raise typer.Exit(1)

        if transcript_path and not transcript_path.exists():
            typer.echo(f"Could not update speaker '{resolved_speaker.name}'.", err=True)
            typer.echo(f"    Transcript file not found: {transcript_path}", err=True)
            raise typer.Exit(1)

        # Update speaker
        updated_speaker = speaker_manager.edit(
            resolved_speaker, presentation_path, transcript_path
        )

        # Display updated speaker information in Direct Summary format
        typer.echo(f"Speaker '{updated_speaker.name}' updated.")
        if presentation_path:
            typer.echo(f"    Presentation -> {updated_speaker.source_presentation}")
        if transcript_path:
            typer.echo(f"    Transcript -> {updated_speaker.source_transcript}")

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in the generic handler
        raise
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


@speaker_app.command("list")
def speaker_list():
    """List all registered speakers with ready status"""
    try:
        # Create speaker manager instance and get all speakers
        speaker_manager = speaker_manager_instance()
        speakers = speaker_manager.list()

        if not speakers:
            typer.echo("No speakers are registered.")
            return

        # Display speakers in Direct Summary format
        typer.echo(f"Registered Speakers ({len(speakers)})")
        typer.echo()

        # Table header
        typer.echo("ID              NAME    STATUS")
        typer.echo("─────────────── ──────  ──────────")

        # Add speaker rows
        from src.utils import data_handler

        for speaker in speakers:
            speaker_path = data_handler.DATA_FOLDER / "speakers" / speaker.speaker_id
            sections_file = speaker_path / "sections.json"
            ready_status = "Ready" if sections_file.exists() else "Not Ready"

            # Format with proper spacing to align columns
            typer.echo(f"{speaker.speaker_id:<15} {speaker.name:<6}  {ready_status}")

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
        resolved_speaker = validate_speaker_resolution(resolved_speaker, speaker)

        # Check if speaker is ready (sections.json exists)
        from src.utils import data_handler

        speaker_path = (
            data_handler.DATA_FOLDER / "speakers" / resolved_speaker.speaker_id
        )
        sections_file = speaker_path / "sections.json"
        status = "Ready" if sections_file.exists() else "Not Ready"

        # Display speaker details in Direct Summary format
        typer.echo(
            f"Showing details for speaker '{resolved_speaker.name}' ({resolved_speaker.speaker_id})"
        )
        typer.echo(f"    ID -> {resolved_speaker.speaker_id}")
        typer.echo(f"    Name -> {resolved_speaker.name}")
        typer.echo(f"    Status -> {status}")
        typer.echo(f"    Presentation -> {resolved_speaker.source_presentation}")
        typer.echo(f"    Transcript -> {resolved_speaker.source_transcript}")

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in the generic handler
        raise
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


@speaker_app.command("process")
def speaker_process(
    speakers: Optional[list[str]] = typer.Argument(None, help="Speaker(s) to process"),
    all: bool = typer.Option(False, "--all", "-a", help="Process all speakers"),
):
    """Generate presentation sections using AI for live control (requires model and API key)"""
    try:
        # Create speaker manager and settings editor instances
        speaker_manager = speaker_manager_instance()
        settings_editor = settings_editor_instance()

        # Get LLM configuration from settings
        settings = settings_editor.list()

        # Validate LLM settings are configured
        if not settings.model:
            typer.echo(
                "Error: LLM model not configured. Use 'moves settings set model <model>' to configure.",
                err=True,
            )
            raise typer.Exit(1)

        if not settings.key:
            typer.echo(
                "Error: LLM API key not configured. Use 'moves settings set key <key>' to configure.",
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
                resolved = validate_speaker_resolution(resolved, speaker_name)
                speaker_list.append(resolved)
        else:
            typer.echo(
                "Error: Either provide speaker names or use --all to process all speakers.",
                err=True,
            )
            raise typer.Exit(1)

        # Display processing message
        if len(speaker_list) == 1:
            typer.echo(
                f"Processing speaker '{speaker_list[0].name}' ({speaker_list[0].speaker_id})..."
            )
        else:
            typer.echo(f"Processing {len(speaker_list)} speakers...")

        # Call speaker_manager.process with resolved speakers
        results = speaker_manager.process(speaker_list, settings.model, settings.key)

        # Display results in Direct Summary format
        if len(speaker_list) == 1:
            result = results[0]
            speaker = speaker_list[0]
            typer.echo(f"Speaker '{speaker.name}' ({speaker.speaker_id}) processed.")
            typer.echo(f"    {result.section_count} sections created.")
        else:
            typer.echo(f"{len(speaker_list)} speakers processed.")
            for i, result in enumerate(results):
                speaker = speaker_list[i]
                typer.echo(
                    f"    '{speaker.name}' ({speaker.speaker_id}) -> {result.section_count} sections created."
                )

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in the generic handler
        raise
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
        resolved_speaker = validate_speaker_resolution(resolved_speaker, speaker)

        # Delete speaker
        success = speaker_manager.delete(resolved_speaker)

        if success:
            typer.echo(
                f"Speaker '{resolved_speaker.name}' ({resolved_speaker.speaker_id}) deleted."
            )
        else:
            typer.echo(f"Could not delete speaker '{resolved_speaker.name}'.", err=True)
            typer.echo("    Failed to delete speaker data.", err=True)
            raise typer.Exit(1)

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in the generic handler
        raise
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


# =============================================================================
# PRESENTATION COMMANDS
# =============================================================================
@presentation_app.command("control")
def presentation_control(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
    """Start live voice-controlled presentation navigation (requires processed speaker)"""
    try:
        import json
        from src.utils import data_handler
        from src.core.components import section_producer

        # Create speaker manager instance
        speaker_manager = speaker_manager_instance()

        # Resolve speaker
        resolved_speaker = speaker_manager.resolve(speaker)
        resolved_speaker = validate_speaker_resolution(resolved_speaker, speaker)

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
            typer.echo(
                "Please run 'moves speaker process' first to generate sections.",
                err=True,
            )
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

        controller = presentation_controller_instance(sections, start_section)

        typer.echo(
            f"Starting presentation control for '{resolved_speaker.name}' ({resolved_speaker.speaker_id})."
        )
        typer.echo(f"    {len(sections)} sections loaded")
        typer.echo("    READY & LISTENING\n")
        typer.echo("    Press Ctrl+C to exit.")
        typer.echo("    \nWaiting for 12 words to first trigger, keep speaking...\n")

        controller.control()

    except KeyboardInterrupt:
        typer.echo("\nPresentation control stopped.")
    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in the generic handler
        raise
    except Exception as e:
        typer.echo(f"Presentation control error: {str(e)}", err=True)
        raise typer.Exit(1)


# =============================================================================
# SETTINGS COMMANDS
# =============================================================================
@settings_app.command("list")
def settings_list():
    """Display current system configuration (model, API key status)"""
    try:
        # Create settings editor instance
        settings_editor = settings_editor_instance()
        settings = settings_editor.list()

        # Display settings in Direct Summary format
        typer.echo("Application Settings.")

        # Display model setting
        model_value = settings.model if settings.model else "Not configured"
        typer.echo(f"    model (LLM Model) -> {model_value}")

        # Display API key setting (masked)
        if settings.key:
            masked_key = (
                settings.key[:8] + "..." + settings.key[-4:]
                if len(settings.key) > 12
                else "***"
            )
            typer.echo(f"    key (API Key) -> {masked_key}")
        else:
            typer.echo("    key (API Key) -> Not configured")

    except Exception as e:
        typer.echo(f"Error accessing settings: {str(e)}", err=True)
        raise typer.Exit(1)


@settings_app.command("set")
def settings_set(
    key: str = typer.Argument(..., help="Setting name to update"),
    value: str = typer.Argument(..., help="New setting value"),
):
    """Configure system settings: model (LLM model name) or key (API key)"""
    try:
        # Create settings editor instance
        settings_editor = settings_editor_instance()

        # Valid setting keys
        valid_keys = ["model", "key"]

        if key not in valid_keys:
            typer.echo(f"Error: Invalid setting key '{key}'", err=True)
            typer.echo(f"Valid keys: {', '.join(valid_keys)}", err=True)
            raise typer.Exit(1)

        # Update setting
        success = settings_editor.set(key, value)

        if success:
            # Display confirmation in Direct Summary format (mask API key in output)
            if key == "key":
                display_value = (
                    value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                )
                typer.echo(f"Setting '{key}' updated.")
                typer.echo(f"    New Value -> {display_value}")
            else:
                typer.echo(f"Setting '{key}' updated.")
                typer.echo(f"    New Value -> {value}")
        else:
            typer.echo(f"Could not update setting '{key}'.", err=True)
            raise typer.Exit(1)

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in the generic handler
        raise
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


@settings_app.command("unset")
def settings_unset(
    key: str = typer.Argument(..., help="Setting name to reset"),
):
    """Reset a setting to its default value (model: gemini/gemini-2.0-flash, key: null)"""
    try:
        # Create settings editor instance
        settings_editor = settings_editor_instance()

        # Check if key exists in template
        valid_keys = ["model", "key"]
        if key not in valid_keys:
            typer.echo(f"Error: Invalid setting key '{key}'", err=True)
            typer.echo(f"Valid keys: {', '.join(valid_keys)}", err=True)
            raise typer.Exit(1)

        # Get the template value to show what it will be reset to
        template_value = settings_editor.template_data.get(key)

        # Reset setting
        success = settings_editor.unset(key)

        if success:
            # Display confirmation in Direct Summary format
            if key in settings_editor.template_data:
                if (
                    key == "key"
                    and template_value
                    and template_value != "null"
                    and template_value is not None
                ):
                    display_value = (
                        str(template_value)[:8] + "..." + str(template_value)[-4:]
                        if len(str(template_value)) > 12
                        else "***"
                    )
                    typer.echo(f"Setting '{key}' reset to default.")
                    typer.echo(f"    New Value -> {display_value}")
                else:
                    display_value = (
                        "Not configured"
                        if template_value is None
                        else str(template_value)
                    )
                    typer.echo(f"Setting '{key}' reset to default.")
                    typer.echo(f"    New Value -> {display_value}")
            else:
                # Key was removed (not in template)
                typer.echo(f"Setting '{key}' reset to default.")
                typer.echo("    New Value -> Not configured")
        else:
            typer.echo(f"Could not reset setting '{key}'.", err=True)
            raise typer.Exit(1)

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in the generic handler
        raise
    except Exception as e:
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(1)


# =============================================================================
# APPLICATION SETUP
# =============================================================================

# Register subcommands
app.add_typer(speaker_app, name="speaker")
app.add_typer(presentation_app, name="presentation")
app.add_typer(settings_app, name="settings")


if __name__ == "__main__":
    app()
