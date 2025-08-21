from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
from .models import SubmissionAdmin, Status


class InMemoryStore:
    def __init__(self):
        self._db: Dict[UUID, SubmissionAdmin] = {}

    def create(self, sub: SubmissionAdmin):
        self._db[sub.id] = sub
        return sub

    def get(self, sid: UUID) -> Optional[SubmissionAdmin]:
        return self._db.get(sid)

    def list(self, status: Optional[Status] = None) -> List[SubmissionAdmin]:
        items = list(self._db.values())
        if status is not None:
            items = [x for x in items if x.status == status]
        return sorted(items, key=lambda x: x.created_at, reverse=True)

    def update(self, sid: UUID, **kwargs) -> SubmissionAdmin:
        s = self._db[sid]
        for k, v in kwargs.items():
            setattr(s, k, v)
        self._db[sid] = s
        return s


store = InMemoryStore()
