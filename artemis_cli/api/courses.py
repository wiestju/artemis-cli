from artemis_cli.api.client import ArtemisClient


def list_courses(client: ArtemisClient) -> list[dict]:
    data = client.get("core/courses/for-dashboard")
    if isinstance(data, dict):
        items = data.get("courses", [])
    else:
        items = data or []
    # Newer Artemis wraps each entry as {"course": {...}, totalStudents: ...}
    return [item["course"] if "course" in item else item for item in items]


def get_course(client: ArtemisClient, course_id: int) -> dict:
    data = client.get(f"core/courses/{course_id}/for-dashboard")
    return data.get("course", data) if isinstance(data, dict) and "course" in data else data


def list_exercises(client: ArtemisClient, course_id: int) -> list[dict]:
    course = get_course(client, course_id)
    return course.get("exercises", [])
