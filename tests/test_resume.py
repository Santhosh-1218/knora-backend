import pytest
from app.models.resume import ResumeDocument, PersonalInfo, Education, Project, Skill
from app.services.pdf_service import pdf_service
from app.services.docx_service import docx_service
from app.services.ats_service import ats_service
from app.services.resume_ai_service import resume_ai_service
from app.repositories.resume_repository import resume_repository


@pytest.mark.asyncio
async def test_pdf_generation_service():
    sample_resume = ResumeDocument(
        user_id="user_123",
        title="Test Resume",
        template_id="knora-modern",
        personal_info=PersonalInfo(
            firstName="John",
            lastName="Doe",
            email="john@example.com",
            phone="+1234567890",
            location="New York, USA",
            linkedin="linkedin.com/in/johndoe",
            github="github.com/johndoe"
        ),
        summary="Experienced Fullstack Software Developer.",
        education=[
            Education(
                institution="MIT",
                degree="B.S.",
                field="Computer Science",
                startDate="2020",
                endDate="2024"
            )
        ],
        projects=[
            Project(
                title="Knora Platform",
                role="Lead Engineer",
                description="Built high-performance ATS resume tools.",
                technologies="Python, FastAPI, React"
            )
        ],
        skills=[
            Skill(name="Python", category="Backend"),
            Skill(name="React", category="Frontend")
        ]
    )

    pdf_bytes = pdf_service.generate_pdf(sample_resume)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_docx_generation_service():
    sample_resume = ResumeDocument(
        user_id="user_123",
        title="Test Resume Word",
        template_id="knora-ats",
        personal_info=PersonalInfo(
            firstName="Jane",
            lastName="Smith",
            email="jane@example.com",
            phone="+1987654321",
            location="San Francisco, CA"
        ),
        summary="Data Analyst specializing in SQL and Python dashboards.",
        skills=[Skill(name="SQL"), Skill(name="Python")]
    )

    docx_bytes = docx_service.generate_docx(sample_resume)
    assert docx_bytes is not None
    assert len(docx_bytes) > 0
    assert docx_bytes[:2] == b"PK"  # Zip archive header for docx


@pytest.mark.asyncio
async def test_ats_analysis_service():
    sample_resume = ResumeDocument(
        user_id="user_123",
        title="ATS Check Resume",
        personal_info=PersonalInfo(
            firstName="Alex",
            lastName="Taylor",
            email="alex@example.com",
            phone="+1555000111",
            linkedin="linkedin.com/in/alextaylor"
        ),
        summary="Engineered scalable backend systems with Python and FastAPI.",
        education=[Education(degree="B.Tech", institution="JNTUH")],
        skills=[Skill(name="Python"), Skill(name="FastAPI"), Skill(name="Docker")]
    )

    analysis = ats_service.calculate_ats_score(sample_resume)
    assert "overallScore" in analysis
    assert analysis["overallScore"] > 50
    assert "passed" in analysis

    # Test job tailoring
    jd = "Looking for a Python software engineer with FastAPI, Docker, and SQL experience."
    tailored = ats_service.tailor_job_description(sample_resume, jd)
    assert "matchPercentage" in tailored
    assert "Python" in tailored["matchedSkills"]


@pytest.mark.asyncio
async def test_ai_writing_service():
    basic_summary = "I am a computer science student."
    enhanced = resume_ai_service.improve_summary(basic_summary, "Software Developer")
    assert len(enhanced) > len(basic_summary)

    bullet = "made the frontend and fixed bugs"
    improved_bullet = resume_ai_service.improve_bullet(bullet)
    assert "Engineered" in improved_bullet or "Architected" in improved_bullet


@pytest.mark.asyncio
async def test_resume_repository_crud():
    user_id = "user_test_999"
    new_resume = ResumeDocument(
        user_id=user_id,
        title="Dev Resume",
        template_id="knora-modern"
    )

    created = await resume_repository.create(new_resume)
    assert created.id is not None

    fetched = await resume_repository.find_by_id(created.id, user_id)
    assert fetched is not None
    assert fetched.title == "Dev Resume"

    updated = await resume_repository.update(created.id, user_id, {"title": "Updated Dev Resume"})
    assert updated.title == "Updated Dev Resume"

    user_resumes = await resume_repository.list_by_user(user_id)
    assert len(user_resumes) == 1

    duplicated = await resume_repository.duplicate(created.id, user_id)
    assert duplicated is not None
    assert "Copy" in duplicated.title

    deleted = await resume_repository.delete(created.id, user_id)
    assert deleted is True
