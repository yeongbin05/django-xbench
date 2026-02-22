from __future__ import annotations

import sys
from dataclasses import dataclass

def dataclass_slots(**kwargs):
    def deco(cls):
        if sys.version_info >= (3, 10):
            return dataclass(slots=True, **kwargs)(cls)
        return dataclass(**kwargs)(cls)
    return deco