"""QUANT CLI 3.0 — Entry point."""
from __future__ import annotations
import asyncio
import typer
from quant.core.config import QuantConfig
from quant.ui import renderer

app = typer.Typer(name="quant", help="QUANT CLI 3.0 — Your AI. Your Rules. Your Data stays with you.", add_completion=False)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    mode: str = typer.Option(None, "--mode", "-m"),
    model: str = typer.Option(None, "--model"),
    provider: str = typer.Option(None, "--provider", "-p"),
    classic: bool = typer.Option(False, "--classic", "-c", help="Use classic REPL instead of TUI"),
):
    if ctx.invoked_subcommand is not None:
        return
    cfg = QuantConfig.load()
    if mode: cfg.mode = mode
    if model: cfg.model = model
    if provider: cfg.provider = provider

    if classic:
        from quant.cli import repl
        asyncio.run(repl(cfg))
    else:
        from quant.cli_tui import run_tui
        run_tui(cfg)


@app.command()
def init():
    renderer.print_banner()
    from pathlib import Path
    import yaml
    from quant.core.config import CONFIG_DIR, CONFIG_FILE, DEFAULT_CONFIG
    CONFIG_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(yaml.dump(DEFAULT_CONFIG, allow_unicode=True), encoding="utf-8")
        renderer.print_success("Created .quant/config.yaml")
    renderer.print_success("Run: quant")


@app.command()
def tui(
    mode: str = typer.Option(None, "--mode", "-m"),
    model: str = typer.Option(None, "--model"),
):
    cfg = QuantConfig.load()
    if mode: cfg.mode = mode
    if model: cfg.model = model
    from quant.cli_tui import run_tui
    run_tui(cfg)


@app.command()
def classic(
    mode: str = typer.Option(None, "--mode", "-m"),
    model: str = typer.Option(None, "--model"),
):
    cfg = QuantConfig.load()
    if mode: cfg.mode = mode
    if model: cfg.model = model
    from quant.cli import repl
    asyncio.run(repl(cfg))


if __name__ == "__main__":
    app()
