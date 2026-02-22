from __future__ import annotations

from django.conf import settings


def _get_setting(name: str, default):
    return getattr(settings, name, default)


def _get_xbench_config() -> dict:
    """
    Read the optional `XBENCH` dict from Django settings.

    This is the preferred configuration style:

        XBENCH = {
            "ENABLED": True,
            "LOG": False,
            "SLOW_AGG": True,
        }

    If `XBENCH` is missing, django-xbench falls back to legacy flat settings
    (e.g., `XBENCH_ENABLED`, `XBENCH_LOG_ENABLED`, ...).
    """
    raw = getattr(settings, "XBENCH", None)
    if not isinstance(raw, dict):
        return {}
    return {str(k).upper(): v for k, v in raw.items()}


_XBENCH = _get_xbench_config()


def _get_bool(key: str, legacy_name: str, default: bool) -> bool:
    if key in _XBENCH:
        return bool(_XBENCH[key])
    return bool(_get_setting(legacy_name, default))


def _get_int(key: str, legacy_name: str, default: int) -> int:
    if key in _XBENCH:
        try:
            return int(_XBENCH[key])
        except (TypeError, ValueError):
            return default
    try:
        return int(_get_setting(legacy_name, default))
    except (TypeError, ValueError):
        return default


def _get_str_lower(key: str, legacy_name: str, default: str) -> str:
    if key in _XBENCH:
        return str(_XBENCH[key]).lower()
    return str(_get_setting(legacy_name, default)).lower()


# -----------------------------------------------------------------------------
# Public configuration values (used by the middleware and slow aggregation).
# -----------------------------------------------------------------------------

# Master switch.
XBENCH_ENABLED = _get_bool("ENABLED", "XBENCH_ENABLED", True)

# Optional request logging.
XBENCH_LOG_ENABLED = _get_bool("LOG", "XBENCH_LOG_ENABLED", False)
XBENCH_LOG_LEVEL = _get_str_lower("LOG_LEVEL", "XBENCH_LOG_LEVEL", "info")

# Slow endpoint aggregation (in-memory, per process).
XBENCH_SLOW_AGG_ENABLED = _get_bool("SLOW_AGG", "XBENCH_SLOW_AGG_ENABLED", False)

# Slow aggregation tuning (advanced; defaults are usually fine).
XBENCH_SLOW_AGG_BUCKET_SECONDS = _get_int(
    "SLOW_BUCKET_SECONDS", "XBENCH_SLOW_AGG_BUCKET_SECONDS", 10
)
XBENCH_SLOW_AGG_BUCKET_COUNT = _get_int(
    "SLOW_BUCKET_COUNT", "XBENCH_SLOW_AGG_BUCKET_COUNT", 60
)
XBENCH_SLOW_AGG_ENDPOINT_CAP = _get_int(
    "SLOW_ENDPOINT_CAP", "XBENCH_SLOW_AGG_ENDPOINT_CAP", 200
)

# Legacy-only: some older configs specify a target window size (seconds).
XBENCH_SLOW_AGG_WINDOW_SECONDS = _get_int(
    "SLOW_WINDOW_SECONDS", "XBENCH_SLOW_AGG_WINDOW_SECONDS", 0
)

XBENCH_SLOW_AGG_BUCKET_SECONDS_EXPLICIT = (
    "SLOW_BUCKET_SECONDS" in _XBENCH
    or getattr(settings, "XBENCH_SLOW_AGG_BUCKET_SECONDS", None) is not None
)
