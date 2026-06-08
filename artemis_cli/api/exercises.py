from artemis_cli.api.client import ArtemisClient


def get_exercise(client: ArtemisClient, exercise_id: int) -> dict:
    return client.get(f"exercise/exercises/{exercise_id}")


def get_exercise_for_assessment(client: ArtemisClient, exercise_id: int) -> dict:
    return client.get(f"exercise/exercises/{exercise_id}/for-assessment-dashboard")


def list_submissions(
    client: ArtemisClient,
    exercise_id: int,
    page: int = 0,
    page_size: int = 20,
    search: str = "",
) -> dict:
    params: dict = {"page": page, "pageSize": page_size}
    if search:
        params["searchTerm"] = search
    return client.get(f"exercise/exercises/{exercise_id}/submissions-for-import", params=params)


def lock_submission(client: ArtemisClient, exercise_id: int, correction_round: int = 0) -> dict:
    """Claim the next unassessed submission for grading."""
    return client.get(
        f"exercise/exercises/{exercise_id}/submission-without-assessment",
        params={"lock": "true", "correction-round": correction_round},
    )
