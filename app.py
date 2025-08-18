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
    from core.speaker_manager import SpeakerManager

    return SpeakerManager()


def presentation_controller_instance(
    sections: list[Section], start_section: Section, selected_mic: int | None = None
):
    from core.presentation_controller import PresentationController

    return PresentationController(
        sections=sections,
        start_section=start_section,
        window_size=12,
        selected_mic=selected_mic,
    )


def settings_editor_instance():
    from core.settings_editor import SettingsEditor

    return SettingsEditor()


# SPEAKER COMMANDS
@speaker_app.command("add")
def speaker_add(
    name: str = typer.Argument(..., help="Speaker's name"),
    source_presentation: Path = typer.Argument(..., help="Path to presentation file"),
    source_transcript: Path = typer.Argument(..., help="Path to transcript file"),
):
    """Create a new speaker profile"""


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


@speaker_app.command("list")
def speaker_list():
    """List all registered speakers"""


@speaker_app.command("show")
def speaker_show(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
    """Display detailed speaker information"""


@speaker_app.command("process")
def speaker_process(
    speakers: str = typer.Argument(..., help="Speaker(s) to process"),
    all: bool = typer.Option(False, "--all", "-a", help="Process all speakers"),
):
    """Prepare speakers for live presentation control"""


@speaker_app.command("delete")
def speaker_delete(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
    """Remove a speaker and their data"""


# PRESENTATION COMMANDS
@presentation_app.command("control")
def presentation_control(
    speaker: str = typer.Argument(..., help="Speaker name or ID"),
):
    """Start live control of a speaker's presentation"""


# SETTINGS COMMANDS
@settings_app.command("list")
def settings_list():
    """Show all current application settings"""


@settings_app.command("set")
def settings_set(
    key: str = typer.Argument(..., help="Setting name to update"),
    value: str = typer.Argument(..., help="New setting value"),
):
    """Change the value of an application setting"""


@settings_app.command("unset")
def settings_unset(
    key: str = typer.Argument(..., help="Setting name to reset"),
):
    """Reset a setting to its default value"""


# Register subcommands
app.add_typer(speaker_app, name="speaker")
app.add_typer(presentation_app, name="presentation")
app.add_typer(settings_app, name="settings")

if __name__ == "__main__":
    app()
