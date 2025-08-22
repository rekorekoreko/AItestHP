from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from .models import SubmissionAdmin, Status
from .config import settings


class MongoStore:
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.collection = self.client[db_name][collection_name]

    async def create(self, sub: SubmissionAdmin) -> SubmissionAdmin:
        doc = sub.model_dump()
        doc["_id"] = str(sub.id)
        doc["id"] = str(sub.id)
        await self.collection.insert_one(doc)
        return sub

    async def get(self, sid: UUID) -> Optional[SubmissionAdmin]:
        doc = await self.collection.find_one({"id": str(sid)})
        if doc:
            doc.pop("_id", None)
            return SubmissionAdmin(**doc)
        return None

    async def list(self, status: Optional[Status] = None) -> List[SubmissionAdmin]:
        query: dict = {}
        if status is not None:
            query["status"] = status
        cursor = self.collection.find(query).sort("created_at", -1)
        items: List[SubmissionAdmin] = []
        async for doc in cursor:
            doc.pop("_id", None)
            items.append(SubmissionAdmin(**doc))
        return items

    async def update(self, sid: UUID, **kwargs) -> SubmissionAdmin:
        await self.collection.update_one({"id": str(sid)}, {"$set": kwargs})
        doc = await self.collection.find_one({"id": str(sid)})
        if not doc:
            raise KeyError("Submission not found")
        doc.pop("_id", None)
        return SubmissionAdmin(**doc)


store = MongoStore(settings.mongodb_uri, settings.mongodb_db, settings.mongodb_collection)
