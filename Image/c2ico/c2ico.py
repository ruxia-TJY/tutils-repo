from pathlib import Path
from typing import Annotated, Optional
from rich.console import Console
from PIL import Image
import typer

app = typer.Typer(
    name='c2ico',
    help="Convert images to ICO format",
)

SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff', '.gif'}

@app.command()
def main(
        image: Annotated[
            Path,
            typer.Argument(help="Image file to convert"),
        ],
        sizes: Annotated[
            Optional[list[int]],
            typer.Option(
                "--size", "-s",
                help="Icon sizes in pixels (e.g. -s 16 -s 32 -s 256)",
            ),
        ] = None,
        output: Annotated[
            Optional[Path],
            typer.Option(
                "--output", "-o",
                help="Output directory (default: same directory as input)",
            ),
        ] = None,
):
    console = Console()

    if not image.exists():
        console.print(f"[red]File not found: {image}[/red]")
        return 1

    if image.suffix.lower() not in SUPPORTED_EXTENSIONS:
        console.print(f"[red]Unsupported format: {image.suffix}[/red]")
        console.print(f"[yellow]Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}[/yellow]")
        return 1

    if sizes is None:
        sizes = [256]

    # Validate sizes
    for s in sizes:
        if s < 1 or s > 256:
            console.print(f"[red]Invalid size {s}: must be between 1 and 256[/red]")
            return 1

    try:
        img = Image.open(image)
        stem = image.stem
        parent = image.parent if output is None else output

        img = img.convert('RGBA')

        for s in sizes:
            out_path = parent / f"{stem}_{s}.ico"
            resized = img.resize((s, s), Image.Resampling.LANCZOS)
            resized.save(str(out_path), format='ICO', sizes=[(s, s)])
            console.print(f"[green]Converted:[/green] {image} -> {out_path} ({s}x{s})")
    except Exception as e:
        console.print(f"[red]Failed to convert: {e}[/red]")
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(app())
