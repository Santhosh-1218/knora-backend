from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.user import UserDocument


class UserRepository:
    def __init__(self):
        self.collection_name = "users"

    @property
    def collection(self):
        return get_database()[self.collection_name]

    def _to_doc(self, raw: Optional[Dict[str, Any]]) -> Optional[UserDocument]:
        if not raw:
            return None
        raw["_id"] = str(raw["_id"])
        return UserDocument(**raw)

    async def create_user(self, user_dict: Dict[str, Any]) -> UserDocument:
        now = datetime.now(timezone.utc)
        user_dict["created_at"] = user_dict.get("created_at", now)
        user_dict["updated_at"] = user_dict.get("updated_at", now)
        
        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        return UserDocument(**user_dict)

    async def find_by_id(self, user_id: str) -> Optional[UserDocument]:
        try:
            raw = await self.collection.find_one({"_id": ObjectId(user_id)})
            return self._to_doc(raw)
        except Exception:
            return None

    async def find_by_email(self, email_normalized: str) -> Optional[UserDocument]:
        raw = await self.collection.find_one({"email_normalized": email_normalized.lower().strip()})
        return self._to_doc(raw)

    async def find_by_mobile(self, mobile: str) -> Optional[UserDocument]:
        raw = await self.collection.find_one({"mobile": mobile.strip()})
        return self._to_doc(raw)

    async def find_by_google_sub(self, sub: str) -> Optional[UserDocument]:
        raw = await self.collection.find_one({"google.sub": sub})
        return self._to_doc(raw)

    async def exists_by_email_or_mobile(self, email_normalized: str, mobile: str) -> tuple[bool, bool]:
        """Returns tuple of (email_exists, mobile_exists) in a single query optimization."""
        cursor = self.collection.find(
            {"$or": [{"email_normalized": email_normalized.lower().strip()}, {"mobile": mobile.strip()}]},
            {"email_normalized": 1, "mobile": 1}
        )
        email_exists = False
        mobile_exists = False
        async for doc in cursor:
            if doc.get("email_normalized") == email_normalized.lower().strip():
                email_exists = True
            if doc.get("mobile") == mobile.strip():
                mobile_exists = True
        return email_exists, mobile_exists

    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[UserDocument]:
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": updates},
            return_document=True
        )
        return self._to_doc(result)

    async def add_auth_method(self, user_id: str, auth_method: str) -> Optional[UserDocument]:
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {
                "$addToSet": {"auth_methods": auth_method},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            return_document=True
        )
        return self._to_doc(result)

    async def link_google_identity(
        self,
        user_id: str,
        google_sub: str,
        google_email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None
    ) -> Optional[UserDocument]:
        google_data = {
            "sub": google_sub,
            "email": google_email.lower().strip(),
            "name": name,
            "picture": picture
        }
        updates: Dict[str, Any] = {
            "google": google_data,
            "updated_at": datetime.now(timezone.utc)
        }
        if picture:
            updates["profile_image"] = picture
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {
                "$set": updates,
                "$addToSet": {"auth_methods": "google"}
            },
            return_document=True
        )
        return self._to_doc(result)

    async def update_last_login(self, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login_at": now, "updated_at": now}}
        )


user_repository = UserRepository()
