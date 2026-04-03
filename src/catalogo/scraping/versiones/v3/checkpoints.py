from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _safe_name(source: str) -> str:
    digest = hashlib.md5(source.encode("utf-8")).hexdigest()
    return digest


def _state_file(checkpoints_dir: Path) -> Path:
    return checkpoints_dir / "state.json"


def _entry_file(checkpoints_dir: Path, source: str) -> Path:
    return checkpoints_dir / f"{_safe_name(source)}.json"


def _ensure_state(checkpoints_dir: Path) -> dict[str, Any]:
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    state_path = _state_file(checkpoints_dir)

    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    state = {
        "completed_sources": [],
        "failed_sources": [],
        "last_updated": None,
    }
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return state


def _save_state(checkpoints_dir: Path, state: dict[str, Any]) -> None:
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    state_path = _state_file(checkpoints_dir)
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_checkpoint_state(checkpoints_dir: str | Path) -> dict[str, Any]:
    return _ensure_state(Path(checkpoints_dir))


def mark_completed(
    checkpoints_dir: str | Path,
    source: str,
    payload: dict[str, Any],
) -> None:
    checkpoints_path = Path(checkpoints_dir)
    checkpoints_path.mkdir(parents=True, exist_ok=True)

    entry_path = _entry_file(checkpoints_path, source)
    entry_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    state = _ensure_state(checkpoints_path)
    completed = set(state.get("completed_sources", []))
    failed = set(state.get("failed_sources", []))

    completed.add(source)
    failed.discard(source)

    state["completed_sources"] = sorted(completed)
    state["failed_sources"] = sorted(failed)
    state["last_updated"] = payload.get("timestamp")
    _save_state(checkpoints_path, state)


def mark_failed(
    checkpoints_dir: str | Path,
    source: str,
    payload: dict[str, Any],
) -> None:
    checkpoints_path = Path(checkpoints_dir)
    checkpoints_path.mkdir(parents=True, exist_ok=True)

    entry_path = _entry_file(checkpoints_path, source)
    entry_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    state = _ensure_state(checkpoints_path)
    completed = set(state.get("completed_sources", []))
    failed = set(state.get("failed_sources", []))

    failed.add(source)
    completed.discard(source)

    state["completed_sources"] = sorted(completed)
    state["failed_sources"] = sorted(failed)
    state["last_updated"] = payload.get("timestamp")
    _save_state(checkpoints_path, state)


def append_json_array(path: str | Path, item: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    data: list[Any]
    if file_path.exists():
        try:
            existing = json.loads(file_path.read_text(encoding="utf-8"))
            data = existing if isinstance(existing, list) else []
        except Exception:
            data = []
    else:
        data = []

    data.append(item)
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_error(
    errors_dir: str | Path,
    source: str,
    payload: dict[str, Any],
) -> None:
    errors_path = Path(errors_dir)
    errors_path.mkdir(parents=True, exist_ok=True)

    error_file = errors_path / f"{_safe_name(source)}.json"
    error_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifest = errors_path / "errors.json"
    manifest_data: list[Any]
    if manifest.exists():
        try:
            existing = json.loads(manifest.read_text(encoding="utf-8"))
            manifest_data = existing if isinstance(existing, list) else []
        except Exception:
            manifest_data = []
    else:
        manifest_data = []

    manifest_data.append(payload)
    manifest.write_text(
        json.dumps(manifest_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
