import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel

from app.core.exceptions import KnoraException, PermissionDeniedError, NotFoundError
from app.models.user import UserDocument
from app.models.resume import ResumeDocument, ResumeFileDocument
from app.repositories.resume_repository import resume_repository
from app.routes.deps import get_current_user
from app.schemas.response import APIResponse
from app.services.pdf_service import pdf_service
from app.services.docx_service import docx_service
from app.services.r2_service import r2_storage_service
from app.services.ats_service import ats_service
from app.services.resume_ai_service import resume_ai_service

logger = logging.getLogger("knora.resumes")

resume_router = APIRouter(prefix="/api/resumes", tags=["Resume Maker"])


class CreateResumeRequest(BaseModel):
    title: Optional[str] = "My Resume"
    templateId: Optional[str] = "knora-modern"


class UpdateResumeRequest(BaseModel):
    title: Optional[str] = None
    template_id: Optional[str] = None
    status: Optional[str] = None
    target_job_title: Optional[str] = None
    target_company: Optional[str] = None
    target_job_description: Optional[str] = None
    personal_info: Optional[dict] = None
    summary: Optional[str] = None
    education: Optional[list] = None
    experience: Optional[list] = None
    projects: Optional[list] = None
    skills: Optional[list] = None
    certifications: Optional[list] = None
    achievements: Optional[list] = None
    languages: Optional[list] = None
    custom_sections: Optional[list] = None
    formatting: Optional[dict] = None


class AIEnhanceRequest(BaseModel):
    action: str  # "summary", "bullet", "project", "grammar", "suggest_skills"
    text: Optional[str] = ""
    target_role: Optional[str] = ""
    technologies: Optional[str] = ""
    title: Optional[str] = ""
    existing_skills: Optional[List[str]] = []


class JobTailorRequest(BaseModel):
    job_description: str


@resume_router.post("", response_model=APIResponse)
async def create_resume(
    payload: CreateResumeRequest,
    current_user: UserDocument = Depends(get_current_user)
):
    """Creates a new empty resume document for the authenticated user."""
    resume = ResumeDocument(
        user_id=str(current_user.id),
        title=payload.title or "My Resume",
        template_id=payload.templateId or "knora-modern",
        personal_info={
            "firstName": current_user.full_name.split()[0] if current_user.full_name else "",
            "lastName": " ".join(current_user.full_name.split()[1:]) if current_user.full_name and len(current_user.full_name.split()) > 1 else "",
            "email": current_user.email or "",
            "phone": current_user.mobile or ""
        }
    )
    
    created = await resume_repository.create(resume)
    return APIResponse(
        success=True,
        message="Resume created successfully",
        data=created.model_dump(by_alias=True)
    )


@resume_router.get("", response_model=APIResponse)
async def list_resumes(
    current_user: UserDocument = Depends(get_current_user)
):
    """Lists all resumes created by the authenticated user."""
    resumes = await resume_repository.list_by_user(str(current_user.id))
    return APIResponse(
        success=True,
        message="Resumes fetched successfully",
        data=[r.model_dump(by_alias=True) for r in resumes]
    )


