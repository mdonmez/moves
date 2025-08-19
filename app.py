from typing import Optional
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.data.models import Section

# Initialize Rich console
console = Console()


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
            console.print(
                f"[red]Error: No speaker found matching '{speaker_name}'[/red]"
            )
            raise typer.Exit(1)
        elif len(resolved_speaker) > 1:
            console.print(
                f"[red]Error: Multiple speakers found matching '{speaker_name}'. Be more specific:[/red]"
            )
            for s in resolved_speaker:
                console.print(f"[yellow]  - {s.name} ({s.speaker_id})[/yellow]")
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
    try:
        # Validate that both file paths exist and are accessible
        if not source_presentation.exists():
            console.print(
                f"[red]Error: Presentation file not found: {source_presentation}[/red]"
            )
            raise typer.Exit(1)

        if not source_transcript.exists():
            console.print(
                f"[red]Error: Transcript file not found: {source_transcript}[/red]"
            )
            raise typer.Exit(1)

        # Create speaker manager instance and add speaker
        speaker_manager = speaker_manager_instance()
        speaker = speaker_manager.add(name, source_presentation, source_transcript)

        # Display success message with created speaker information
        console.print(
            "\n[bold green]✓ Speaker profile created successfully:[/bold green]"
        )
        console.print(f"[cyan]  Name:[/cyan] {speaker.name}")
        console.print(f"[cyan]  Speaker ID:[/cyan] {speaker.speaker_id}")
        console.print(f"[cyan]  Presentation:[/cyan] {speaker.source_presentation}")
        console.print(f"[cyan]  Transcript:[/cyan] {speaker.source_transcript}")
        console.print()

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
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
    try:
        # Validate at least one update parameter is provided
        if not source_presentation and not source_transcript:
            console.print(
                "[red]Error: At least one update parameter (--presentation or --transcript) must be provided[/red]"
            )
            raise typer.Exit(1)

        # Create speaker manager instance and resolve speaker
        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)
        resolved_speaker = validate_speaker_resolution(resolved_speaker, speaker)

        # Convert string paths to Path objects and validate
        presentation_path = Path(source_presentation) if source_presentation else None
        transcript_path = Path(source_transcript) if source_transcript else None

        if presentation_path and not presentation_path.exists():
            console.print(
                f"[red]Error: Presentation file not found: {presentation_path}[/red]"
            )
            raise typer.Exit(1)

        if transcript_path and not transcript_path.exists():
            console.print(
                f"[red]Error: Transcript file not found: {transcript_path}[/red]"
            )
            raise typer.Exit(1)

        # Update speaker
        updated_speaker = speaker_manager.edit(
            resolved_speaker, presentation_path, transcript_path
        )

        # Display updated speaker information
        console.print(
            "\n[bold green]✓ Speaker profile updated successfully:[/bold green]"
        )
        console.print(f"[cyan]  Name:[/cyan] {updated_speaker.name}")
        console.print(f"[cyan]  Speaker ID:[/cyan] {updated_speaker.speaker_id}")
        console.print(
            f"[cyan]  Presentation:[/cyan] {updated_speaker.source_presentation}"
        )
        console.print(f"[cyan]  Transcript:[/cyan] {updated_speaker.source_transcript}")
        console.print()

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)


