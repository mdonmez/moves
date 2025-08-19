from typing import Optional
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from src.data.models import Section

console = Console()

# Initialize Typer CLI application
app = typer.Typer(
    help="""
    moves CLI: Presentation control, reimagined.

    This tool helps you manage speaker profiles, process their presentation
    materials, and control live presentations with voice commands.
    """,
    add_completion=False,
    rich_markup_mode="rich",
)

# Subcommands for speaker, presentation, and settings management
speaker_app = typer.Typer(
    help="Manage speaker profiles, files, and processing.", name="speaker"
)
presentation_app = typer.Typer(
    help="Control a speaker's presentation in real-time.", name="presentation"
)
settings_app = typer.Typer(
    help="Configure application settings, like API keys and models.", name="settings"
)


def speaker_manager_instance():
    from src.core.speaker_manager import SpeakerManager

    return SpeakerManager()


def presentation_controller_instance(sections: list[Section], start_section: Section):
    from src.core.presentation_controller import PresentationController

    return PresentationController(
        sections=sections, start_section=start_section, window_size=12
    )


def settings_editor_instance():
    from src.core.settings_editor import SettingsEditor

    return SettingsEditor()


# SPEAKER COMMANDS
@speaker_app.command("add", help="Create a new speaker profile.")
def speaker_add(
    name: str = typer.Argument(..., help="The speaker's name for identification."),
    source_presentation: Path = typer.Argument(
        ..., help="Path to the presentation file (e.g., PDF)."
    ),
    source_transcript: Path = typer.Argument(
        ..., help="Path to the transcript file (e.g., PDF)."
    ),
):
    try:
        if not source_presentation.exists():
            console.print(
                f"[bold red]Error:[/bold red] Presentation file not found: {source_presentation}"
            )
            raise typer.Exit(1)

        if not source_transcript.exists():
            console.print(
                f"[bold red]Error:[/bold red] Transcript file not found: {source_transcript}"
            )
            raise typer.Exit(1)

        speaker_manager = speaker_manager_instance()
        speaker = speaker_manager.add(name, source_presentation, source_transcript)

        console.print("\n[bold green]✓ Speaker profile created successfully:[/bold green]")
        console.print(f"  [bold]Name:[/bold] {speaker.name}")
        console.print(f"  [bold]Speaker ID:[/bold] {speaker.speaker_id}")
        console.print(f"  [bold]Presentation:[/bold] {speaker.source_presentation}")
        console.print(f"  [bold]Transcript:[/bold] {speaker.source_transcript}")
        console.print()

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@speaker_app.command(
    "edit", help="Update a speaker's source presentation or transcript file."
)
def speaker_edit(
    speaker: str = typer.Argument(..., help="The name or ID of the speaker to edit."),
    source_presentation: Optional[str] = typer.Option(
        None,
        "--presentation",
        "-p",
        help="Path to the new presentation file.",
        show_default=False,
    ),
    source_transcript: Optional[str] = typer.Option(
        None,
        "--transcript",
        "-t",
        help="Path to the new transcript file.",
        show_default=False,
    ),
):
    try:
        if not source_presentation and not source_transcript:
            console.print(
                "[bold red]Error:[/bold red] Please provide a new file path for either --presentation or --transcript."
            )
            raise typer.Exit(1)

        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)

        if isinstance(resolved_speaker, list):
            if not resolved_speaker:
                console.print(
                    f"[bold red]Error:[/bold red] No speaker found matching '{speaker}'."
                )
                raise typer.Exit(1)
            else:
                console.print(
                    f"[bold yellow]Warning:[/bold yellow] Multiple speakers found for '{speaker}'. Please be more specific."
                )
                for s in resolved_speaker:
                    console.print(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)

        presentation_path = Path(source_presentation) if source_presentation else None
        transcript_path = Path(source_transcript) if source_transcript else None

        if presentation_path and not presentation_path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Presentation file not found: {presentation_path}"
            )
            raise typer.Exit(1)

        if transcript_path and not transcript_path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Transcript file not found: {transcript_path}"
            )
            raise typer.Exit(1)

        updated_speaker = speaker_manager.edit(
            resolved_speaker, presentation_path, transcript_path
        )

        console.print("\n[bold green]✓ Speaker profile updated successfully:[/bold green]")
        console.print(f"  [bold]Name:[/bold] {updated_speaker.name}")
        console.print(f"  [bold]Speaker ID:[/bold] {updated_speaker.speaker_id}")
        console.print(
            f"  [bold]Presentation:[/bold] {updated_speaker.source_presentation}"
        )
        console.print(f"  [bold]Transcript:[/bold] {updated_speaker.source_transcript}")
        console.print()

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@speaker_app.command("list", help="List all registered speakers and their status.")
def speaker_list():
    try:
        from src.utils import data_handler

        speaker_manager = speaker_manager_instance()
        speakers = speaker_manager.list()

        if not speakers:
            console.print("[yellow]No speakers found.[/yellow]")
            return

        table = Table(
            title="[bold]Registered Speakers[/bold]",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Speaker ID", style="cyan", width=15)
        table.add_column("Name", style="green", width=25)
        table.add_column("Ready", justify="center", width=10)

        for speaker in speakers:
            speaker_path = (
                data_handler.DATA_FOLDER / "speakers" / speaker.speaker_id
            )
            is_ready = (speaker_path / "sections.json").exists()
            status = "[bold green]✓ Yes[/bold green]" if is_ready else "[bold red]✗ No[/bold red]"
            table.add_row(speaker.speaker_id, speaker.name, status)

        console.print(table)
        console.print(f"\nTotal speakers: {len(speakers)}")

    except Exception as e:
        console.print(f"[bold red]Error accessing speaker data:[/bold red] {e}")
        raise typer.Exit(1)


@speaker_app.command(
    "show", help="Display detailed information about a specific speaker."
)
def speaker_show(
    speaker: str = typer.Argument(..., help="The name or ID of the speaker to show."),
):
    try:
        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)

        if isinstance(resolved_speaker, list):
            if not resolved_speaker:
                console.print(
                    f"[bold red]Error:[/bold red] No speaker found matching '{speaker}'."
                )
                raise typer.Exit(1)
            else:
                console.print(
                    f"[bold yellow]Warning:[/bold yellow] Multiple speakers found for '{speaker}'. Please be more specific."
                )
                for s in resolved_speaker:
                    console.print(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)

        from src.utils import data_handler

        speaker_path = (
            data_handler.DATA_FOLDER / "speakers" / resolved_speaker.speaker_id
        )
        local_presentation = speaker_path / "presentation.pdf"
        local_transcript = speaker_path / "transcript.pdf"

        def get_status(path: Path):
            return (
                "[bold green]✓ Exists[/bold green]"
                if path.exists()
                else "[bold red]✗ Not Found[/bold red]"
            )

        console.print(f"\n[bold]Speaker Details for '{resolved_speaker.name}'[/bold]")
        console.print(f"  [bold]Speaker ID:[/bold] {resolved_speaker.speaker_id}")

        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("File Type", style="cyan")
        table.add_column("Path")
        table.add_column("Status", justify="right")

        table.add_row(
            "[bold]Source Presentation[/bold]",
            str(resolved_speaker.source_presentation),
            get_status(resolved_speaker.source_presentation),
        )
        table.add_row(
            "[bold]Source Transcript[/bold]",
            str(resolved_speaker.source_transcript),
            get_status(resolved_speaker.source_transcript),
        )
        table.add_row()
        table.add_row(
            "[bold]Local Presentation[/bold]",
            str(local_presentation),
            get_status(local_presentation),
        )
        table.add_row(
            "[bold]Local Transcript[/bold]",
            str(local_transcript),
            get_status(local_transcript),
        )

        console.print(table)

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@speaker_app.command(
    "process",
    help="Generate presentation sections from source files using an LLM.",
)
def speaker_process(
    speakers: Optional[list[str]] = typer.Argument(
        None, help="A list of speaker names or IDs to process."
    ),
    all: bool = typer.Option(
        False, "--all", "-a", help="Process all registered speakers."
    ),
):
    try:
        speaker_manager = speaker_manager_instance()
        settings_editor = settings_editor_instance()
        settings = settings_editor.list()

        if not settings.model:
            console.print(
                "[bold red]Error:[/bold red] LLM model not configured. Use 'moves settings set model <model_name>' to set it."
            )
            raise typer.Exit(1)

        if not settings.key:
            console.print(
                "[bold red]Error:[/bold red] LLM API key not configured. Use 'moves settings set key <api_key>' to set it."
            )
            raise typer.Exit(1)

        if all:
            speaker_list = speaker_manager.list()
            if not speaker_list:
                console.print("[yellow]No speakers found to process.[/yellow]")
                return
        elif speakers:
            speaker_list = []
            for speaker_name in speakers:
                resolved = speaker_manager.resolve(speaker_name)
                if isinstance(resolved, list):
                    if not resolved:
                        console.print(
                            f"[bold red]Error:[/bold red] No speaker found matching '{speaker_name}'."
                        )
                        raise typer.Exit(1)
                    else:
                        console.print(
                            f"[bold yellow]Warning:[/bold yellow] Multiple speakers found for '{speaker_name}'. Please be more specific."
                        )
                        for s in resolved:
                            console.print(f"  - {s.name} ({s.speaker_id})")
                        raise typer.Exit(1)
                else:
                    speaker_list.append(resolved)
        else:
            console.print(
                "[bold red]Error:[/bold red] You must either provide speaker names or use the --all flag."
            )
            raise typer.Exit(1)

        console.print(
            f"\n[bold]Processing {len(speaker_list)} speaker(s) with [cyan]{settings.model}[/cyan]...[/bold]"
        )

        results = speaker_manager.process(speaker_list, settings.model, settings.key)

        console.print("\n[bold green]✓ Processing completed successfully[/bold green]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Speaker", style="cyan")
        table.add_column("Sections Generated", justify="center")
        table.add_column("Transcript Source", justify="center")
        table.add_column("Presentation Source", justify="center")

        for i, result in enumerate(results):
            speaker = speaker_list[i]
            table.add_row(
                f"{speaker.name} ({speaker.speaker_id})",
                str(result.section_count),
                result.transcript_from,
                result.presentation_from,
            )
        console.print(table)

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Processing error:[/bold red] {e}")
        raise typer.Exit(1)


