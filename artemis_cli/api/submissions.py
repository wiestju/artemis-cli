from artemis_cli.api.client import ArtemisClient


def get_submissions(client: ArtemisClient, participation_id: int) -> list[dict]:
    """All submissions for a participation (latest last)."""
    data = client.get(f"exercise/participations/{participation_id}/submissions")
    return data if isinstance(data, list) else []


def get_result_details(client: ArtemisClient, participation_id: int, result_id: int) -> list[dict]:
    data = client.get(f"assessment/participations/{participation_id}/results/{result_id}/details")
    return data if isinstance(data, list) else []


def download_file_upload(client: ArtemisClient, participation_id: int) -> bytes:
    """Download a file-upload submission as raw bytes."""
    return client.get_bytes(f"fileupload/participations/{participation_id}/file-upload-submission")
