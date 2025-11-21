#!/usr/bin/env python3
"""
Electronics Product Research Agent - Main Entry Point

A terminal-based AI agent that helps users research and compare electronics products
across multiple retailers (Amazon, Walmart, Best Buy).
"""
import sys
from orchestrator import WorkflowOrchestrator
from utils.terminal import (
    console, clear_screen, print_welcome, print_header,
    print_error, print_markdown, get_input, print_divider
)
from config import Config


def main():
    """Main entry point for the application."""
    # Clear screen and show welcome
    clear_screen()
    print_welcome()

    print_divider()

    # Get initial user input
    console.print("\n[bold]Tell me what you're looking for:[/bold]")
    console.print("[dim]Example: \"I need a gaming laptop under $1500 with good graphics\"[/dim]\n")

    try:
        user_input = get_input("You")

        if not user_input or not user_input.strip():
            print_error("Please provide some details about what you're looking for.")
            sys.exit(1)

        # Run the workflow
        orchestrator = WorkflowOrchestrator()
        report = orchestrator.run(user_input)

        if report:
            # Display the report
            print_divider()
            print_header("Your Personalized Product Research Report")
            print_markdown(report)

            console.print("\n[green]Report generation complete![/green]")
            console.print("Thank you for using the Electronics Research Agent!\n")
        else:
            print_error("Unable to generate report. Please try again.")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user. Goodbye![/yellow]\n")
        sys.exit(0)

    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")

        if Config.DEBUG:
            console.print("\n[red]Debug information:[/red]")
            raise

        console.print("\n[dim]Please check your configuration and try again.[/dim]")
        console.print("[dim]Enable DEBUG=true in .env for more details.[/dim]\n")
        sys.exit(1)


def show_version():
    """Display version information."""
    console.print("\n[bold cyan]Electronics Product Research Agent[/bold cyan]")
    console.print("Version: 1.0.0 (MVP)")
    console.print(f"LLM Provider: {Config.LLM_PROVIDER.title()}")
    console.print(f"LLM Model: {Config.LLM_MODEL}")
    console.print()


def show_help():
    """Display help information."""
    help_text = """
# Electronics Product Research Agent - Help

## Usage
```bash
python main.py
```

## How It Works
1. **Requirements Gathering**: The agent asks questions to understand what you need
2. **Product Research**: Searches across Amazon, Walmart, and Best Buy
3. **Analysis**: Uses AI to analyze products and identify the best matches
4. **Report Generation**: Creates a detailed comparison report with top 5 recommendations

## Configuration
Edit the `.env` file to configure:
- LLM provider (Claude or Gemini)
- API keys
- Scraping behavior
- Cache settings

## Tips
- Be specific about what you're looking for
- Include your budget
- Mention key requirements (specs, features, use case)
- The more information you provide upfront, the better the results

## Example Inputs
- "I need a 4K TV under $800 for gaming"
- "Looking for wireless earbuds with noise cancellation, budget $200"
- "Gaming laptop with RTX 4060, under $1500"

## Troubleshooting
- Make sure you have API keys configured in `.env`
- Check your internet connection
- Enable DEBUG=true for detailed error messages
- Clear cache if results seem stale: `rm -rf cache/*`

## Support
For issues and feedback, check the project README.
"""
    print_markdown(help_text)


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['-h', '--help', 'help']:
            show_help()
            sys.exit(0)

        elif arg in ['-v', '--version', 'version']:
            show_version()
            sys.exit(0)

        else:
            console.print(f"[yellow]Unknown argument: {arg}[/yellow]")
            console.print("Use --help for usage information\n")
            sys.exit(1)

    # Run main application
    main()
