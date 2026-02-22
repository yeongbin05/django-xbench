from __future__ import annotations

from typing import Dict, Any
from .compat import dataclass_slots

@dataclass_slots()
class EndpointStats:
    """
    Aggregated performance statistics for a single endpoint.

    Stores cumulative metrics such as request count, total latency,
    maximum latency, database time, and query count.

    All time values are in seconds.
    """

    count: int = 0
    total: float = 0.0
    max: float = 0.0
    db_total: float = 0.0
    query_total: int = 0

    def update(
        self,
        *,
        duration_s: float,
        db_s: float = 0.0,
        query_count: int = 0,
        n: int = 1,
    ) -> None:
        """
        Add request metrics to this endpoint.

        Negative values are treated as zero.

        Parameters
        ----------
        duration_s
            Total request duration in seconds.
        db_s, optional
            Database time in seconds.
        query_count, optional
            Number of database queries executed.
        n, optional
            Number of identical samples to add (default 1).
        """
        if n <= 0:
            return

        if duration_s < 0:
            duration_s = 0.0
        if db_s < 0:
            db_s = 0.0
        if query_count < 0:
            query_count = 0

        self.count += n
        self.total += duration_s * n
        self.db_total += db_s * n
        self.query_total += query_count * n

        if duration_s > self.max:
            self.max = duration_s

    def merge_from(self, other: "EndpointStats") -> None:
        """
        Merge metrics from another EndpointStats instance into this one.

        The merge is performed in-place. The `other` instance is not modified.
        """
        if other.count <= 0:
            return

        self.count += other.count
        self.total += other.total
        self.db_total += other.db_total
        self.query_total += other.query_total

        if other.max > self.max:
            self.max = other.max

    @property
    def avg(self) -> float:
        """Average request duration in seconds."""
        return self.total / self.count if self.count else 0.0

    @property
    def db_ratio(self) -> float:
        """Ratio of database time to total time (0–1)."""
        return (self.db_total / self.total) if self.total > 0 else 0.0

    @property
    def avg_q(self) -> float:
        """Average number of queries per request."""
        return self.query_total / self.count if self.count else 0.0

    @property
    def damage(self) -> float:
        """Total accumulated latency (count × avg)."""
        return self.total

    def to_dict(self) -> Dict[str, Any]:
        """
        Return metrics as a dictionary.

        Keys
        ----
        count : int
        total : float
        avg : float
        max : float
        db_total : float
        db_ratio : float
        query_total : int
        avg_q : float
        damage : float
        """
        return {
            "count": self.count,
            "total": self.total,
            "avg": self.avg,
            "max": self.max,
            "db_total": self.db_total,
            "db_ratio": self.db_ratio,
            "query_total": self.query_total,
            "avg_q": self.avg_q,
            "damage": self.damage,
        }
