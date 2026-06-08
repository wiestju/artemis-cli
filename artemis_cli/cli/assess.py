import json
from pathlib import Path

import click
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from artemis_cli.api.client import get_client, ArtemisError
from artemis_cli.api import assessments as api
from artemis_cli.cli.fmt import console, success, error, info


@click.group("assess")
def assess_group():
    """Grade and submit assessments (tutor commands)."""


@assess_group.command("submit")
@click.argument("participation_id", type=int)
@click.option("--type", "exercise_type", default="text", show_default=True,
              type=click.Choice(["text", "modeling", "file-upload", "programming"]))
@click.option("--feedbacks", "-f", type=str, default=None,
              help="JSON array of feedback objects or path to a .json file")
@click.option("--result-id", type=int, default=None)
@click.option("--note", default="", help="Internal assessor note")
@click.option("--draft", is_flag=True, help="Save as draft instead of finalising")
def submit_assessment(
    participation_id: int,
    exercise_type: str,
    feedbacks: str | None,
    result_id: int | None,
    note: str,
    draft: bool,
):
    """Submit an assessment for PARTICIPATION_ID."""
    try:
        fb_list = _load_feedbacks(feedbacks)
    except (json.JSONDecodeError, OSError) as e:
        error(f"Invalid feedbacks: {e}")
        raise SystemExit(1)
    try:
        result = api.save_assessment(
            get_client(), participation_id, fb_list, exercise_type,
            result_id=result_id, submit=not draft, note=note,
        )
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    action = "Draft saved" if draft else "Assessment submitted"
    success(f"{action} — result ID: [bold]{result.get('id')}[/bold], score: [bold]{result.get('score')}[/bold]")


@assess_group.command("interactive")
@click.argument("participation_id", type=int)
@click.option("--type", "exercise_type", default="text", show_default=True,
              type=click.Choice(["text", "modeling", "file-upload", "programming"]))
@click.option("--max-points", type=float, default=100.0, show_default=True)
def interactive_assess(participation_id: int, exercise_type: str, max_points: float):
    """Interactively build and submit an assessment."""
    console.print(Panel(
        f"Participation: [bold]{participation_id}[/bold]  |  Type: [bold]{exercise_type}[/bold]  |  Max: [bold]{max_points}[/bold]",
        title="Interactive Assessment",
        expand=False,
    ))

    feedbacks: list[dict] = []
    total = 0.0

    while True:
        console.print(f"\n[dim]Current feedbacks: {len(feedbacks)} | Total credits: {total:.1f}[/dim]")
        action = Prompt.ask(
            "Action",
            choices=["add", "list", "remove", "submit", "draft", "cancel"],
            default="add",
        )

        if action == "add":
            text = Prompt.ask("Feedback text")
            detail = Prompt.ask("Detail (optional)", default="")
            try:
                credits = float(Prompt.ask("Credits", default="0"))
            except ValueError:
                error("Credits must be a number.")
                continue
            fb: dict = {"text": text, "type": "MANUAL_UNREFERENCED", "credits": credits}
            if detail:
                fb["detailText"] = detail
            feedbacks.append(fb)
            total += credits
            success(f"Added feedback ({credits:+.1f})")

        elif action == "list":
            if not feedbacks:
                console.print("[dim]No feedbacks yet.[/dim]")
            for i, fb in enumerate(feedbacks):
                console.print(f"  [{i}] {fb['credits']:+.1f}  {fb['text']}")

        elif action == "remove":
            try:
                idx = int(Prompt.ask("Index to remove"))
            except ValueError:
                error("Index must be an integer.")
                continue
            if 0 <= idx < len(feedbacks):
                removed = feedbacks.pop(idx)
                total -= removed["credits"]
                success(f"Removed feedback [{idx}]")
            else:
                error(f"No feedback at index {idx}.")

        elif action in ("submit", "draft"):
            if not feedbacks and not Confirm.ask("No feedbacks added — submit anyway?"):
                continue
            try:
                result = api.save_assessment(
                    get_client(), participation_id, feedbacks, exercise_type,
                    submit=(action == "submit"),
                )
            except ArtemisError as e:
                error(str(e))
                raise SystemExit(1)
            label = "Submitted" if action == "submit" else "Draft saved"
            success(f"{label} — result ID: [bold]{result.get('id')}[/bold], score: [bold]{result.get('score')}[/bold]")
            break

        elif action == "cancel":
            if Confirm.ask("Cancel and discard?"):
                console.print("[yellow]Cancelled.[/yellow]")
                break


@assess_group.command("cancel")
@click.argument("submission_id", type=int)
@click.option("--type", "exercise_type", default="text", show_default=True,
              type=click.Choice(["text", "modeling", "file-upload", "programming"]))
def cancel_assessment(submission_id: int, exercise_type: str):
    """Release a locked submission without grading it."""
    try:
        api.cancel_assessment(get_client(), submission_id, exercise_type)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)
    success(f"Submission [bold]{submission_id}[/bold] released.")


@assess_group.command("external")
@click.argument("exercise_id", type=int)
@click.option("--student", required=True, help="Student login (e.g. uXXXX)")
@click.option("--score", required=True, type=float)
@click.option("--feedbacks", "-f", type=str, default=None)
def external_result(exercise_id: int, student: str, score: float, feedbacks: str | None):
    """Submit an external result for a student (no participation required)."""
    try:
        fb_list = _load_feedbacks(feedbacks)
    except (json.JSONDecodeError, OSError) as e:
        error(f"Invalid feedbacks: {e}")
        raise SystemExit(1)
    try:
        result = api.create_external_result(get_client(), exercise_id, student, score, fb_list)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)
    success(f"Result created — ID: [bold]{result.get('id')}[/bold], score: [bold]{result.get('score')}[/bold]")


def _load_feedbacks(value: str | None) -> list[dict]:
    if not value:
        return []
    p = Path(value)
    if p.is_file():
        return json.loads(p.read_text())
    return json.loads(value)
