import io
import logging
from xhtml2pdf import pisa
from app.models.resume import ResumeDocument

logger = logging.getLogger("knora.pdf")


class PDFService:
    def generate_pdf(self, resume: ResumeDocument) -> bytes:
        """
        Renders a structured ResumeDocument into a high-quality, text-selectable A4 PDF byte string.
        """
        html_content = self._render_resume_to_html(resume)
        
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            io.StringIO(html_content),
            dest=pdf_buffer,
            encoding='utf-8'
        )
        
        if pisa_status.err:
            logger.error(f"Error generating PDF for resume {resume.id}: {pisa_status.err}")
            raise RuntimeError("Failed to generate PDF document from resume content.")
            
        return pdf_buffer.getvalue()

    def _render_resume_to_html(self, resume: ResumeDocument) -> str:
        p = resume.personal_info
        f = resume.formatting

        font_family = f.font if f.font in ["Inter", "Roboto", "Helvetica", "Georgia", "Times-Roman"] else "Helvetica"
        accent_color = f.accentColor or "#1A73E8"
        paper_size = f.paperSize or "A4"

        # Generate HTML structure matching template layout
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: {paper_size} portrait;
        margin: 12mm 15mm 12mm 15mm;
    }}
    body {{
        font-family: '{font_family}', sans-serif;
        color: #1f2937;
        font-size: 10pt;
        line-height: 1.4;
        margin: 0;
        padding: 0;
    }}
    a {{
        color: {accent_color};
        text-decoration: none;
    }}
    .header {{
        border-bottom: 2px solid {accent_color};
        padding-bottom: 8px;
        margin-bottom: 12px;
    }}
    .name {{
        font-size: 20pt;
        font-weight: bold;
        color: #111827;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}
    .contact-line {{
        font-size: 9pt;
        color: #4b5563;
    }}
    .section-title {{
        font-size: 11pt;
        font-weight: bold;
        color: {accent_color};
        text-transform: uppercase;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 3px;
        margin-top: 10px;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }}
    .summary-text {{
        font-size: 9.5pt;
        color: #374151;
        margin-bottom: 8px;
        text-align: justify;
    }}
    .item {{
        margin-bottom: 8px;
    }}
    .item-header {{
        width: 100%;
        margin-bottom: 2px;
    }}
    .item-title {{
        font-weight: bold;
        font-size: 10pt;
        color: #111827;
    }}
    .item-sub {{
        font-weight: bold;
        font-size: 9.5pt;
        color: #4b5563;
    }}
    .item-date {{
        float: right;
        font-size: 9pt;
        color: #6b7280;
        font-style: italic;
    }}
    .item-desc {{
        font-size: 9pt;
        color: #374151;
        margin-top: 2px;
    }}
    ul {{
        margin: 3px 0 6px 16px;
        padding: 0;
    }}
    li {{
        font-size: 9pt;
        color: #374151;
        margin-bottom: 2px;
    }}
    .skills-group {{
        margin-bottom: 4px;
    }}
    .skills-cat {{
        font-weight: bold;
        font-size: 9pt;
        color: #111827;
    }}
    .skills-list {{
        font-size: 9pt;
        color: #374151;
    }}
</style>
</head>
<body>

    <!-- Header Section -->
    <div class="header">
        <div class="name">{p.firstName} {p.lastName}</div>
        <div class="contact-line">
            {[item for item in [p.email, p.phone, p.location] if item]}
            {(' &bull; ' + p.linkedin) if p.linkedin else ''}
            {(' &bull; ' + p.github) if p.github else ''}
            {(' &bull; ' + p.portfolio) if p.portfolio else ''}
        </div>
    </div>
"""

        # Professional Summary
        if resume.summary and resume.summary.strip():
            html += f"""
    <div class="section-title">Professional Summary</div>
    <div class="summary-text">{resume.summary.strip()}</div>
"""

        # Education
        if resume.education:
            html += '<div class="section-title">Education</div>'
            for edu in resume.education:
                dates = f"{edu.startDate or ''} - {'Present' if edu.currentlyStudying else (edu.endDate or '')}"
                grade_str = f" &bull; GPA/Grade: {edu.grade}" if edu.grade else ""
                html += f"""
    <div class="item">
        <div class="item-header">
            <span class="item-title">{edu.degree} {f"in {edu.field}" if edu.field else ""}</span>
            <span class="item-date">{dates}</span>
        </div>
        <div class="item-sub">{edu.institution}{f", {edu.location}" if edu.location else ""}{grade_str}</div>
        {f'<div class="item-desc">{edu.description}</div>' if edu.description else ''}
    </div>
"""

        # Experience
        if resume.experience:
            html += '<div class="section-title">Experience</div>'
            for exp in resume.experience:
                dates = f"{exp.startDate or ''} - {'Present' if exp.currentlyWorking else (exp.endDate or '')}"
                html += f"""
    <div class="item">
        <div class="item-header">
            <span class="item-title">{exp.position}</span>
            <span class="item-date">{dates}</span>
        </div>
        <div class="item-sub">{exp.company}{f", {exp.location}" if exp.location else ""}</div>
        {f'<div class="item-desc">{exp.description}</div>' if exp.description else ''}
"""
                if exp.achievements:
                    html += "<ul>"
                    for ach in exp.achievements:
                        if ach.strip():
                            html += f"<li>{ach.strip()}</li>"
                    html += "</ul>"
                html += "</div>"

        # Projects
        if resume.projects:
            html += '<div class="section-title">Projects</div>'
            for proj in resume.projects:
                dates = f"{proj.startDate or ''} - {proj.endDate or ''}" if proj.startDate else ""
                tech_str = f" | <em>Tech: {proj.technologies}</em>" if proj.technologies else ""
                html += f"""
    <div class="item">
        <div class="item-header">
            <span class="item-title">{proj.title}</span>
            {f'<span class="item-date">{dates}</span>' if dates else ''}
        </div>
        <div class="item-sub">{proj.role if proj.role else 'Developer'}{tech_str}</div>
        <div class="item-desc">{proj.description}</div>
    </div>
"""

        # Technical Skills
        if resume.skills:
            html += '<div class="section-title">Skills & Technologies</div>'
            categories = {}
            for sk in resume.skills:
                cat = sk.category or "Technical"
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(sk.name)
            
            for cat, sk_list in categories.items():
                html += f"""
    <div class="skills-group">
        <span class="skills-cat">{cat}:</span>
        <span class="skills-list">{", ".join(sk_list)}</span>
    </div>
"""

        # Certifications
        if resume.certifications:
            html += '<div class="section-title">Certifications</div>'
            for cert in resume.certifications:
                date_str = f" ({cert.issueDate})" if cert.issueDate else ""
                issuer_str = f" &bull; {cert.issuer}" if cert.issuer else ""
                html += f"""
    <div class="item">
        <span class="item-title">{cert.name}</span>
        <span class="item-sub">{issuer_str}{date_str}</span>
    </div>
"""

        # Achievements
        if resume.achievements:
            html += '<div class="section-title">Honors & Achievements</div>'
            for ach in resume.achievements:
                html += f"""
    <div class="item">
        <span class="item-title">{ach.title}</span>
        {f'<span class="item-sub"> &bull; {ach.organization}</span>' if ach.organization else ''}
        {f'<div class="item-desc">{ach.description}</div>' if ach.description else ''}
    </div>
"""

        # Languages
        if resume.languages:
            html += '<div class="section-title">Languages</div>'
            lang_strs = [f"<strong>{l.language}</strong> ({l.proficiency})" for l in resume.languages if l.language]
            html += f'<div class="skills-list">{" &bull; ".join(lang_strs)}</div>'

        # Custom Sections
        if resume.custom_sections:
            for cs in resume.custom_sections:
                if cs.title:
                    html += f'<div class="section-title">{cs.title}</div>'
                    if cs.items:
                        html += "<ul>"
                        for itm in cs.items:
                            html += f"<li>{itm}</li>"
                        html += "</ul>"

        html += """
</body>
</html>
"""
        return html


pdf_service = PDFService()
