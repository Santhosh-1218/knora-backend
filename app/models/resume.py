from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
import uuid


class PersonalInfo(BaseModel):
    firstName: str = ""
    lastName: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""


class Education(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    institution: str = ""
    degree: str = ""
    field: str = ""
    location: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    currentlyStudying: bool = False
    grade: Optional[str] = ""
    description: Optional[str] = ""


class Experience(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company: str = ""
    position: str = ""
    location: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    currentlyWorking: bool = False
    description: Optional[str] = ""
    achievements: List[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    role: Optional[str] = ""
    description: str = ""
    technologies: str = ""
    githubUrl: Optional[str] = ""
    liveUrl: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""


class Skill(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = "Technical"
    level: str = "Intermediate"


class Certification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    issuer: str = ""
    issueDate: Optional[str] = ""
    expiryDate: Optional[str] = ""
    credentialId: Optional[str] = ""
    credentialUrl: Optional[str] = ""


class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    organization: Optional[str] = ""
    date: Optional[str] = ""
    description: Optional[str] = ""


class Language(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    language: str = ""
    proficiency: str = "Fluent"


class CustomSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    items: List[str] = Field(default_factory=list)


class FormattingSettings(BaseModel):
    templateId: str = "knora-modern"
    font: str = "Inter"
    fontSize: str = "normal"  # small, normal, large
    headingSize: str = "normal"
    lineHeight: str = "normal"
    margin: str = "normal"  # compact, normal, spacious
    sectionSpacing: str = "normal"
    accentColor: str = "#1A73E8"
    paperSize: str = "A4"


class ResumeDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    title: str = "Untitled Resume"
    template_id: str = "knora-modern"
    status: str = "draft"  # "draft", "complete"
    
    target_job_title: Optional[str] = ""
    target_company: Optional[str] = ""
    target_job_description: Optional[str] = ""
    
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    achievements: List[Achievement] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    custom_sections: List[CustomSection] = Field(default_factory=list)
    formatting: FormattingSettings = Field(default_factory=FormattingSettings)

    completion_score: int = 0
    ats_score: int = 0

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)


class ResumeFileDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    resume_id: str
    user_id: str
    type: str  # "pdf" or "docx"
    object_key: str
    file_name: str
    mime_type: str
    size: int = 0
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)
