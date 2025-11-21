"""
Terminal UI utilities using Rich library for beautiful CLI output.
"""
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from typing import List, Optional
import time


# Global console instance
console = Console()


def print_header(text: str, style: str = "bold blue"):
    """Print a header panel."""
    console.print(Panel(text, style=style, padding=(1, 2)))


def print_status(text: str, emoji: str = "▶"):
    """Print a status message."""
    console.print(f"[yellow]{emoji}[/yellow] {text}")


def print_success(text: str):
    """Print a success message."""
    console.print(f"[green]✓[/green] {text}")


def print_error(text: str):
    """Print an error message."""
    console.print(f"[red]✗[/red] {text}")


def print_warning(text: str):
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {text}")


def print_info(text: str):
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {text}")


def print_markdown(markdown_text: str):
    """Print formatted markdown."""
    md = Markdown(markdown_text)
    console.print(md)


def print_json(data: dict, title: Optional[str] = None):
    """Print JSON data with syntax highlighting."""
    import json
    json_str = json.dumps(data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)

    if title:
        console.print(Panel(syntax, title=title, border_style="blue"))
    else:
        console.print(syntax)


def print_divider(char: str = "─", style: str = "dim"):
    """Print a divider line."""
    console.print(char * console.width, style=style)


def clear_screen():
    """Clear the terminal screen."""
    console.clear()


def get_input(prompt_text: str, default: Optional[str] = None) -> str:
    """Get user input with a styled prompt."""
    return Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]", default=default)


def get_confirmation(prompt_text: str, default: bool = True) -> bool:
    """Get yes/no confirmation from user."""
    return Confirm.ask(f"[bold yellow]{prompt_text}[/bold yellow]", default=default)


def print_product_table(products: List, max_rows: int = 5):
    """
    Print a table of products.

    Args:
        products: List of Product or AnalysisResult objects
        max_rows: Maximum number of rows to display
    """
    table = Table(title="Product Comparison", show_header=True, header_style="bold magenta")

    table.add_column("Rank", style="cyan", width=6)
    table.add_column("Product", style="green", width=40)
    table.add_column("Price", style="yellow", width=12)
    table.add_column("Rating", style="magenta", width=10)
    table.add_column("Score", style="blue", width=10)

    for i, item in enumerate(products[:max_rows], 1):
        # Handle both Product and AnalysisResult
        if hasattr(item, 'product'):
            # AnalysisResult
            product = item.product
            score = f"{item.match_score:.0f}/100"
        else:
            # Product
            product = item
            score = "N/A"

        retailer, price = product.get_best_price()
        rating = product.get_average_rating()

        # Truncate product name if too long
        name = product.name
        if len(name) > 37:
            name = name[:34] + "..."

        table.add_row(
            str(i),
            name,
            f"${price:.2f}",
            f"{rating:.1f}/5" if rating > 0 else "No rating",
            score
        )

    console.print(table)


def print_requirements_summary(requirements):
    """Print a summary of user requirements."""
    table = Table(title="Your Requirements", show_header=False, box=None)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")

    table.add_row("Product", requirements.product_category)

    if requirements.budget:
        budget_str = f"${requirements.budget.min or 0:.0f} - ${requirements.budget.max:.0f}"
        if requirements.budget.flexible:
            budget_str += " (flexible)"
        table.add_row("Budget", budget_str)

    if requirements.use_case:
        table.add_row("Use Case", requirements.use_case)

    if requirements.must_have_specs:
        specs = ", ".join(f"{k}: {v}" for k, v in list(requirements.must_have_specs.items())[:3])
        if len(requirements.must_have_specs) > 3:
            specs += f" (+{len(requirements.must_have_specs) - 3} more)"
        table.add_row("Must-Have Specs", specs)

    console.print(table)


def show_progress(description: str = "Processing..."):
    """
    Return a progress spinner context manager.

    Usage:
        with show_progress("Researching products..."):
            # Do work
            time.sleep(2)
    """
    return console.status(description, spinner="dots")


def create_progress_bar(total: int, description: str = "Progress"):
    """
    Create a progress bar.

    Usage:
        with create_progress_bar(100, "Scraping") as progress:
            task = progress.add_task("[cyan]Scraping...", total=100)
            for i in range(100):
                progress.update(task, advance=1)
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    )


def print_welcome():
    """Print welcome message."""
    welcome_text = """
    # Electronics Research Agent

    I'll help you find the perfect electronics product by:
    - Understanding your specific needs and constraints
    - Researching products across Amazon, Walmart, and Best Buy
    - Analyzing reviews and specifications
    - Surfacing important considerations you might miss
    - Providing top 5 recommendations with detailed comparisons

    Let's get started!
    """
    print_markdown(welcome_text)


def print_analysis_summary(analysis_results: List, requirements):
    """Print a summary of analysis results."""
    print_header("Analysis Complete")

    console.print(f"\n[bold]Total products analyzed:[/bold] {len(analysis_results)}")
    console.print(f"[bold]Top recommendations:[/bold] {min(5, len(analysis_results))}\n")

    if analysis_results:
        best = analysis_results[0]
        console.print(f"[bold green]Best match:[/bold green] {best.product.name}")
        console.print(f"[bold]Match score:[/bold] {best.match_score:.0f}/100")
        retailer, price = best.product.get_best_price()
        console.print(f"[bold]Best price:[/bold] ${price:.2f} at {retailer.title()}\n")


def save_report_prompt(report: str, filepath: str) -> bool:
    """Ask user if they want to save the report and do so if confirmed."""
    if get_confirmation(f"Would you like to save this report to {filepath}?", default=True):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            print_success(f"Report saved to {filepath}")
            return True
        except Exception as e:
            print_error(f"Failed to save report: {e}")
            return False
    return False


def print_section_header(text: str):
    """Print a section header."""
    console.print(f"\n[bold underline blue]{text}[/bold underline blue]\n")


def print_bullet_list(items: List[str], style: str = "white"):
    """Print a bullet point list."""
    for item in items:
        console.print(f"  • [{style}]{item}[/{style}]")
