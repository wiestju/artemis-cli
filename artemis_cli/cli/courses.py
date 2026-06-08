import click
from artemis_cli.api.client import get_client, ArtemisError
from artemis_cli.api import courses as api
from artemis_cli.cli.fmt import console, error, make_table


@click.group("courses")
def courses_group():
    """List and inspect courses."""


@courses_group.command("list")
def list_courses():
    """List all your courses."""
    try:
        client = get_client()
        items = api.list_courses(client)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    if not items:
        console.print("[yellow]No courses found.[/yellow]")
        return

    t = make_table("ID", "Title", "Short", "Role", "Start", "End")
    for c in sorted(items, key=lambda x: x.get("id", 0)):
        role = (
            "Instructor" if c.get("isAtLeastInstructor")
            else "Tutor" if c.get("isAtLeastTeachingAssistant")
            else "Student"
        )
        t.add_row(
            str(c.get("id", "")),
            c.get("title", ""),
            c.get("shortName", ""),
            role,
            _date(c.get("startDate")),
            _date(c.get("endDate")),
        )
    console.print(t)


@courses_group.command("exercises")
@click.argument("course_id", type=int)
def list_exercises(course_id: int):
    """List exercises for COURSE_ID."""
    try:
        client = get_client()
        items = api.list_exercises(client, course_id)
    except ArtemisError as e:
        error(str(e))
        raise SystemExit(1)

    if not items:
        console.print("[yellow]No exercises found.[/yellow]")
        return

    t = make_table("ID", "Title", "Type", "Due", "Points", "Assessment")
    for ex in sorted(items, key=lambda x: x.get("dueDate") or ""):
        t.add_row(
            str(ex.get("id", "")),
            ex.get("title", ""),
            ex.get("type", ""),
            _date(ex.get("dueDate")),
            str(ex.get("maxPoints", "")),
            ex.get("assessmentType", ""),
        )
    console.print(t)


def _date(iso: str | None) -> str:
    if not iso:
        return ""
    return iso[:10]