@speaker_app.command("delete", help="Remove a speaker and all their associated data.")
def speaker_delete(
    speaker: str = typer.Argument(..., help="The name or ID of the speaker to delete."),
):
    try:
        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)

        if isinstance(resolved_speaker, list):
            if not resolved_speaker:
                console.print(
                    f"[bold red]Error:[/bold red] No speaker found matching '{speaker}'."
                )
                raise typer.Exit(1)
            else:
                console.print(
                    f"[bold yellow]Warning:[/bold yellow] Multiple speakers found for '{speaker}'. Please be more specific."
                )
                for s in resolved_speaker:
                    console.print(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)

        console.print(
            f"\n[bold yellow]Permanently deleting speaker: {resolved_speaker.name} ({resolved_speaker.speaker_id})[/bold yellow]"
        )
        if typer.confirm("Are you sure you want to continue?"):
            success = speaker_manager.delete(resolved_speaker)
            if success:
                console.print(
                    "[bold green]✓ Speaker and associated data deleted successfully.[/bold green]\n"
                )
            else:
                console.print(
                    "[bold red]Error:[/bold red] Failed to delete speaker data."
                )
                raise typer.Exit(1)
        else:
            console.print("Deletion cancelled.")

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


# PRESENTATION COMMANDS
@presentation_app.command(
    "control", help="Start the live presentation control for a speaker."
)
def presentation_control(
    speaker: str = typer.Argument(..., help="The name or ID of the speaker to control."),
):
    try:
        import json
        from src.utils import data_handler
        from src.core.components import section_producer

        speaker_manager = speaker_manager_instance()
        resolved_speaker = speaker_manager.resolve(speaker)

        if isinstance(resolved_speaker, list):
            if not resolved_speaker:
                console.print(
                    f"[bold red]Error:[/bold red] No speaker found matching '{speaker}'."
                )
                raise typer.Exit(1)
            else:
                console.print(
                    f"[bold yellow]Warning:[/bold yellow] Multiple speakers found for '{speaker}'. Please be more specific."
                )
                for s in resolved_speaker:
                    console.print(f"  - {s.name} ({s.speaker_id})")
                raise typer.Exit(1)

        speaker_path = (
            data_handler.DATA_FOLDER / "speakers" / resolved_speaker.speaker_id
        )
        sections_file = speaker_path / "sections.json"

        if not sections_file.exists():
            console.print(
                f"[bold red]Error:[/bold red] Speaker '{resolved_speaker.name}' has not been processed."
            )
            console.print(
                "Please run [bold]'moves speaker process'[/bold] first to generate presentation sections."
            )
            raise typer.Exit(1)

        try:
            sections_data = json.loads(data_handler.read(sections_file))
            sections = section_producer.convert_to_objects(sections_data)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to load sections data: {e}")
            raise typer.Exit(1)

        if not sections:
            console.print(
                "[bold red]Error:[/bold red] No sections found in the processed data."
            )
            raise typer.Exit(1)

        start_section = sections[0]

        console.print(
            f"\n[bold]Starting presentation control for: [green]{resolved_speaker.name}[/green][/bold]"
        )
        console.print(f"  [cyan]Loaded {len(sections)} sections.[/cyan]")
        console.print("  [cyan]Using default microphone.[/cyan]")
        console.print("─" * 50)

        controller = presentation_controller_instance(sections, start_section)
        controller.control()

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Presentation control stopped by user.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Presentation control error:[/bold red] {e}")
        raise typer.Exit(1)


