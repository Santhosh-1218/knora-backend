from datetime import datetime, timezone
from typing import Any, Dict, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.otp import OTPDocument


class OTPRepository:
    def __init__(self):
        self.collection_name = "otp_verifications"

    @property
    def collection(self):
        return get_database()[self.collection_name]

    def _to_doc(self, raw: Optional[Dict[str, Any]]) -> Optional[OTPDocument]:
        if not raw:
            return None
        raw["_id"] = str(raw["_id"])
        return OTPDocument(**raw)

    async def invalidate_previous_otps(self, identifier_hash: str, channel: str, purpose: str) -> None:
        await self.collection.delete_many({
            "identifier_hash": identifier_hash,
            "channel": channel,
            "purpose": purpose
        })

    async def create_otp(
        self,
        identifier_hash: str,
        channel: str,
        purpose: str,
        otp_hash: str,
        salt: str,
        expires_at: datetime,
        max_attempts: int = 5
    ) -> OTPDocument:
        # Invalidate existing OTPs for the same target and purpose
        await self.invalidate_previous_otps(identifier_hash, channel, purpose)

        doc = {
            "identifier_hash": identifier_hash,
            "channel": channel,
            "purpose": purpose,
            "otp_hash": otp_hash,
            "salt": salt,
            "attempts": 0,
            "max_attempts": max_attempts,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return OTPDocument(**doc)

    async def find_latest_otp(self, identifier_hash: str, channel: str, purpose: str) -> Optional[OTPDocument]:
        raw = await self.collection.find_one(
            {
                "identifier_hash": identifier_hash,
                "channel": channel,
                "purpose": purpose
            },
            sort=[("created_at", -1)]
        )
        return self._to_doc(raw)

    async def increment_attempts(self, otp_id: str) -> int:
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(otp_id)},
            {"$inc": {"attempts": 1}},
            return_document=True
        )
        return result.get("attempts", 0) if result else 0

    async def delete_otp(self, otp_id: str) -> None:
        await self.collection.delete_one({"_id": ObjectId(otp_id)})


otp_repository = OTPRepository()
