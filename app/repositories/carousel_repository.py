from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.db.mongodb import get_database
from app.core.logging import logger

DEFAULT_CAROUSEL_SLIDES = [
    {
        "_id": "slide_1",
        "title": "1,000+ Academic Videos & Notes",
        "subtitle": "Structured learning content for university engineering students across all B.Tech branches.",
        "badge": "ACADEMICS",
        "ctaText": "Explore Academics",
        "targetPath": "/academics",
        "isPublic": True,
        "featureName": None,
        "iconName": "BookOpen",
        "accentColor": "#1A73E8",
        "bgImage": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1400&q=80",
        "order": 1,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": "slide_2",
        "title": "Build Your ATS-Friendly Resume",
        "subtitle": "Create a professional, recruiter-approved resume formatted for top tech companies.",
        "badge": "RESUME BUILDER",
        "ctaText": "Build Resume",
        "targetPath": "/student-corner/resume/maker",
        "isPublic": False,
        "featureName": "Resume Builder",
        "iconName": "FileText",
        "accentColor": "#38bdf8",
        "bgImage": "https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&w=1400&q=80",
        "order": 2,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": "slide_3",
        "title": "Check Your ATS Score with AI",
        "subtitle": "Compare your resume with real job descriptions to identify missing keywords and boost match score.",
        "badge": "ATS SCORE ANALYZER",
        "ctaText": "Check Resume",
        "targetPath": "/student-corner/ats-checker",
        "isPublic": False,
        "featureName": "ATS Resume Checker",
        "iconName": "SearchCheck",
        "accentColor": "#34d399",
        "bgImage": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1400&q=80",
        "order": 3,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": "slide_4",
        "title": "Build Your Developer Portfolio with AI",
        "subtitle": "Publish your personalized developer portfolio site in less than 2 minutes.",
        "badge": "AI PORTFOLIO BUILDER",
        "ctaText": "Build Portfolio",
        "targetPath": "/student-corner/portfolio",
        "isPublic": False,
        "featureName": "Portfolio Builder",
        "iconName": "Globe",
        "accentColor": "#a78bfa",
        "bgImage": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=1400&q=80",
        "order": 4,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": "slide_5",
        "title": "Discover Top Jobs & Internships",
        "subtitle": "Find software engineering internships and fresher roles tailored to your B.Tech branch.",
        "badge": "CAREER MARKETPLACE",
        "ctaText": "Explore Jobs",
        "targetPath": "/student-corner/jobs",
        "isPublic": False,
        "featureName": "Job Portal",
        "iconName": "Briefcase",
        "accentColor": "#f472b6",
        "bgImage": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1400&q=80",
        "order": 5,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": "slide_6",
        "title": "Meet Guru.AI — Your 24/7 AI Student Assistant",
        "subtitle": "Solve doubts, explain complex code, generate study notes, and prepare for interviews.",
        "badge": "GURU.AI TUTOR",
        "ctaText": "Try Guru.AI",
        "targetPath": "/guru-ai",
        "isPublic": False,
        "featureName": "Guru.AI Assistant",
        "iconName": "Sparkles",
        "accentColor": "#1A73E8",
        "bgImage": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1400&q=80",
        "order": 6,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": "slide_7",
        "title": "Discover Hackathons & Tech Events",
        "subtitle": "Find AI summits, coding competitions, developer conferences, and placement masterclasses.",
        "badge": "HACKATHONS & EVENTS",
        "ctaText": "Explore Events",
        "targetPath": "/student-corner/events",
        "isPublic": False,
        "featureName": "Hackathons & Events",
        "iconName": "Trophy",
        "accentColor": "#fbbf24",
        "bgImage": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1400&q=80",
        "order": 7,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]


class CarouselRepository:
    def __init__(self):
        self.collection_name = "carousel_slides"

    @property
    def collection(self):
        return get_database()[self.collection_name]

    async def seed_if_empty(self):
        count = await self.collection.count_documents({})
        if count == 0:
            logger.info("Seeding initial carousel slides in MongoDB...")
            await self.collection.insert_many(DEFAULT_CAROUSEL_SLIDES)

    async def get_active_slides(self) -> List[dict]:
        await self.seed_if_empty()
        cursor = self.collection.find({"isActive": True}).sort("order", 1)
        slides = await cursor.to_list(length=100)
        for s in slides:
            s["id"] = str(s["_id"])
        return slides

    async def get_all_slides(self) -> List[dict]:
        await self.seed_if_empty()
        cursor = self.collection.find().sort("order", 1)
        slides = await cursor.to_list(length=100)
        for s in slides:
            s["id"] = str(s["_id"])
        return slides

    async def create_slide(self, slide_data: dict) -> dict:
        slide_data["created_at"] = datetime.utcnow()
        slide_data["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(slide_data)
        slide_data["id"] = str(result.inserted_id)
        return slide_data

    async def update_slide(self, slide_id: str, update_data: dict) -> Optional[dict]:
        update_data["updated_at"] = datetime.utcnow()
        query = {"_id": ObjectId(slide_id)} if ObjectId.is_valid(slide_id) else {"_id": slide_id}
        
        await self.collection.update_one(query, {"$set": update_data})
        slide = await self.collection.find_one(query)
        if slide:
            slide["id"] = str(slide["_id"])
        return slide

    async def delete_slide(self, slide_id: str) -> bool:
        query = {"_id": ObjectId(slide_id)} if ObjectId.is_valid(slide_id) else {"_id": slide_id}
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0
