import logging
from typing import List, Dict, Any

logger = logging.getLogger("knora.ai")


class ResumeAIService:
    def improve_summary(self, text: str, target_role: str = "") -> str:
        """
        Enhances professional summary text with strong impact and professional vocabulary.
        """
        if not text or not text.strip():
            role_title = target_role if target_role else "Software & Technology Professional"
            return f"Motivated {role_title} with strong technical foundation in modern software development, web applications, and problem solving. Proven track record of building reliable projects and collaborating effectively."
        
        cleaned = text.strip()
        if not cleaned.endswith("."):
            cleaned += "."
            
        return f"Results-driven software developer specializing in scalable web solutions. {cleaned} Committed to engineering high-quality code and leveraging cutting-edge tools to deliver impactful user experiences."

    def improve_bullet(self, bullet: str) -> str:
        """
        Transforms a basic bullet point into an ATS-friendly impact statement with action verbs.
        """
        if not bullet or not bullet.strip():
            return "Engineered scalable features using modern frameworks, improving system responsiveness and overall user experience."

        cleaned = bullet.strip().lstrip("•-").strip()
        
        action_map = {
            "make": "Architected and built",
            "made": "Engineered and deployed",
            "work": "Collaborated on designing",
            "worked": "Spearheaded the development of",
            "use": "Leveraged",
            "used": "Utilized",
            "help": "Facilitated",
            "create": "Conceived and implemented"
        }

        first_word = cleaned.split()[0].lower() if cleaned else ""
        if first_word in action_map:
            words = cleaned.split()
            words[0] = action_map[first_word]
            cleaned = " ".join(words)

        if not any(char.isdigit() for char in cleaned):
            cleaned += ", enhancing application performance and reducing processing overhead by 25%."
        elif not cleaned.endswith("."):
            cleaned += "."

        return cleaned

    def generate_project_description(self, title: str, technologies: str, raw_desc: str) -> str:
        """
        Generates a clear 2-3 sentence project description highlighting technical stack and outcome.
        """
        tech_str = f" using {technologies}" if technologies else ""
        base = raw_desc.strip() if raw_desc else f"Built {title}"
        return f"{base}{tech_str}. Implemented secure REST APIs, optimized database queries, and designed an intuitive user interface to ensure high availability and smooth performance."

    def suggest_skills(self, existing_skills: List[str], target_role: str = "") -> List[str]:
        """
        Suggests relevant technical skills based on existing skills and target role.
        """
        existing_lower = [s.lower() for s in existing_skills]
        pool = ["Data Structures", "Algorithms", "React", "FastAPI", "Python", "Node.js", "MongoDB", "Git", "Docker", "REST APIs", "TypeScript", "SQL"]
        
        suggestions = [sk for sk in pool if sk.lower() not in existing_lower]
        return suggestions[:5]

    def improve_grammar(self, text: str) -> str:
        """
        Fixes basic formatting, capitalization, and punctuation.
        """
        if not text:
            return ""
        lines = text.split("\n")
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                capitalized = stripped[0].upper() + stripped[1:]
                if not capitalized.endswith((".", "!", "?")):
                    capitalized += "."
                fixed_lines.append(capitalized)
        return "\n".join(fixed_lines)


resume_ai_service = ResumeAIService()
