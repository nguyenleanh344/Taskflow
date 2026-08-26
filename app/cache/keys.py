PROJECT_CACHE_PREFIX = "project"


def project_key(project_id: int) -> str:
    return f"{PROJECT_CACHE_PREFIX}:{project_id}"
