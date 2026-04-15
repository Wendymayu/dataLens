"""Main entry point for DataLens"""
from agent.config import ConfigManager
from agent.cli import CliInterface
from agent.agent import NL2SQLAgent
from agent.utils import setup_windows_encoding, get_console

# Configure Windows console encoding
setup_windows_encoding()


def main():
    """Main program loop"""
    console = get_console()
    config_manager = ConfigManager("config.json")
    cli = CliInterface(config_manager)

    # Check if API key is configured
    if not config_manager.config.model.api_key:
        console.print("[yellow]⚠ No API key configured. Please configure a model first.[/yellow]")
        cli.config_model()

    # Check if any database is configured
    if not config_manager.config.databases:
        console.print("[yellow]⚠ No database configured. Please add one.[/yellow]")
        cli.config_add()

    cli.print_banner()

    # Main interaction loop
    while True:
        try:
            user_input = console.input(cli.input_prompt()).strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["exit", "quit"]:
                console.print("[cyan]Goodbye![/cyan]")
                break

            elif user_input.lower() == "help":
                cli.show_help()

            elif user_input.lower().startswith("config "):
                cmd = user_input.split(maxsplit=1)[1]
                if cmd == "add":
                    cli.config_add()
                elif cmd == "list":
                    cli.config_list()
                elif cmd == "remove":
                    cli.config_remove()
                elif cmd == "model":
                    cli.config_model()
                else:
                    console.print("[red]Unknown config command[/red]")

            elif user_input.lower().startswith("switch "):
                db_name = user_input.split(maxsplit=1)[1]
                cli.switch_database(db_name)

            else:
                # Natural language query
                if not config_manager.config.current_database:
                    console.print("[red]No database selected. Use 'config add' first.[/red]")
                    continue

                try:
                    with console.status("[cyan]Processing query...[/cyan]", spinner="dots"):
                        db_config = config_manager.get_database()
                        agent = NL2SQLAgent(
                            config_manager.config.model,
                            db_config
                        )
                        response = agent.query(user_input)
                        agent.close()

                    cli.display_query_result(user_input, response)

                except Exception as e:
                    cli.display_error(str(e))

        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
