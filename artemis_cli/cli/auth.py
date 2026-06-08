import click
from artemis_cli.api import client as api
from artemis_cli import config
from artemis_cli.cli.fmt import console, success, error

_SSO_HINT = (
    "\n[dim]If your instance uses SSO (e.g. KIT), use --token instead:\n"
    "  1. Log in via browser\n"
    "  2. Open DevTools → Application → Cookies → copy the [bold]jwt[/bold] value\n"
    "  3. Run: artemis login --server <url> --token <jwt>[/dim]"
)


@click.command("login")
@click.option("--server", "-s", prompt="Artemis server URL", help="e.g. https://artemis.cs.kit.edu")
@click.option("--username", "-u", default=None, help="Username (not needed with --token)")
@click.option("--password", "-p", default=None, hide_input=True, help="Password (not needed with --token)")
@click.option("--token", "-t", default=None, help="Paste JWT directly (for SSO instances like KIT)")
@click.option("--no-remember", is_flag=True, default=False, help="Short-lived token (password login only)")
def login(server: str, username: str | None, password: str | None, token: str | None, no_remember: bool):
    """Log in and store credentials.

    \b
    Password login (internal Artemis accounts):
      artemis login --server https://example.com

    \b
    Token login (SSO / university login, e.g. KIT):
      1. Log in via browser, open DevTools → Application → Cookies
      2. Copy the value of the 'jwt' cookie
      3. artemis login --server https://artemis.cs.kit.edu --token <jwt>
    """
    if token:
        config.save_session(server, token)
        success(f"Token stored for [cyan]{server}[/cyan]")
        return

    # Password flow — prompt only if not provided
    if not username:
        username = click.prompt("Username")
    if not password:
        password = click.prompt("Password", hide_input=True)

    with console.status("Authenticating..."):
        try:
            token = api.login(server, username, password, remember_me=not no_remember)
        except api.ArtemisError as e:
            error(str(e))
            console.print(_SSO_HINT)
            raise SystemExit(1)

    config.save_session(server, token)
    success(f"Logged in to [cyan]{server}[/cyan] as [bold]{username}[/bold]")


@click.command("logout")
def logout():
    """Clear stored credentials."""
    server = config.get_server()
    config.clear_session()
    success(f"Logged out from [cyan]{server or 'Artemis'}[/cyan]")


@click.command("whoami")
def whoami():
    """Show the currently configured server and token status."""
    server = config.get_server()
    token = config.get_token()
    if not server or not token:
        error("Not logged in. Run: artemis login")
        raise SystemExit(1)
    console.print(f"Server : [cyan]{server}[/cyan]")
    console.print(f"Token  : [dim]{token[:12]}...{token[-6:]}[/dim]")
