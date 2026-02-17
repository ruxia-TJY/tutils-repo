import os
from pathlib import Path
from typing import Annotated
from rich.console import Console
import typer

app = typer.Typer(
    name='TCount',
    help="Count all files in folder",
)

@app.command()
def main(
        path:Annotated[
            Path,
            typer.Argument(..., help="Path to count files in")
        ] = Path.cwd(),
        show:Annotated[
            bool,
            typer.Option(
                "--show",
                "-s",
                help="Show all files and folders",
                is_flag=True,
            )
        ] = False,
):
    console = Console()

    if not os.path.exists(path):
        console.print("[red]The path does not exist![/red]")
        return 0

    fileCount = 0
    dirCount = 0

    for root, dirs, files in os.walk(path):
        dirCount += len(dirs)
        fileCount += len(files)

        for dir in dirs:
            if show: console.print(os.path.join(root, dir),style='bold yellow')

        for file in files:
            if show:console.print(os.path.join(root, file),style='#af00ff')

    console.rule()
    console.print(f'Files Count:{fileCount}',style='bold green')
    console.print(f'Dirs Count:{dirCount}',style='bold green')
    console.print(f'Total Files:{fileCount + dirCount}',style='bold green')
    return 0

if __name__ == "__main__":
    raise SystemExit(app())