@speaker_app.command("list")
def speaker_list():
    """List all registered speakers with ready status"""
    try:
        # Create speaker manager instance and get all speakers
        speaker_manager = speaker_manager_instance()
        speakers = speaker_manager.list()

        if not speakers:
            console.print("[yellow]No speakers found.[/yellow]")
            return

        # Create table for better formatting
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Speaker ID", style="cyan", width=15)
        table.add_column("Name", style="magenta", width=20)
        table.add_column("Ready", style="green", width=10)

        # Add speaker rows
        from src.utils import data_handler

        for speaker in speakers:
            speaker_path = data_handler.DATA_FOLDER / "speakers" / speaker.speaker_id
            sections_file = speaker_path / "sections.json"
            ready_status = (
                "[green]✓ Yes[/green]" if sections_file.exists() else "[red]✗ No[/red]"
            )

            table.add_row(speaker.speaker_id, speaker.name, ready_status)

        console.print(
            Panel(table, title="[bold]Registered Speakers[/bold]", border_style="blue")
        )
        console.print(f"[dim]Total speakers: {len(speakers)}[/dim]")

    except Exception as e:
        console.print(f"[red]Error accessing speaker data: {str(e)}[/red]")
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

        # Get paths for local files
        from src.utils import data_handler

        speaker_path = (
            data_handler.DATA_FOLDER / "speakers" / resolved_speaker.speaker_id
        )
        local_presentation = speaker_path / "presentation.pdf"
        local_transcript = speaker_path / "transcript.pdf"

        # Create file status table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("File Type", style="cyan", width=12)
        table.add_column("Source Path", style="white", width=50)
        table.add_column("Status", style="green", width=12)
        table.add_column("Local Path", style="white", width=50)
        table.add_column("Local Status", style="green", width=12)

        # Source files information
        pres_exists = (
            "[green]✓ EXISTS[/green]"
            if resolved_speaker.source_presentation.exists()
            else "[red]✗ NOT FOUND[/red]"
        )
        trans_exists = (
            "[green]✓ EXISTS[/green]"
            if resolved_speaker.source_transcript.exists()
            else "[red]✗ NOT FOUND[/red]"
        )
        local_pres_exists = (
            "[green]✓ EXISTS[/green]"
            if local_presentation.exists()
            else "[red]✗ NOT FOUND[/red]"
        )
        local_trans_exists = (
            "[green]✓ EXISTS[/green]"
            if local_transcript.exists()
            else "[red]✗ NOT FOUND[/red]"
        )

        table.add_row(
            "Presentation",
            str(resolved_speaker.source_presentation),
            pres_exists,
            str(local_presentation),
            local_pres_exists,
        )
        table.add_row(
            "Transcript",
            str(resolved_speaker.source_transcript),
            trans_exists,
            str(local_transcript),
            local_trans_exists,
        )

        # Display speaker details
        console.print("\n[bold blue]Speaker Details[/bold blue]")
        console.print(f"[cyan]Name:[/cyan] {resolved_speaker.name}")
        console.print(f"[cyan]Speaker ID:[/cyan] {resolved_speaker.speaker_id}")
        console.print()
        console.print(
            Panel(table, title="[bold]File Information[/bold]", border_style="blue")
        )

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
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
            console.print(
                "[red]Error: LLM model not configured. Use 'moves settings set model <model>' to configure.[/red]"
            )
            raise typer.Exit(1)

        if not settings.key:
            console.print(
                "[red]Error: LLM API key not configured. Use 'moves settings set key <key>' to configure.[/red]"
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
            console.print(
                "[red]Error: Either provide speaker names or use --all to process all speakers.[/red]"
            )
            raise typer.Exit(1)

        # Display processing start message with Rich
        with console.status(
            f"[bold blue]Processing {len(speaker_list)} speaker(s) with {settings.model}...",
            spinner="dots",
        ):
            # Call speaker_manager.process with resolved speakers
            results = speaker_manager.process(
                speaker_list, settings.model, settings.key
            )

        # Display processing results with Rich
        console.print("\n[bold green]✓ Processing completed successfully[/bold green]")

        # Create results table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Speaker", style="cyan", width=25)
        table.add_column("Sections", style="green", width=10)
        table.add_column("Transcript", style="yellow", width=12)
        table.add_column("Presentation", style="magenta", width=12)

        for i, result in enumerate(results):
            speaker = speaker_list[i]
            table.add_row(
                f"{speaker.name} ({speaker.speaker_id})",
                str(result.section_count),
                result.transcript_from,
                result.presentation_from,
            )

        console.print(
            Panel(table, title="[bold]Processing Results[/bold]", border_style="green")
        )

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Processing error: {str(e)}[/red]")
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

        # Display confirmation and delete
        console.print(
            f"\n[yellow]Deleting speaker: {resolved_speaker.name} ({resolved_speaker.speaker_id})[/yellow]"
        )

        success = speaker_manager.delete(resolved_speaker)

        if success:
            console.print(
                "[green]✓ Speaker and associated data deleted successfully[/green]"
            )
        else:
            console.print("[red]Error: Failed to delete speaker data.[/red]")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
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
            console.print(
                f"[red]Error: Speaker '{resolved_speaker.name}' has not been processed yet.[/red]"
            )
            console.print(
                "[yellow]Please run 'moves speaker process' first to generate sections.[/yellow]"
            )
            raise typer.Exit(1)

        # Load sections data
        try:
            sections_data = json.loads(data_handler.read(sections_file))
            sections = section_producer.convert_to_objects(sections_data)
        except Exception as e:
            console.print(f"[red]Error: Failed to load sections data: {str(e)}[/red]")
            raise typer.Exit(1)

        if not sections:
            console.print("[red]Error: No sections found in processed data.[/red]")
            raise typer.Exit(1)

        # Determine starting section (first section)
        start_section = sections[0]

        # Create and start presentation controller
        console.print(
            f"\n[bold green]Starting presentation control for: {resolved_speaker.name}[/bold green]"
        )
        console.print(f"[cyan]Loaded {len(sections)} sections[/cyan]")
        console.print("[dim]Using default microphone[/dim]")
        console.print("═" * 50)

        controller = presentation_controller_instance(sections, start_section)
        controller.control()

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Presentation control stopped.[/yellow]")
    except Exception as e:
        console.print(f"[red]Presentation control error: {str(e)}[/red]")
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

        # Create settings table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Setting", style="cyan", width=15)
        table.add_column("Value", style="green", width=30)
        table.add_column("Status", style="yellow", width=15)

        # Add model setting
        model_value = settings.model if settings.model else "[dim]Not configured[/dim]"
        model_status = (
            "[green]✓ Set[/green]" if settings.model else "[red]✗ Missing[/red]"
        )
        table.add_row("Model", model_value, model_status)

        # Add API key setting (masked)
        if settings.key:
            masked_key = (
                settings.key[:8] + "..." + settings.key[-4:]
                if len(settings.key) > 12
                else "***"
            )
            key_status = "[green]✓ Set[/green]"
        else:
            masked_key = "[dim]Not configured[/dim]"
            key_status = "[red]✗ Missing[/red]"
        table.add_row("API Key", masked_key, key_status)

        console.print(
            Panel(table, title="[bold]Application Settings[/bold]", border_style="blue")
        )

    except Exception as e:
        console.print(f"[red]Error accessing settings: {str(e)}[/red]")
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
            console.print(f"[red]Error: Invalid setting key '{key}'[/red]")
            console.print(f"[yellow]Valid keys: {', '.join(valid_keys)}[/yellow]")
            raise typer.Exit(1)

        # Update setting
        success = settings_editor.set(key, value)

        if success:
            # Display confirmation (mask API key in output)
            if key == "key":
                display_value = (
                    value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                )
                console.print(
                    f"[green]✓ Setting updated: {key} = {display_value}[/green]"
                )
            else:
                console.print(f"[green]✓ Setting updated: {key} = {value}[/green]")
        else:
            console.print(f"[red]Error: Failed to update setting '{key}'[/red]")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
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
            console.print(f"[red]Error: Invalid setting key '{key}'[/red]")
            console.print(f"[yellow]Valid keys: {', '.join(valid_keys)}[/yellow]")
            raise typer.Exit(1)

        # Get the template value to show what it will be reset to
        template_value = settings_editor.template_data.get(key)

        # Reset setting
        success = settings_editor.unset(key)

        if success:
            if key in settings_editor.template_data:
                # Display confirmation showing the reset value
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
                    console.print(
                        f"[green]✓ Setting reset: {key} = {display_value} (default)[/green]"
                    )
                else:
                    display_value = (
                        "Not configured"
                        if template_value is None
                        else str(template_value)
                    )
                    console.print(
                        f"[green]✓ Setting reset: {key} = {display_value} (default)[/green]"
                    )
            else:
                # Key was removed (not in template)
                console.print(f"[green]✓ Setting removed: {key}[/green]")
        else:
            console.print(f"[red]Error: Failed to reset setting '{key}'[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
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
