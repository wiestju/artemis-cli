import click
from pathlib import Path
from rich.panel import Panel
from artemis_cli.api.client import get_client, ArtemisError
from artemis_cli.api import submissions as api
from artemis_cli.cli.fmt import console, error, success, make_table


@click.group("submissions")
def submissions_group():
    """Inspect submission content and results."""


@submissions_group.command("view")
@click.argument("participation_id", type=int)
def view_submission(participation_id: int):
    """Show the latest submission for PARTICIPATION_ID."""
    try:
        subs = api.get_submissions(get_client(), participation_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    if not subs:
        console.print("[yellow]No submissions found.[/yellow]")
        return

    sub = subs[-1]
    console.print(Panel(
        f"Submission ID    : {sub.get('id')}\n"
        f"Type             : {sub.get('submissionType', '')}\n"
        f"Submitted        : {'✓' if sub.get('submitted') else '–'}\n"
        f"Date             : {sub.get('submissionDate', '')}\n"
        f"Language         : {sub.get('language', '')}\n",
        title=f"Submission (Participation #{participation_id})",
        expand=False,
    ))

    if sub.get("text"):
        console.print("\n[bold]Text[/bold]")
        console.print(sub["text"])

    if sub.get("repoCloneUrl") or sub.get("repositoryUri"):
        repo = sub.get("repoCloneUrl") or sub.get("repositoryUri")
        console.print(f"\n[bold]Repository[/bold] [cyan]{repo}[/cyan]")

    if len(subs) > 1:
        console.print(f"\n[dim]({len(subs)} submissions total — showing latest)[/dim]")


@submissions_group.command("result")
@click.argument("participation_id", type=int)
def view_result(participation_id: int):
    """Show the latest assessed result for PARTICIPATION_ID."""
    try:
        client = get_client()
        subs = api.get_submissions(client, participation_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    if not subs:
        console.print("[yellow]No submissions found.[/yellow]")
        return

    # Find latest submission that has a result
    result = None
    sub_id = None
    for sub in reversed(subs):
        results = sub.get("results") or []
        if results:
            result = results[-1]
            sub_id = sub.get("id")
            break

    if not result:
        console.print("[yellow]No assessed result found.[/yellow]")
        return

    assessor = result.get("assessor") or {}
    console.print(Panel(
        f"Result ID    : {result.get('id')}\n"
        f"Score        : {result.get('score')}\n"
        f"Rated        : {'✓' if result.get('rated') else '–'}\n"
        f"Completion   : {result.get('completionDate', '')}\n"
        f"Assessor     : {assessor.get('login', '')}\n"
        f"Submission   : {sub_id}\n",
        title=f"Latest Result (Participation #{participation_id})",
        expand=False,
    ))

    result_id = result.get("id")
    if result_id:
        try:
            feedbacks = api.get_result_details(client, participation_id, result_id)
        except ArtemisError:
            feedbacks = result.get("feedbacks") or []

        if feedbacks:
            t = make_table("Credits", "Text", "Detail")
            for fb in feedbacks:
                t.add_row(
                    f"{fb.get('credits', 0):+.1f}",
                    fb.get("text") or "",
                    fb.get("detailText") or "",
                )
            console.print(t)


@submissions_group.command("download")
@click.argument("participation_id", type=int)
@click.option("--output", "-o", default=None, help="Output file path (default: submission_<id>.zip)")
def download_submission(participation_id: int, output: str | None):
    """Download a file-upload submission to disk."""
    try:
        client = get_client()
        data = api.download_file_upload(client, participation_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    dest = Path(output) if output else Path(f"submission_{participation_id}.zip")
    dest.write_bytes(data)
    success(f"Saved to [cyan]{dest}[/cyan] ({len(data)} bytes)")
