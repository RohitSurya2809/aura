from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

import typer
from rich.console import Console
from rich.table import Table

import aura
from aura.application.bootstrap import AuraApplication, create_application
from aura.core.errors import AuraError

if TYPE_CHECKING:
    from uuid import UUID

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
def chat(
    conversation_id: Optional[str] = typer.Option(  # noqa: UP007, UP045
        None,
        "--resume",
        "-r",
        help="Resume an existing conversation by ID.",
    ),
) -> None:
    """Start a new conversation or resume an existing one."""
    try:
        application = create_application()
        asyncio.run(_run_chat(application, conversation_id))
    except AuraError as exc:
        console.print(f"[red]Error:[/red] {exc.message}")
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation ended.[/yellow]")
        raise typer.Exit(code=0) from None
    except Exception as exc:
        console.print(f"[red]Unexpected error:[/red] {exc}")
        raise typer.Exit(code=1) from None


async def _run_chat(
    application: AuraApplication,
    conversation_id: Optional[str],  # noqa: UP007, UP045
) -> None:
    """Run the interactive chat loop."""
    await application.startup()

    try:
        from uuid import UUID

        from aura.application.services.conversation_service import ConversationService
        from aura.application.services.llm_service import LLMService
        from aura.infrastructure.database.repositories import (
            ConversationRepository,
            MessageRepository,
        )
        from aura.infrastructure.providers.gemini import GeminiProvider
        from aura.infrastructure.providers.openrouter import OpenRouterProvider

        async with application.db.session() as session:
            conv_repo = ConversationRepository(session)
            msg_repo = MessageRepository(session)

            # Create LLM service
            from aura.infrastructure.providers.router import ProviderRouter

            # Auto-detect available providers
            primary = None
            fallback = None

            # Prefer OpenRouter if available
            if application.settings.openrouter.is_configured:
                primary = OpenRouterProvider(application.settings.openrouter)
                if application.settings.gemini.is_configured:
                    fallback = GeminiProvider(application.settings.gemini)
            elif application.settings.gemini.is_configured:
                primary = GeminiProvider(application.settings.gemini)
            else:
                raise AuraError(
                    "No LLM provider configured. "
                    "Set AURA_OPENROUTER_API_KEY or AURA_GEMINI_API_KEY"
                )

            router = ProviderRouter(primary=primary, fallback=fallback)
            llm_service = LLMService(router=router)

            conv_service = ConversationService(
                conversation_repo=conv_repo,
                message_repo=msg_repo,
                llm_service=llm_service,
            )

            # Create or resume conversation
            if conversation_id:
                conv_id: UUID = UUID(conversation_id)
                console.print(f"[cyan]Resuming conversation {conv_id}[/cyan]")
            else:
                conv_id = await conv_service.create_conversation(title="Chat Session")
                console.print("[green]New conversation started[/green]")

            # Chat loop
            console.print("[yellow]Type 'exit' to end the conversation[/yellow]\n")

            while True:
                try:
                    user_input = console.input("[cyan]You >[/cyan] ").strip()
                except EOFError:
                    break

                if user_input.lower() == "exit":
                    break

                if not user_input:
                    continue

                console.print("[dim]...[/dim]", end="")

                try:
                    response = await conv_service.send_message(conv_id, user_input)
                    console.print("\r     \r", end="")  # Clear "..." spinner
                    console.print(f"[cyan]Aura >[/cyan] {response}\n")
                except Exception as exc:
                    console.print(f"\n[red]Error:[/red] {exc}")

    finally:
        await application.shutdown()


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
