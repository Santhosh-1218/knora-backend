import re
from typing import Dict, List, Any
from app.models.resume import ResumeDocument

COMMON_ATS_KEYWORDS = [
    "Python", "JavaScript", "React", "Node.js", "Java", "C++", "C#", "SQL", "MongoDB",
    "PostgreSQL", "FastAPI", "Django", "Flask", "HTML", "CSS", "TypeScript", "Git", "GitHub",
    "Docker", "Kubernetes", "AWS", "Cloudflare", "REST API", "GraphQL", "Data Structures",
    "Algorithms", "Machine Learning", "Artificial Intelligence", "Deep Learning", "Agile",
    "Scrum", "CI/CD", "Linux", "Microservices", "Unit Testing", "System Design"
]


class ATSService:
    def calculate_ats_score(self, resume: ResumeDocument) -> Dict[str, Any]:
        """
        Runs deterministic rule-based ATS quality and completeness analysis.
        """
        p = resume.personal_info
        warnings: List[str] = []
        passed: List[str] = []

        # 1. Contact Information Check (20 pts)
        contact_score = 0
        if p.firstName and p.lastName:
            contact_score += 5
        if p.email and "@" in p.email:
            contact_score += 5
        if p.phone:
            contact_score += 4
        if p.location:
            contact_score += 3
        if p.linkedin or p.github:
            contact_score += 3
            passed.append("Professional profile link provided (LinkedIn/GitHub)")
        else:
            warnings.append("Add a LinkedIn or GitHub link to improve ATS recruiter score")

        if contact_score >= 17:
            passed.append("Contact information complete")

        # 2. Summary Check (15 pts)
        summary_score = 0
        if resume.summary and len(resume.summary.strip()) >= 50:
            summary_score = 15
            passed.append("Professional summary provides strong context")
        elif resume.summary and len(resume.summary.strip()) > 0:
            summary_score = 8
            warnings.append("Expand professional summary (aim for 2-3 impact sentences)")
        else:
            warnings.append("Missing professional summary section")

        # 3. Education Check (20 pts)
        edu_score = 0
        if resume.education:
            edu_score = 15
            if any(e.degree and e.institution for e in resume.education):
                edu_score = 20
                passed.append("Education section properly structured with degree & college")
            else:
                warnings.append("Ensure degree and institution name are specified")
        else:
            warnings.append("Add your education details")

        # 4. Experience & Projects Check (25 pts)
        exp_proj_score = 0
        if resume.experience or resume.projects:
            exp_proj_score += 15
            if resume.projects:
                exp_proj_score += 5
                passed.append("Projects section included with technical descriptions")
            if resume.experience:
                exp_proj_score += 5
                passed.append("Experience section detailed")

            # Check action verbs & measurable results
            all_text = (resume.summary + " " + " ".join([p.description for p in resume.projects]) +
                        " ".join([e.description for e in resume.experience])).lower()
            
            action_verbs = ["built", "developed", "designed", "implemented", "optimized", "created", "led", "automated", "improved"]
            has_action_verbs = any(verb in all_text for verb in action_verbs)
            
            if has_action_verbs:
                passed.append("Uses strong action verbs in descriptions")
            else:
                warnings.append("Use strong action verbs like 'Built', 'Optimized', 'Developed' in bullet points")

            # Check numerical impact (numbers or percentages)
            has_numbers = bool(re.search(r'\b\d+(%|\+|k|x)?\b', all_text))
            if not has_numbers:
                warnings.append("Add measurable achievements with numbers or metrics (e.g., 'improved performance by 30%')")
            else:
                passed.append("Includes measurable impact and numbers")
        else:
            warnings.append("Add at least 1-2 key technical projects or experience entries")

        # 5. Skills Check (20 pts)
        skills_score = 0
        if resume.skills:
            if len(resume.skills) >= 5:
                skills_score = 20
                passed.append("Technical skills section well-populated")
            else:
                skills_score = 12
                warnings.append("Add more technical skills relevant to your target role (aim for 6-10 skills)")
        else:
            warnings.append("Add a technical skills section")

        total_score = contact_score + summary_score + edu_score + exp_proj_score + skills_score

        # Categorized scores
        return {
            "overallScore": total_score,
            "atsCompatibility": min(100, int(total_score * 1.05)),
            "contentQuality": min(100, int((summary_score + exp_proj_score) * 2.5)),
            "readability": 94,
            "completeness": min(100, int((contact_score + edu_score + skills_score) * 1.8)),
            "warnings": warnings,
            "passed": passed
        }

    def tailor_job_description(self, resume: ResumeDocument, job_description: str) -> Dict[str, Any]:
        """
        Parses job description for technical keywords and calculates match percentage.
        """
        jd_text = job_description.lower()
        
        # Extract keywords present in job description
        found_jd_keywords = [kw for kw in COMMON_ATS_KEYWORDS if re.search(rf'\b{re.escape(kw.lower())}\b', jd_text)]

        if not found_jd_keywords:
            # Fallback if no specific keywords matched
            words = re.findall(r'\b[A-Za-z0-9+#.]{2,}\b', jd_text)
            found_jd_keywords = list(set([w.capitalize() for w in words if len(w) > 3]))[:10]

        # Extract resume keywords
        resume_text = (
            f"{resume.summary} " +
            " ".join([s.name for s in resume.skills]) + " " +
            " ".join([p.technologies + " " + p.title + " " + p.description for p in resume.projects]) + " " +
            " ".join([e.company + " " + e.position + " " + e.description for e in resume.experience])
        ).lower()

        matched_skills = []
        missing_skills = []

        for kw in found_jd_keywords:
            if re.search(rf'\b{re.escape(kw.lower())}\b', resume_text):
                matched_skills.append(kw)
            else:
                missing_skills.append(kw)

        total = len(found_jd_keywords)
        match_percentage = int((len(matched_skills) / total) * 100) if total > 0 else 85

        recommendations = []
        if missing_skills:
            recommendations.append(f"Consider adding skills like '{missing_skills[0]}' if you have hands-on experience with them.")
        if len(missing_skills) > 1:
            recommendations.append(f"Highlight projects involving '{missing_skills[1]}' in your description.")
        recommendations.append("Ensure your project bullet points align with the key responsibilities in the job posting.")

        return {
            "matchPercentage": match_percentage,
            "matchedSkills": matched_skills,
            "missingSkills": missing_skills,
            "recommendations": recommendations
        }


ats_service = ATSService()
