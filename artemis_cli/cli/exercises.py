import click
from rich.panel import Panel
from artemis_cli.api.client import get_client, ArtemisError
from artemis_cli.api import exercises as api
from artemis_cli.cli.fmt import console, error, make_table, info


@click.group("exercises")
def exercises_group():
    """Inspect exercises and their submissions."""


@exercises_group.command("view")
@click.argument("exercise_id", type=int)
def view_exercise(exercise_id: int):
    """Show details for EXERCISE_ID."""
    try:
        ex = api.get_exercise(get_client(), exercise_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    console.print(Panel(
        f"[bold]{ex.get('title')}[/bold]\n"
        f"Type        : {ex.get('type', '')}\n"
        f"Max Points  : {ex.get('maxPoints', '')} (+{ex.get('bonusPoints', 0)} bonus)\n"
        f"Assessment  : {ex.get('assessmentType', '')}\n"
        f"Due         : {ex.get('dueDate', '')}\n"
        f"Release     : {ex.get('releaseDate', '')}\n"
        f"Categories  : {', '.join(ex.get('categories', []))}\n",
        title=f"Exercise #{exercise_id}",
        expand=False,
    ))

    ps = ex.get("problemStatement")
    if ps:
        console.print("\n[bold]Problem Statement[/bold]")
        console.print(ps[:2000] + ("..." if len(ps) > 2000 else ""))


@exercises_group.command("submissions")
@click.argument("exercise_id", type=int)
@click.option("--page", default=0, show_default=True)
@click.option("--page-size", default=20, show_default=True)
@click.option("--search", default="", help="Filter by student name/login")
def list_submissions(exercise_id: int, page: int, page_size: int, search: str):
    """List submissions for EXERCISE_ID (instructor only).

    Note: Tutors use 'exercises next' to receive one submission at a time.
    This command requires instructor role.
    """
    try:
        data = api.list_submissions(get_client(), exercise_id, page, page_size, search)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    items = data.get("content", []) if isinstance(data, dict) else data or []
    total = data.get("totalElements", len(items)) if isinstance(data, dict) else len(items)

    if not items:
        console.print("[yellow]No submissions found.[/yellow]")
        return

    t = make_table("Sub ID", "Participation", "Student", "Submitted", "Score", "Assessed by")
    for s in items:
        part = s.get("participation", {})
        student = part.get("student") or part.get("participants", [{}])[0] if part else {}
        result = (s.get("results") or [{}])[-1]
        assessor = result.get("assessor", {})
        t.add_row(
            str(s.get("id", "")),
            str(part.get("id", "")),
            student.get("login") or student.get("name") or "",
            "✓" if s.get("submitted") else "–",
            str(result.get("score", "")) if result else "",
            assessor.get("login", "") if assessor else "",
        )
    console.print(t)
    console.print(f"[dim]Page {page + 1} · {len(items)} of {total} submissions[/dim]")


@exercises_group.command("next")
@click.argument("exercise_id", type=int)
@click.option("--correction-round", type=click.IntRange(0, 1), default=0, show_default=True,
              help="0 = first correction, 1 = second correction round")
def next_submission(exercise_id: int, correction_round: int):
    """Lock and display the next unassessed submission."""
    try:
        sub = api.lock_submission(get_client(), exercise_id, correction_round)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    part = sub.get("participation", {})
    console.print(Panel(
        f"Submission ID    : {sub.get('id')}\n"
        f"Participation ID : {part.get('id')}\n"
        f"Submitted        : {sub.get('submissionDate', '')}\n"
        f"Type             : {sub.get('submissionType', '')}\n",
        title="Locked Submission",
        expand=False,
    ))

    # Show text content if available
    text = sub.get("text")
    if text:
        console.print("\n[bold]Submission Text[/bold]")
        console.print(text)


@exercises_group.command("dashboard")
@click.argument("exercise_id", type=int)
def exercise_dashboard(exercise_id: int):
    """Show assessment progress dashboard for EXERCISE_ID (tutor view)."""
    try:
        data = api.get_exercise_for_assessment(get_client(), exercise_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    subs = data.get("numberOfSubmissions") or {}
    assessments = data.get("numberOfAssessmentsOfCorrectionRounds") or [{}]
    done = assessments[0] if assessments else {}

    console.print(Panel(
        f"[bold]{data.get('title', '')}[/bold]\n"
        f"Submissions (in time) : {subs.get('inTime', '?')}\n"
        f"Submissions (late)    : {subs.get('late', 0)}\n"
        f"Assessments done      : {done.get('inTime', '?')}\n"
        f"Open complaints       : {data.get('numberOfOpenComplaints', 0)}\n"
        f"More feedback reqs.   : {data.get('numberOfOpenMoreFeedbackRequests', 0)}\n",
        title=f"Assessment Dashboard #{exercise_id}",
        expand=False,
    ))
    total = subs.get("inTime", 0) or 0
    done_n = done.get("inTime", 0) or 0
    if total:
        pct = done_n / total * 100
        info(f"Progress: {done_n}/{total} ({pct:.0f}%)")
