"""
Read-only integration tests against a live Artemis instance.

All tests use only GET requests (plus the initial login POST).
Nothing is submitted, locked, or modified.

IDs (course, exercise, participation) are auto-detected from the API —
no manual configuration needed beyond credentials.
"""
import pytest
from artemis_cli.api.client import ArtemisClient, ArtemisError
from artemis_cli.api import courses as courses_api
from artemis_cli.api import exercises as exercises_api
from artemis_cli.api import submissions as submissions_api
from artemis_cli.api import complaints as complaints_api


def _skip_if_forbidden(exc: ArtemisError, msg: str = "requires tutor/instructor role") -> None:
    if exc.status == 403:
        pytest.skip(f"403 — {msg}")
    raise exc


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class TestAuth:
    def test_token_obtained(self, client: ArtemisClient) -> None:
        assert client._token, "Login produced an empty token"
        assert len(client._token) > 20

    def test_server_stored(self, client: ArtemisClient) -> None:
        assert client.server.startswith("https://")


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

class TestCourses:
    def test_list_returns_list(self, client: ArtemisClient) -> None:
        result = courses_api.list_courses(client)
        assert isinstance(result, list)

    def test_courses_have_required_fields(self, client: ArtemisClient) -> None:
        courses = courses_api.list_courses(client)
        if not courses:
            pytest.skip("No enrolled courses")
        for c in courses:
            assert "id" in c, f"Course missing 'id': {c}"
            assert "title" in c, f"Course missing 'title': {c}"

    def test_get_course_by_id(self, client: ArtemisClient, course_id: int) -> None:
        course = courses_api.get_course(client, course_id)
        assert course.get("id") == course_id

    def test_list_exercises_for_course(self, client: ArtemisClient, course_id: int) -> None:
        exercises = courses_api.list_exercises(client, course_id)
        assert isinstance(exercises, list)

    def test_exercise_fields(self, client: ArtemisClient, course_id: int) -> None:
        exercises = courses_api.list_exercises(client, course_id)
        if not exercises:
            pytest.skip("No exercises in this course")
        for ex in exercises:
            assert "id" in ex
            assert "title" in ex


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------

class TestExercises:
    def test_get_exercise(self, client: ArtemisClient, exercise_id: int) -> None:
        ex = exercises_api.get_exercise(client, exercise_id)
        assert ex.get("id") == exercise_id
        assert "title" in ex

    def test_exercise_type_is_known(self, client: ArtemisClient, exercise_id: int) -> None:
        known = {
            "TEXT", "MODELING", "FILE_UPLOAD", "PROGRAMMING",
            "TextExercise", "ModelingExercise", "FileUploadExercise", "ProgrammingExercise",
            "file-upload", "text", "modeling", "programming",
        }
        ex = exercises_api.get_exercise(client, exercise_id)
        ex_type = ex.get("type") or ex.get("exerciseType") or ex.get("discriminator")
        if ex_type:
            assert ex_type in known, f"Unknown exercise type: {ex_type}"

    def test_exercise_dashboard(self, client: ArtemisClient, exercise_id: int) -> None:
        try:
            data = exercises_api.get_exercise_for_assessment(client, exercise_id)
        except ArtemisError as e:
            _skip_if_forbidden(e, "exercise dashboard requires tutor role")
        assert data is not None

    def test_exercise_dashboard_has_submission_stats(
        self, client: ArtemisClient, exercise_id: int
    ) -> None:
        try:
            data = exercises_api.get_exercise_for_assessment(client, exercise_id)
        except ArtemisError as e:
            _skip_if_forbidden(e, "exercise dashboard requires tutor role")
        assert "numberOfSubmissions" in data or "id" in data

    def test_list_submissions_returns_data(
        self, client: ArtemisClient, exercise_id: int
    ) -> None:
        try:
            data = exercises_api.list_submissions(client, exercise_id, page_size=5)
        except ArtemisError as e:
            _skip_if_forbidden(e, "submission list requires tutor role")
        assert data is not None

    def test_list_submissions_pagination(
        self, client: ArtemisClient, exercise_id: int
    ) -> None:
        try:
            page0 = exercises_api.list_submissions(client, exercise_id, page=0, page_size=5)
            page1 = exercises_api.list_submissions(client, exercise_id, page=1, page_size=5)
        except ArtemisError as e:
            _skip_if_forbidden(e, "submission list requires tutor role")
        # Both pages must be valid responses (content or empty)
        assert page0 is not None
        assert page1 is not None


# ---------------------------------------------------------------------------
# Submissions (tutor only)
# ---------------------------------------------------------------------------

class TestSubmissions:
    def test_get_submissions_returns_list(
        self, client: ArtemisClient, participation_id: int
    ) -> None:
        subs = submissions_api.get_submissions(client, participation_id)
        assert isinstance(subs, list)

    def test_submission_has_required_fields(
        self, client: ArtemisClient, participation_id: int
    ) -> None:
        subs = submissions_api.get_submissions(client, participation_id)
        if not subs:
            pytest.skip("No submissions for this participation")
        sub = subs[-1]
        assert "id" in sub

    def test_result_details(
        self, client: ArtemisClient, participation_id: int
    ) -> None:
        subs = submissions_api.get_submissions(client, participation_id)
        if not subs:
            pytest.skip("No submissions")
        result = None
        for sub in reversed(subs):
            results = sub.get("results") or []
            if results:
                result = results[-1]
                break
        if not result:
            pytest.skip("No assessed result found")
        details = submissions_api.get_result_details(client, participation_id, result["id"])
        assert isinstance(details, list)


# ---------------------------------------------------------------------------
# Complaints (tutor only)
# ---------------------------------------------------------------------------

class TestComplaints:
    def test_list_complaints_returns_list(
        self, client: ArtemisClient, exercise_id: int
    ) -> None:
        try:
            items = complaints_api.list_complaints(client, exercise_id, "COMPLAINT")
        except ArtemisError as e:
            _skip_if_forbidden(e, "complaint list requires tutor role")
        assert isinstance(items, list)

    def test_list_more_feedback_returns_list(
        self, client: ArtemisClient, exercise_id: int
    ) -> None:
        try:
            items = complaints_api.list_more_feedback(client, exercise_id)
        except ArtemisError as e:
            _skip_if_forbidden(e, "more-feedback list requires tutor role")
        assert isinstance(items, list)

    def test_complaint_fields_when_present(
        self, client: ArtemisClient, exercise_id: int
    ) -> None:
        try:
            items = complaints_api.list_complaints(client, exercise_id, "COMPLAINT")
        except ArtemisError as e:
            _skip_if_forbidden(e, "complaint list requires tutor role")
        if not items:
            pytest.skip("No complaints for this exercise")
        for c in items:
            assert "id" in c
            assert "complaintType" in c
