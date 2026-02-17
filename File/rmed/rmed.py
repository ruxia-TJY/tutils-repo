import os
from pathlib import Path
from typing import Annotated
from rich.console import Console
import typer

app = typer.Typer(
    name='rmed',
    help="remove empty directories",
)

@app.command()
def main(
        path: Annotated[
            Path,
            typer.Argument(
                ...,
                help="Target directory path"),
        ] = Path.cwd(),
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run", "-d",
                help="Preview empty directories without actually deleting",
                is_flag=True,
            )
        ] = False,
):
    console = Console()

    if not os.path.exists(path):
        console.print("[red]The path does not exist![/red]")
        return 0

    removed = []
    # bottomup so that nested empty dirs get removed first
    for root, dirs, files in os.walk(path, topdown=False):
        if root == str(path):
            continue
        if len(os.listdir(root)) == 0:
            if dry_run:
                console.print(f"[yellow][DRY RUN][/yellow] {root}")
            else:
                try:
                    os.rmdir(root)
                    console.print(f"[red]Deleted:[/red] {root}")
                except OSError as e:
                    console.print(f"[red]Failed to delete {root}: {e}[/red]")
                    continue
            removed.append(root)

    console.rule()
    if not removed:
        console.print("[green]No empty directories found.[/green]")
    else:
        action = "Would delete" if dry_run else "Deleted"
        console.print(f'{action} {len(removed)} empty directory(ies)', style='bold green')
    return 0

if __name__ == "__main__":
    raise SystemExit(app())
