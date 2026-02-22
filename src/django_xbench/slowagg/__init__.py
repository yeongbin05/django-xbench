from .window import RollingWindow
from ..conf import (
    XBENCH_SLOW_AGG_BUCKET_SECONDS,
    XBENCH_SLOW_AGG_BUCKET_COUNT,
    XBENCH_SLOW_AGG_ENDPOINT_CAP,
    XBENCH_SLOW_AGG_WINDOW_SECONDS,
    XBENCH_SLOW_AGG_BUCKET_SECONDS_EXPLICIT,
)


def _ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


bucket_count = int(XBENCH_SLOW_AGG_BUCKET_COUNT)
bucket_seconds = int(XBENCH_SLOW_AGG_BUCKET_SECONDS)

# Backward compatibility: legacy configs may set a target window size instead of bucket seconds.
# Legacy window_seconds is only used when bucket_seconds was not explicitly set.
if (not XBENCH_SLOW_AGG_BUCKET_SECONDS_EXPLICIT) and XBENCH_SLOW_AGG_WINDOW_SECONDS > 0:
    window_seconds = int(XBENCH_SLOW_AGG_WINDOW_SECONDS)
    bucket_seconds = max(1, _ceil_div(window_seconds, bucket_count))

WINDOW = RollingWindow(
    bucket_seconds=bucket_seconds,
    bucket_count=bucket_count,
    endpoint_cap=int(XBENCH_SLOW_AGG_ENDPOINT_CAP),
)
