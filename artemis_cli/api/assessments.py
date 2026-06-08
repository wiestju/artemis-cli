from artemis_cli.api.client import ArtemisClient, ArtemisError

_ASSESSMENT_PREFIX = {
    "text": "text-assessment",
    "modeling": "modeling-assessment",
    "file-upload": "fileupload-assessment",
    "programming": "programming-assessment",
}


def _prefix(exercise_type: str) -> str:
    prefix = _ASSESSMENT_PREFIX.get(exercise_type.lower())
    if prefix is None:
        valid = ", ".join(_ASSESSMENT_PREFIX)
        raise ArtemisError(0, f"Unknown exercise type '{exercise_type}'. Valid: {valid}")
    return prefix


def save_assessment(
    client: ArtemisClient,
    participation_id: int,
    feedbacks: list[dict],
    exercise_type: str = "text",
    result_id: int | None = None,
    submit: bool = False,
    note: str = "",
) -> dict:
    """Save (draft) or submit a final assessment."""
    prefix = _prefix(exercise_type)
    payload: dict = {"feedbacks": feedbacks, "submit": submit}
    if result_id:
        payload["resultId"] = result_id
    if note:
        payload["assessmentNote"] = note

    return client.post(
        f"{prefix}/participations/{participation_id}/results",
        json=payload,
    )


def cancel_assessment(client: ArtemisClient, submission_id: int, exercise_type: str = "text") -> None:
    prefix = _prefix(exercise_type)
    client.post(f"{prefix}/submissions/{submission_id}/cancel-assessment")


def create_external_result(
    client: ArtemisClient,
    exercise_id: int,
    student_login: str,
    score: float,
    feedbacks: list[dict] | None = None,
    rated: bool = True,
) -> dict:
    """Submit a result for a student without a participation (external grading)."""
    payload = {
        "score": score,
        "rated": rated,
        "feedbacks": feedbacks or [],
    }
    return client.post(
        f"assessment/exercises/{exercise_id}/external-submission-results?studentLogin={student_login}",
        json=payload,
    )