# SETTINGS COMMANDS
@settings_app.command("list", help="Show all current application settings.")
def settings_list():
    """Show all current application settings"""
    try:
        settings_editor = settings_editor_instance()
        settings = settings_editor.list()

        table = Table(
            title="[bold]Application Settings[/bold]",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Setting", style="cyan", width=20)
        table.add_column("Value", style="green")

        table.add_row(
            "LLM Model", settings.model if settings.model else "[yellow]Not set[/yellow]"
        )

        if settings.key:
            masked_key = (
                f"{settings.key[:8]}...{settings.key[-4:]}"
                if len(settings.key) > 12
                else "***"
            )
            table.add_row("LLM API Key", masked_key)
        else:
            table.add_row("LLM API Key", "[yellow]Not set[/yellow]")

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error accessing settings:[/bold red] {e}")
        raise typer.Exit(1)


@settings_app.command("set", help="Change the value of an application setting.")
def settings_set(
    key: str = typer.Argument(..., help="The setting to update (e.g., 'model', 'key')."),
    value: str = typer.Argument(..., help="The new value for the setting."),
):
    try:
        settings_editor = settings_editor_instance()
        valid_keys = ["model", "key"]

        if key not in valid_keys:
            console.print(
                f"[bold red]Error:[/bold red] Invalid setting key '{key}'. Valid keys are: {', '.join(valid_keys)}"
            )
            raise typer.Exit(1)

        success = settings_editor.set(key, value)

        if success:
            display_value = value
            if key == "key":
                display_value = (
                    f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                )
            console.print(
                f"[bold green]✓ Setting updated:[/bold green] {key} = {display_value}"
            )
        else:
            console.print(f"[bold red]Error:[/bold red] Failed to update setting '{key}'.")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@settings_app.command("unset", help="Reset a setting to its default value.")
def settings_unset(
    key: str = typer.Argument(
        ..., help="The setting to reset to default (e.g., 'model', 'key')."
    ),
):
    try:
        settings_editor = settings_editor_instance()
        valid_keys = ["model", "key"]
        if key not in valid_keys:
            console.print(
                f"[bold red]Error:[/bold red] Invalid setting key '{key}'. Valid keys are: {', '.join(valid_keys)}"
            )
            raise typer.Exit(1)

        template_value = settings_editor.template_data.get(key)
        success = settings_editor.unset(key)

        if success:
            display_value = (
                "[yellow]Not set[/yellow]"
                if template_value is None
                else str(template_value)
            )
            console.print(
                f"[bold green]✓ Setting reset:[/bold green] {key} = {display_value} (default)"
            )
        else:
            console.print(f"[bold red]Error:[/bold red] Failed to reset setting '{key}'.")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


# Register subcommands
app.add_typer(speaker_app)
app.add_typer(presentation_app)
app.add_typer(settings_app)

if __name__ == "__main__":
    app()
