from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .bucket import Bucket, DEFAULT_ENDPOINT_CAP
from .stats import EndpointStats


@dataclass(slots=True)
class RollingWindow:
    """
    Rolling time window using fixed-size buckets (ring buffer).

    Invariant:
        window_seconds == bucket_seconds * bucket_count
    """

    bucket_seconds: int = 10
    bucket_count: int = 60
    endpoint_cap: int = DEFAULT_ENDPOINT_CAP

    buckets: List[Bucket] = field(init=False)
    window_seconds: int = field(init=False)  # derived

    _current_idx: int = field(default=0, init=False)
    _current_bucket_start: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.bucket_seconds <= 0:
            raise ValueError("bucket_seconds must be > 0")
        if self.bucket_count <= 0:
            raise ValueError("bucket_count must be > 0")

        self.window_seconds = self.bucket_seconds * self.bucket_count
        self.buckets = [Bucket(endpoint_cap=self.endpoint_cap) for _ in range(self.bucket_count)]

        now = int(time.time())
        self._current_bucket_start = self._align_to_bucket(now)
        self._current_idx = 0

    def update(
        self,
        endpoint_key: str,
        *,
        duration_s: float,
        db_s: float = 0.0,
        query_count: int = 0,
        now: int | None = None,
        n: int = 1,
    ) -> None:
        self.rotate_if_needed(now=now)
        self.buckets[self._current_idx].update(
            endpoint_key,
            duration_s=duration_s,
            db_s=db_s,
            query_count=query_count,
            n=n,
        )

    def rotate_if_needed(self, *, now: int | None = None) -> None:
        if now is None:
            now = int(time.time())

        aligned = self._align_to_bucket(now)
        if aligned <= self._current_bucket_start:
            return

        steps = (aligned - self._current_bucket_start) // self.bucket_seconds
        if steps <= 0:
            return

        # If time jumped beyond the full window, clear everything.
        if steps >= self.bucket_count:
            for b in self.buckets:
                b.clear()
            self._current_idx = 0
            self._current_bucket_start = aligned
            return

        # Advance step-by-step: move index, clear the new current bucket.
        for _ in range(steps):
            self._current_idx = (self._current_idx + 1) % self.bucket_count
            self.buckets[self._current_idx].clear()

        self._current_bucket_start = aligned

    def aggregate(self, *, now: int | None = None) -> Dict[str, EndpointStats]:
        self.rotate_if_needed(now=now)
        merged: Dict[str, EndpointStats] = {}
        for b in self.buckets:
            for key, st in b.iter_items():
                merged.setdefault(key, EndpointStats()).merge_from(st)
        return merged

    def top_n(self, n: int = 20, *, now: int | None = None) -> List[Tuple[str, EndpointStats]]:
        if n <= 0:
            return []
        items = list(self.aggregate(now=now).items())
        items.sort(key=lambda kv: kv[1].damage, reverse=True)
        return items[:n]

    def snapshot(self, n: int = 20, *, now: int | None = None) -> Dict[str, object]:
        top = self.top_n(n=n, now=now)
        return {
            "window_seconds": self.window_seconds,
            "bucket_seconds": self.bucket_seconds,
            "bucket_count": self.bucket_count,
            "generated_at": int(time.time()) if now is None else now,
            "top": [{"endpoint": k, **st.to_dict()} for k, st in top],
        }

    def _align_to_bucket(self, ts: int) -> int:
        return ts - (ts % self.bucket_seconds)
