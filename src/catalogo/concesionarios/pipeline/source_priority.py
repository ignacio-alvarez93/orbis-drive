SOURCE_PRIORITY = {
    "autocasion_profesional": 100,
    "cochesnet_concesionarios": 50,
}


def get_source_priority(source_name: str | None) -> int:
    if not source_name:
        return 0
    return SOURCE_PRIORITY.get(source_name, 0)