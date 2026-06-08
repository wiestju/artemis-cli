import click
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from artemis_cli.api.client import get_client, ArtemisError
from artemis_cli.api import complaints as api
from artemis_cli.cli.fmt import console, error, success, make_table


@click.group("complaints")
def complaints_group():
    """Manage complaints and more-feedback requests (tutor commands)."""


@complaints_group.command("list")
@click.argument("exercise_id", type=int)
@click.option("--type", "complaint_type",
              type=click.Choice(["complaint", "feedback"], case_sensitive=False),
              default="complaint", show_default=True,
              help="complaint = grade complaints, feedback = more-feedback requests")
def list_complaints(exercise_id: int, complaint_type: str):
    """List open complaints or more-feedback requests for EXERCISE_ID."""
    api_type = "COMPLAINT" if complaint_type.lower() == "complaint" else "MORE_FEEDBACK"
    try:
        items = api.list_complaints(get_client(), exercise_id, api_type)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    if not items:
        console.print("[yellow]No open items found.[/yellow]")
        return

    t = make_table("ID", "Student", "Type", "Accepted", "Text")
    for c in items:
        student = (c.get("student") or c.get("participant") or {})
        accepted = c.get("accepted")
        t.add_row(
            str(c.get("id", "")),
            student.get("login") or student.get("name") or "",
            c.get("complaintType", ""),
            "✓" if accepted is True else ("✗" if accepted is False else "–"),
            (c.get("complaintText") or "")[:80],
        )
    console.print(t)
    console.print(f"[dim]{len(items)} item(s)[/dim]")


@complaints_group.command("unlock")
@click.argument("complaint_id", type=int)
def unlock_complaint(complaint_id: int):
    """Release a locked complaint without resolving it."""
    try:
        api.unlock_complaint(get_client(), complaint_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)
    success(f"Complaint [bold]{complaint_id}[/bold] unlocked.")


@complaints_group.command("respond")
@click.argument("complaint_id", type=int)
@click.option("--text", "-t", default=None, help="Response text (prompted if omitted)")
@click.option("--accept/--reject", default=None,
              help="Accept or reject the complaint (prompted if omitted)")
def respond_to_complaint(complaint_id: int, text: str | None, accept: bool | None):
    """Submit a tutor response to COMPLAINT_ID."""
    if text is None:
        text = Prompt.ask("Response text")
    if accept is None:
        accept = Confirm.ask("Accept the complaint?")

    try:
        result = api.respond_to_complaint(get_client(), complaint_id, text, accept)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    action = "accepted" if accept else "rejected"
    rid = (result or {}).get("id", "")
    success(f"Complaint [bold]{complaint_id}[/bold] {action} — response ID: [bold]{rid}[/bold]")


@complaints_group.command("feedback-list")
@click.argument("exercise_id", type=int)
def list_feedback_requests(exercise_id: int):
    """List open more-feedback requests for EXERCISE_ID."""
    try:
        items = api.list_more_feedback(get_client(), exercise_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    if not items:
        console.print("[yellow]No more-feedback requests found.[/yellow]")
        return

    t = make_table("ID", "Student", "Accepted", "Text")
    for c in items:
        student = (c.get("student") or c.get("participant") or {})
        accepted = c.get("accepted")
        t.add_row(
            str(c.get("id", "")),
            student.get("login") or student.get("name") or "",
            "✓" if accepted is True else ("✗" if accepted is False else "–"),
            (c.get("complaintText") or "")[:80],
        )
    console.print(t)
    console.print(f"[dim]{len(items)} request(s)[/dim]")
