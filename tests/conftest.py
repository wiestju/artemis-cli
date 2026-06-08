"""
Integration test fixtures.

Requires a .env file in the project root. Two auth modes are supported:

  Password login (internal Artemis accounts):
    ARTEMIS_USERNAME=uXXXXX
    ARTEMIS_PASSWORD=yourpassword

  Token login (SSO / university login, e.g. KIT):
    ARTEMIS_TOKEN=<jwt cookie value from browser DevTools>

Optional:
  ARTEMIS_SERVER=https://artemis.cs.kit.edu   (default)
  ARTEMIS_COURSE_ID=123                        (auto-detected from first course if omitted)
  ARTEMIS_EXERCISE_ID=456                      (exercise-level tests skipped if omitted)
"""
import os
import pytest
from dotenv import load_dotenv

from artemis_cli.api.client import login, ArtemisClient

load_dotenv()


@pytest.fixture(scope="session")
def client() -> ArtemisClient:
    server = os.getenv("ARTEMIS_SERVER", "https://artemis.cs.kit.edu").rstrip("/")

    # Token-based auth (SSO / KIT)
    token = os.getenv("ARTEMIS_TOKEN")
    if token:
        return ArtemisClient(server=server, token=token)

    # Password-based auth (internal accounts)
    username = os.getenv("ARTEMIS_USERNAME")
    password = os.getenv("ARTEMIS_PASSWORD")
    if not username or not password:
        pytest.skip(
            "No credentials in .env — set ARTEMIS_TOKEN (SSO) "
            "or ARTEMIS_USERNAME + ARTEMIS_PASSWORD"
        )

    try:
        token = login(server, username, password)
    except Exception as e:
        pytest.skip(f"Login failed: {e}")

    return ArtemisClient(server=server, token=token)


@pytest.fixture(scope="session")
def course_id(client: ArtemisClient) -> int:
    """Use ARTEMIS_COURSE_ID from .env, or fall back to the first enrolled course."""
    from artemis_cli.api.courses import list_courses
    env_id = os.getenv("ARTEMIS_COURSE_ID")
    if env_id:
        return int(env_id)
    courses = list_courses(client)
    if not courses:
        pytest.skip("No courses found — set ARTEMIS_COURSE_ID in .env")
    return int(courses[0]["id"])


@pytest.fixture(scope="session")
def exercise_id(client: ArtemisClient, course_id: int) -> int:
    """Use ARTEMIS_EXERCISE_ID from .env, or auto-detect from first exercise in the course."""
    from artemis_cli.api.courses import list_exercises
    env_id = os.getenv("ARTEMIS_EXERCISE_ID")
    if env_id:
        return int(env_id)
    exercises = list_exercises(client, course_id)
    if not exercises:
        pytest.skip("No exercises found in course — set ARTEMIS_EXERCISE_ID in .env")
    return int(exercises[0]["id"])


@pytest.fixture(scope="session")
def participation_id(client: ArtemisClient, exercise_id: int) -> int:
    """Auto-detect a participation ID from the first submission of the exercise."""
    from artemis_cli.api.exercises import list_submissions
    from artemis_cli.api.client import ArtemisError
    env_id = os.getenv("ARTEMIS_PARTICIPATION_ID")
    if env_id:
        return int(env_id)
    try:
        data = list_submissions(client, exercise_id, page_size=1)
        items = data.get("content", []) if isinstance(data, dict) else data or []
        if not items:
            pytest.skip("No submissions found — cannot auto-detect participation ID")
        part = items[0].get("participation", {})
        pid = part.get("id")
        if not pid:
            pytest.skip("Participation ID not in submission response")
        return int(pid)
    except ArtemisError as e:
        if e.status == 403:
            pytest.skip("Tutor role required to list submissions")
        raise