@resume_router.get("/{id}", response_model=APIResponse)
async def get_resume(
    id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Fetches a specific resume belonging to the authenticated user."""
    resume = await resume_repository.find_by_id(id, str(current_user.id))
    if not resume:
        raise NotFoundError("Resume not found or access denied.")
    return APIResponse(
        success=True,
        message="Resume details fetched",
        data=resume.model_dump(by_alias=True)
    )


@resume_router.patch("/{id}", response_model=APIResponse)
async def update_resume(
    id: str,
    payload: UpdateResumeRequest,
    current_user: UserDocument = Depends(get_current_user)
):
    """Updates / autosaves resume fields for the authenticated user."""
    existing = await resume_repository.find_by_id(id, str(current_user.id))
    if not existing:
        raise NotFoundError("Resume not found or access denied.")

    update_dict = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    
    # Recalculate ATS & Completion scores upon save
    updated_resume = await resume_repository.update(id, str(current_user.id), update_dict)
    
    # Calculate scores
    scores = ats_service.calculate_ats_score(updated_resume)
    await resume_repository.update(id, str(current_user.id), {
        "ats_score": scores["overallScore"],
        "completion_score": scores["completeness"]
    })
    updated_resume.ats_score = scores["overallScore"]
    updated_resume.completion_score = scores["completeness"]

    return APIResponse(
        success=True,
        message="Resume updated successfully",
        data=updated_resume.model_dump(by_alias=True)
    )


@resume_router.delete("/{id}", response_model=APIResponse)
async def delete_resume(
    id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Deletes a resume and associated file records for the authenticated user."""
    deleted = await resume_repository.delete(id, str(current_user.id))
    if not deleted:
        raise NotFoundError("Resume not found or access denied.")
    return APIResponse(
        success=True,
        message="Resume deleted successfully",
        data={"id": id}
    )


@resume_router.post("/{id}/duplicate", response_model=APIResponse)
async def duplicate_resume(
    id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Duplicates an existing resume for the authenticated user."""
    duplicated = await resume_repository.duplicate(id, str(current_user.id))
    if not duplicated:
        raise NotFoundError("Resume not found or access denied.")
    return APIResponse(
        success=True,
        message="Resume duplicated successfully",
        data=duplicated.model_dump(by_alias=True)
    )


@resume_router.post("/{id}/generate/pdf", response_model=APIResponse)
async def generate_pdf_and_upload(
    id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """
    Renders server-side PDF for the resume, uploads to Cloudflare R2 bucket,
    creates a ResumeFile metadata record, and returns a short-lived presigned download URL.
    """
    resume = await resume_repository.find_by_id(id, str(current_user.id))
    if not resume:
        raise NotFoundError("Resume not found or access denied.")

    pdf_bytes = pdf_service.generate_pdf(resume)
    
    # Calculate file versioning
    existing_files = await resume_repository.list_files(id, str(current_user.id))
    pdf_count = sum(1 for f in existing_files if f.type == "pdf") + 1
    
    version_str = f"v{pdf_count}"
    safe_title = "".join(c for c in resume.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    file_name = f"{safe_title}_{version_str}.pdf"
    
    object_key = f"users/{current_user.id}/resumes/{id}/pdf/{version_str}_{file_name}"

    # Upload to Cloudflare R2
    r2_storage_service.upload_file(pdf_bytes, object_key, content_type="application/pdf")

    # Create file metadata record
    file_doc = ResumeFileDocument(
        resume_id=id,
        user_id=str(current_user.id),
        type="pdf",
        object_key=object_key,
        file_name=file_name,
        mime_type="application/pdf",
        size=len(pdf_bytes),
        version=pdf_count
    )
    saved_file = await resume_repository.create_file(file_doc)

    # Generate presigned download URL (15 minutes)
    presigned_url = r2_storage_service.generate_presigned_url(object_key, expiration=900)

    return APIResponse(
        success=True,
        message="PDF generated and uploaded to Cloudflare R2 successfully",
        data={
            "file": saved_file.model_dump(by_alias=True),
            "download_url": presigned_url
        }
    )


@resume_router.post("/{id}/generate/docx", response_model=APIResponse)
async def generate_docx_and_upload(
    id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """
    Renders native Microsoft Word .docx file, uploads to Cloudflare R2,
    creates a ResumeFile record, and returns a short-lived presigned download URL.
    """
    resume = await resume_repository.find_by_id(id, str(current_user.id))
    if not resume:
        raise NotFoundError("Resume not found or access denied.")

    docx_bytes = docx_service.generate_docx(resume)
    
    existing_files = await resume_repository.list_files(id, str(current_user.id))
    docx_count = sum(1 for f in existing_files if f.type == "docx") + 1
    
    version_str = f"v{docx_count}"
    safe_title = "".join(c for c in resume.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    file_name = f"{safe_title}_{version_str}.docx"
    
    object_key = f"users/{current_user.id}/resumes/{id}/docx/{version_str}_{file_name}"

    # Upload to Cloudflare R2
    r2_storage_service.upload_file(docx_bytes, object_key, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    # Save file metadata
    file_doc = ResumeFileDocument(
        resume_id=id,
        user_id=str(current_user.id),
        type="docx",
        object_key=object_key,
        file_name=file_name,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size=len(docx_bytes),
        version=docx_count
    )
    saved_file = await resume_repository.create_file(file_doc)

    presigned_url = r2_storage_service.generate_presigned_url(object_key, expiration=900)

    return APIResponse(
        success=True,
        message="DOCX generated and uploaded to Cloudflare R2 successfully",
        data={
            "file": saved_file.model_dump(by_alias=True),
            "download_url": presigned_url
        }
    )


@resume_router.get("/{id}/files", response_model=APIResponse)
async def list_resume_files(
    id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Lists all generated PDF/DOCX file records for a resume."""
    resume = await resume_repository.find_by_id(id, str(current_user.id))
    if not resume:
        raise NotFoundError("Resume not found or access denied.")

    files = await resume_repository.list_files(id, str(current_user.id))
    return APIResponse(
        success=True,
        message="Resume files listed",
        data=[f.model_dump(by_alias=True) for f in files]
    )


@resume_router.get("/{id}/files/{file_id}/download", response_model=APIResponse)
async def get_download_url(
    id: str,
    file_id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Generates a secure presigned GET download URL for an R2 object."""
    file_doc = await resume_repository.find_file_by_id(file_id, id, str(current_user.id))
    if not file_doc:
        raise NotFoundError("File record not found or access denied.")

    url = r2_storage_service.generate_presigned_url(file_doc.object_key, expiration=900)
    if not url:
        raise HTTPException(status_code=500, detail="Could not generate presigned download URL.")

    return APIResponse(
        success=True,
        message="Presigned download URL generated",
        data={"download_url": url, "file": file_doc.model_dump(by_alias=True)}
    )


@resume_router.delete("/{id}/files/{file_id}", response_model=APIResponse)
async def delete_resume_file(
    id: str,
    file_id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Deletes a generated file record and removes object from Cloudflare R2."""
    file_doc = await resume_repository.find_file_by_id(file_id, id, str(current_user.id))
    if not file_doc:
        raise NotFoundError("File record not found or access denied.")

    # Remove object from R2
    r2_storage_service.delete_file(file_doc.object_key)

    # Delete database record
    await resume_repository.delete_file(file_id, id, str(current_user.id))

    return APIResponse(
        success=True,
        message="Resume file deleted successfully",
        data={"file_id": file_id}
    )


@resume_router.post("/{id}/ai/enhance", response_model=APIResponse)
async def ai_enhance(
    id: str,
    payload: AIEnhanceRequest,
    current_user: UserDocument = Depends(get_current_user)
):
    """Provides AI text enhancement for summaries, bullet points, and skill suggestions."""
    resume = await resume_repository.find_by_id(id, str(current_user.id))
    if not resume:
        raise NotFoundError("Resume not found or access denied.")

    result = {}
    if payload.action == "summary":
        result["enhancedText"] = resume_ai_service.improve_summary(payload.text or resume.summary, payload.target_role)
    elif payload.action == "bullet":
        result["enhancedText"] = resume_ai_service.improve_bullet(payload.text)
    elif payload.action == "project":
        result["enhancedText"] = resume_ai_service.generate_project_description(payload.title, payload.technologies, payload.text)
    elif payload.action == "grammar":
        result["enhancedText"] = resume_ai_service.improve_grammar(payload.text)
    elif payload.action == "suggest_skills":
        current_skill_names = [s.name for s in resume.skills]
        result["suggestedSkills"] = resume_ai_service.suggest_skills(current_skill_names, payload.target_role)

    return APIResponse(
        success=True,
        message="AI enhancement generated",
        data=result
    )


@resume_router.post("/{id}/ats/analyze", response_model=APIResponse)
async def analyze_ats(
    id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Runs ATS health and quality analysis on the resume."""
    resume = await resume_repository.find_by_id(id, str(current_user.id))
    if not resume:
        raise NotFoundError("Resume not found or access denied.")

    analysis = ats_service.calculate_ats_score(resume)
    return APIResponse(
        success=True,
        message="ATS health analysis complete",
        data=analysis
    )


@resume_router.post("/{id}/tailor", response_model=APIResponse)
async def tailor_job(
    id: str,
    payload: JobTailorRequest,
    current_user: UserDocument = Depends(get_current_user)
):
    """Analyzes job description keywords and returns match score and missing skills."""
    resume = await resume_repository.find_by_id(id, str(current_user.id))
    if not resume:
        raise NotFoundError("Resume not found or access denied.")

    match_result = ats_service.tailor_job_description(resume, payload.job_description)
    
    # Save target job description to resume
    await resume_repository.update(id, str(current_user.id), {
        "target_job_description": payload.job_description
    })

    return APIResponse(
        success=True,
        message="Job description tailoring analysis complete",
        data=match_result
    )
