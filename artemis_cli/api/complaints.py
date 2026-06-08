from artemis_cli.api.client import ArtemisClient


def list_complaints(
    client: ArtemisClient,
    exercise_id: int,
    complaint_type: str = "COMPLAINT",
) -> list[dict]:
    """List complaints or more-feedback requests for an exercise (tutor)."""
    params = {"exerciseId": exercise_id, "complaintType": complaint_type}
    data = client.get("assessment/complaints", params=params)
    return data if isinstance(data, list) else []


def list_more_feedback(client: ArtemisClient, exercise_id: int) -> list[dict]:
    return list_complaints(client, exercise_id, complaint_type="MORE_FEEDBACK")


def lock_complaint(client: ArtemisClient, complaint_id: int) -> dict:
    """Claim a complaint for editing (creates an empty draft response)."""
    return client.post(f"assessment/complaints/{complaint_id}/response") or {}


def unlock_complaint(client: ArtemisClient, complaint_id: int) -> None:
    """Release a locked complaint without resolving it."""
    client.delete(f"assessment/complaints/{complaint_id}/response")


def respond_to_complaint(
    client: ArtemisClient,
    complaint_id: int,
    text: str,
    accepted: bool,
) -> dict:
    """Lock then resolve a complaint in one call."""
    lock_complaint(client, complaint_id)
    payload = {
        "action": "RESOLVE_COMPLAINT",
        "responseText": text,
        "complaintIsAccepted": accepted,
    }
    return client.patch(f"assessment/complaints/{complaint_id}/response", json=payload) or {}
