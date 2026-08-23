from datetime import datetime, timezone
from typing import Any, Dict, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.session import SessionDocument


class SessionRepository:
    def __init__(self):
        self.collection_name = "sessions"

    @property
    def collection(self):
        return get_database()[self.collection_name]

    def _to_doc(self, raw: Optional[Dict[str, Any]]) -> Optional[SessionDocument]:
        if not raw:
            return None
        raw["_id"] = str(raw["_id"])
        return SessionDocument(**raw)

    async def create_session(
        self,
        user_id: str,
        refresh_token_hash: str,
        jti: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> SessionDocument:
        now = datetime.now(timezone.utc)
        doc = {
            "user_id": user_id,
            "refresh_token_hash": refresh_token_hash,
            "jti": jti,
            "user_agent": user_agent,
            "ip_address": ip_address,
            "expires_at": expires_at,
            "created_at": now,
            "updated_at": now
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return SessionDocument(**doc)

    async def find_session_by_hash(self, refresh_token_hash: str) -> Optional[SessionDocument]:
        raw = await self.collection.find_one({"refresh_token_hash": refresh_token_hash})
        return self._to_doc(raw)

    async def find_session_by_jti(self, jti: str) -> Optional[SessionDocument]:
        raw = await self.collection.find_one({"jti": jti})
        return self._to_doc(raw)

    async def delete_session_by_hash(self, refresh_token_hash: str) -> bool:
        result = await self.collection.delete_one({"refresh_token_hash": refresh_token_hash})
        return result.deleted_count > 0

    async def delete_session_by_jti(self, jti: str) -> bool:
        result = await self.collection.delete_one({"jti": jti})
        return result.deleted_count > 0

    async def delete_all_user_sessions(self, user_id: str) -> int:
        result = await self.collection.delete_many({"user_id": user_id})
        return result.deleted_count


session_repository = SessionRepository()
