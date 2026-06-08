import click
from artemis_cli.cli.auth import login, logout, whoami
from artemis_cli.cli.courses import courses_group
from artemis_cli.cli.exercises import exercises_group
from artemis_cli.cli.submissions import submissions_group
from artemis_cli.cli.assess import assess_group
from artemis_cli.cli.complaints import complaints_group


@click.group()
@click.version_option(package_name="artemis-cli")
def cli():
    """Unofficial CLI for the Artemis learning platform.

    \b
    Quickstart:
      artemis login
      artemis courses list
      artemis courses exercises <course_id>
      artemis exercises submissions <exercise_id>
      artemis exercises next <exercise_id>
      artemis assess interactive <participation_id>
    """


cli.add_command(login)
cli.add_command(logout)
cli.add_command(whoami)
cli.add_command(courses_group)
cli.add_command(exercises_group)
cli.add_command(submissions_group)
cli.add_command(assess_group)
cli.add_command(complaints_group)
