import os
from pathlib import Path
from typing import Annotated, Optional
from rich.console import Console
import typer

app = typer.Typer(
    name='rme',
    help="remove file by extension",
)

@app.command()
def main(
        path: Annotated[
            Path,
            typer.Argument(
                ...,
                help="Target directory path"),
        ] = Path.cwd(),
        extensions: Annotated[
            Optional[list[str]],
            typer.Argument(help="File extensions to delete (e.g. .log .tmp .bak)"),
        ] = None,
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run", "-d",
                help="Preview files to be deleted without actually deleting",
                is_flag=True,
            )
        ] = False,
):
    console = Console()

    if not os.path.exists(path):
        console.print("[red]The path does not exist![/red]")
        return 0

    if extensions is None:
        console.print("[yellow]No extensions specified (e.g. rme . .log .tmp .bak)[/yellow]")
        return 0

    # Normalize extensions to always start with a dot
    normalized = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    matched_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if any(file.endswith(ext) for ext in normalized):
                matched_files.append(os.path.join(root, file))

    if not matched_files:
        console.print(f"[green]No files found matching extensions: {', '.join(normalized)}[/green]")
        return 0

    for filepath in matched_files:
        if dry_run:
            console.print(f"[yellow][DRY RUN][/yellow] {filepath}")
        else:
            try:
                os.remove(filepath)
                console.print(f"[red]Deleted:[/red] {filepath}")
            except OSError as e:
                console.print(f"[red]Failed to delete {filepath}: {e}[/red]")

    console.rule()
    action = "Would delete" if dry_run else "Deleted"
    console.print(f'{action} {len(matched_files)} file(s) matching {", ".join(normalized)}', style='bold green')
    return 0

if __name__ == "__main__":
    raise SystemExit(app())
