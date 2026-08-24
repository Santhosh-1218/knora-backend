from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.resume import ResumeDocument, ResumeFileDocument


class ResumeRepository:
    @property
    def resumes_collection(self):
        return get_database()["resumes"]

    @property
    def files_collection(self):
        return get_database()["resume_files"]

    async def create(self, resume: ResumeDocument) -> ResumeDocument:
        doc = resume.model_dump(by_alias=True, exclude={"id"})
        doc["created_at"] = datetime.now(timezone.utc)
        doc["updated_at"] = datetime.now(timezone.utc)
        result = await self.resumes_collection.insert_one(doc)
        resume.id = str(result.inserted_id)
        return resume

    async def find_by_id(self, resume_id: str, user_id: str) -> Optional[ResumeDocument]:
        try:
            query = {"_id": ObjectId(resume_id), "user_id": user_id}
        except Exception:
            return None
        doc = await self.resumes_collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            return ResumeDocument(**doc)
        return None

    async def list_by_user(self, user_id: str) -> List[ResumeDocument]:
        cursor = self.resumes_collection.find({"user_id": user_id}).sort("updated_at", -1)
        resumes = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            resumes.append(ResumeDocument(**doc))
        return resumes

    async def update(self, resume_id: str, user_id: str, update_data: dict) -> Optional[ResumeDocument]:
        try:
            query = {"_id": ObjectId(resume_id), "user_id": user_id}
        except Exception:
            return None

        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.resumes_collection.find_one_and_update(
            query,
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
            return ResumeDocument(**result)
        return None

    async def delete(self, resume_id: str, user_id: str) -> bool:
        try:
            query = {"_id": ObjectId(resume_id), "user_id": user_id}
        except Exception:
            return False

        result = await self.resumes_collection.delete_one(query)
        if result.deleted_count > 0:
            # Also clean up associated file records
            await self.files_collection.delete_many({"resume_id": resume_id, "user_id": user_id})
            return True
        return False

    async def duplicate(self, resume_id: str, user_id: str) -> Optional[ResumeDocument]:
        original = await self.find_by_id(resume_id, user_id)
        if not original:
            return None

        dup_data = original.model_dump(exclude={"id"})
        dup_data["title"] = f"{original.title} (Copy)"
        dup_data["created_at"] = datetime.now(timezone.utc)
        dup_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.resumes_collection.insert_one(dup_data)
        dup_data["_id"] = str(result.inserted_id)
        return ResumeDocument(**dup_data)

    async def create_file(self, file_doc: ResumeFileDocument) -> ResumeFileDocument:
        doc = file_doc.model_dump(by_alias=True, exclude={"id"})
        doc["created_at"] = datetime.now(timezone.utc)
        result = await self.files_collection.insert_one(doc)
        file_doc.id = str(result.inserted_id)
        return file_doc

    async def list_files(self, resume_id: str, user_id: str) -> List[ResumeFileDocument]:
        cursor = self.files_collection.find({"resume_id": resume_id, "user_id": user_id}).sort("created_at", -1)
        files = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            files.append(ResumeFileDocument(**doc))
        return files

    async def find_file_by_id(self, file_id: str, resume_id: str, user_id: str) -> Optional[ResumeFileDocument]:
        try:
            query = {"_id": ObjectId(file_id), "resume_id": resume_id, "user_id": user_id}
        except Exception:
            return None
        doc = await self.files_collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            return ResumeFileDocument(**doc)
        return None

    async def delete_file(self, file_id: str, resume_id: str, user_id: str) -> bool:
        try:
            query = {"_id": ObjectId(file_id), "resume_id": resume_id, "user_id": user_id}
        except Exception:
            return False
        result = await self.files_collection.delete_one(query)
        return result.deleted_count > 0


resume_repository = ResumeRepository()
