"""CLI interface for DataLens Agent"""
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from agent.config import ConfigManager, DatabaseConfig
from agent.utils import get_console
import os


class CliInterface:
    """Command-line interface for the DataLens Agent"""

    def __init__(self, config_manager: ConfigManager):
        self.console = get_console()
        self.config_manager = config_manager

    def print_banner(self):
        """Print welcome banner"""
        banner = """
[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]
[bold cyan]║      DataLens - 智能数据分析平台      ║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]

[green]Commands:[/green]
  [yellow]config add[/yellow]       - Add a new database
  [yellow]config list[/yellow]      - List all databases
  [yellow]config remove[/yellow]    - Remove a database
  [yellow]config model[/yellow]     - Configure LLM model
  [yellow]switch [db_name][/yellow] - Switch active database
  [yellow]help[/yellow]             - Show this help
  [yellow]exit / quit[/yellow]      - Exit the program

[green]Or just type your question directly![/green]
        """
        self.console.print(banner)

    def input_prompt(self) -> str:
        """Get user input with custom prompt"""
        current_db = self.config_manager.config.current_database or "none"
        return f"[cyan]({current_db})>[/cyan] "

    def show_help(self):
        """Show detailed help information"""
        help_text = """
[bold cyan]DataLens Help[/bold cyan]

[bold]Configuration Commands:[/bold]
  [yellow]config add[/yellow]
    Interactively add a new database connection.

  [yellow]config list[/yellow]
    Display all configured databases and highlight the current one.

  [yellow]config remove[/yellow]
    Remove a database configuration.

  [yellow]config model[/yellow]
    Configure the LLM model (anthropic, qwen, zhipu).

[bold]Database Commands:[/bold]
  [yellow]switch <db_name>[/yellow]
    Switch to a different database.

[bold]Query:[/bold]
  Simply type your natural language question about the database!
  Examples:
    - "How many users are there?"
    - "Show me the top 10 products by price"
    - "List all orders from 2024"
        """
        self.console.print(help_text)

    def config_add(self):
        """Add a new database configuration"""
        self.console.print("[bold cyan]Add New Database[/bold cyan]")
        name = self.console.input("[yellow]Database name:[/yellow] ").strip()
        if not name:
            self.console.print("[red]Database name cannot be empty[/red]")
            return

        if name in self.config_manager.config.databases:
            self.console.print("[red]Database already exists[/red]")
            return

        host = self.console.input("[yellow]Host (default: localhost):[/yellow] ").strip() or "localhost"
        port = self.console.input("[yellow]Port (default: 3306):[/yellow] ").strip() or "3306"
        user = self.console.input("[yellow]Username:[/yellow] ").strip()
        password = self.console.input("[yellow]Password:[/yellow] ").strip()
        database = self.console.input("[yellow]Database name:[/yellow] ").strip()

        if not all([user, database]):
            self.console.print("[red]Username and database name are required[/red]")
            return

        try:
            db_config = DatabaseConfig(
                name=name,
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database,
            )
            self.config_manager.add_database(name, db_config)
            self.console.print(f"[green]✓ Database '{name}' added successfully[/green]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

    def config_list(self):
        """List all database configurations"""
        dbs = self.config_manager.list_databases()
        if not dbs:
            self.console.print("[yellow]No databases configured[/yellow]")
            return

        table = Table(title="Configured Databases")
        table.add_column("Name", style="cyan")
        table.add_column("Host", style="magenta")
        table.add_column("Database", style="green")

        current = self.config_manager.config.current_database
        for name, db in dbs.items():
            marker = " ✓" if name == current else "  "
            table.add_row(f"{marker} {name}", db.host, db.database)

        self.console.print(table)

    def config_remove(self):
        """Remove a database configuration"""
        dbs = self.config_manager.list_databases()
        if not dbs:
            self.console.print("[yellow]No databases to remove[/yellow]")
            return

        self.console.print("[bold cyan]Remove Database[/bold cyan]")
        self.console.print("Available databases:")
        for i, name in enumerate(dbs.keys(), 1):
            self.console.print(f"  {i}. {name}")

        choice = self.console.input("[yellow]Enter database name to remove:[/yellow] ").strip()
        if choice in dbs:
            self.config_manager.remove_database(choice)
            self.console.print(f"[green]✓ Database '{choice}' removed[/green]")
        else:
            self.console.print("[red]Invalid database name[/red]")

    def config_model(self):
        """Configure LLM model"""
        self.console.print("[bold cyan]Configure LLM Model[/bold cyan]")
        self.console.print("\nAvailable providers:")
        self.console.print("  1. anthropic (Claude)")
        self.console.print("  2. qwen (Alibaba Tongyi)")
        self.console.print("  3. zhipu (Zhipu AI / GLM)")
        self.console.print("  4. openai-compatible (OpenAI兼容API，支持自定义URL)")

        provider_choice = self.console.input("[yellow]Select provider (1-4):[/yellow] ").strip()
        provider_map = {"1": "anthropic", "2": "qwen", "3": "zhipu", "4": "openai-compatible"}
        provider = provider_map.get(provider_choice)

        if not provider:
            self.console.print("[red]Invalid choice[/red]")
            return

        base_url = None

        if provider == "anthropic":
            model_name = "claude-3-5-sonnet-20241022"
            self.console.print(f"[cyan]Default model: {model_name}[/cyan]")
        elif provider == "qwen":
            model_name = "qwen-turbo"
            custom = self.console.input("[yellow]Model name (default: qwen-turbo):[/yellow] ").strip()
            if custom:
                model_name = custom
        elif provider == "zhipu":
            model_name = "glm-4"
            custom = self.console.input("[yellow]Model name (default: glm-4):[/yellow] ").strip()
            if custom:
                model_name = custom
        elif provider == "openai-compatible":
            model_name = self.console.input("[yellow]Model name (e.g., glm-5, qwen-max):[/yellow] ").strip()
            if not model_name:
                self.console.print("[red]Model name is required[/red]")
                return
            base_url = self.console.input("[yellow]Base URL (e.g., https://dashscope.aliyuncs.com/compatible-mode/v1):[/yellow] ").strip()
            if not base_url:
                self.console.print("[red]Base URL is required for openai-compatible provider[/red]")
                return

        api_key = self.console.input(f"[yellow]API Key:[/yellow] ").strip()
        if not api_key:
            self.console.print("[red]API key is required[/red]")
            return

        self.config_manager.update_model(provider, model_name, api_key, base_url)
        self.console.print(f"[green]✓ Model configured: {provider} - {model_name}[/green]")
        if base_url:
            self.console.print(f"[green]  Base URL: {base_url}[/green]")

    def switch_database(self, db_name: str):
        """Switch active database"""
        if self.config_manager.set_current_database(db_name):
            self.console.print(f"[green]✓ Switched to database: {db_name}[/green]")
        else:
            self.console.print(f"[red]Database '{db_name}' not found[/red]")

    def display_query_result(self, query: str, result: str):
        """Display query result"""
        self.console.print("\n" + "="*60)
        self.console.print("[bold cyan]Response:[/bold cyan]")
        self.console.print(Panel(result, border_style="cyan"))
        self.console.print("="*60 + "\n")

    def display_error(self, error: str):
        """Display error message"""
        self.console.print(Panel(f"[red]Error: {error}[/red]", border_style="red"))
