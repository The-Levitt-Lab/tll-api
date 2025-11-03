from __future__ import annotations

from fastapi import Query


class PaginationParams:
    def __init__(self, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
        self.offset = offset
        self.limit = limit

