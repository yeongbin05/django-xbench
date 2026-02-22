from __future__ import annotations

from dataclasses import field
from typing import Dict, Iterable, Tuple
from .compat import dataclass_slots
from .stats import EndpointStats


DEFAULT_ENDPOINT_CAP = 200
OTHER_KEY = "__other__"


dataclass_slots
class Bucket:
    """
    A single time bucket holding per-endpoint aggregated stats.

    - Stores: endpoint_key -> EndpointStats
    - Safety belt: caps the number of endpoints to avoid unbounded growth.
      When cap is reached, new endpoints are aggregated into "__other__".
    """
    endpoint_cap: int = DEFAULT_ENDPOINT_CAP
    data: Dict[str, EndpointStats] = field(default_factory=dict)

    def clear(self) -> None:
        """Reset bucket contents."""
        self.data.clear()

    def update(
        self,
        endpoint_key: str,
        *,
        duration_s: float,
        db_s: float = 0.0,
        query_count: int = 0,
        n: int = 1,
    ) -> None:
        """
        Update stats for an endpoint within this bucket.

        If the number of unique endpoints exceeds `endpoint_cap`,
        new unseen endpoints are aggregated into "__other__".
        """
        key = self._resolve_key(endpoint_key)
        stats = self.data.get(key)
        if stats is None:
            stats = EndpointStats()
            self.data[key] = stats

        stats.update(
            duration_s=duration_s,
            db_s=db_s,
            query_count=query_count,
            n=n,
        )

    def iter_items(self) -> Iterable[Tuple[str, EndpointStats]]:
        """Iterate (endpoint_key, EndpointStats) pairs."""
        return self.data.items()

    def _resolve_key(self, endpoint_key: str) -> str:
        """
        Decide where to store this endpoint.

        - If endpoint already exists: keep it.
        - Else if we still have capacity: allocate a new entry.
        - Else: use OTHER_KEY to aggregate.
        """
        if endpoint_key in self.data:
            return endpoint_key

        if self.endpoint_cap <= 0:
            # Degenerate config: everything goes to __other__
            return OTHER_KEY

        if len(self.data) < self.endpoint_cap:
            return endpoint_key

        return OTHER_KEY
