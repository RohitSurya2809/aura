from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

import aura
from aura.application.bootstrap import AuraApplication, create_application
from aura.core.errors import AuraError

app = typer.Typer(
    name="aura",
    help="Aura — A lightweight, agentic personal AI companion.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"Aura v{aura.__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(  # noqa: UP007, UP045
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Aura — A lightweight, agentic personal AI companion."""


@app.command()
def status() -> None:
    """Check Aura system status (database connectivity, configuration)."""
    try:
        application = create_application()
        result = asyncio.run(_run_status(application))
        _print_status(result)
    except AuraError as exc:
        console.print(f"[red]Error:[/red] {exc.message}")
        raise typer.Exit(code=1) from None
    except Exception as exc:
        console.print(f"[red]Unexpected error:[/red] {exc}")
        raise typer.Exit(code=1) from None


async def _run_status(application: AuraApplication) -> dict[str, object]:
    try:
        await application.startup()
        return await application.health_check()
    finally:
        await application.shutdown()


def _print_status(result: dict[str, object]) -> None:
    table = Table(title="Aura Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")

    for key, value in result.items():
        style = "green" if value in ("healthy", "connected") else "yellow"
        table.add_row(key, str(value), style=style if key != "version" else "")

    console.print(table)
