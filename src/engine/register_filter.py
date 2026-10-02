"""
Register, Sociolect, and Lexical Filter for Upstage.
"""

import re
from typing import Dict, List

ANACHRONISTIC_MODERNISMS = [
    "psychology", "psychological", "trauma", "traumatic", "narcissistic",
    "societal", "perspective", "unconscious", "subconscious", "concept",
    "ideology", "systemic", "existential", "identity", "relationship",
    "ego", "projection", "coping", "mechanisms", "toxic", "validation"
]

FALSTAFFIAN_LEXICAL_MARKERS = [
    "sack", "sherris", "capon", "belly", "knave", "rogue", "honour",
    "villanous", "hal", "sugar", "gout", "fat", "quoth", "alas",
    "marry", "prithee", "by the mass", "i'faith", "scutcheon"
]


class RegisterFilter:
    @staticmethod
    def audit_pronominal_address(
        text: str,
        speaker_rank: str,
        addressee_rank: str,
        affect: str = "neutral"
    ) -> Dict[str, any]:
        tokens = re.findall(r"\b[a-zA-Z']+\b", text.lower())
        t_forms = sum(1 for tok in tokens if tok in {"thou", "thee", "thy", "thine", "thyself"})
        v_forms = sum(1 for tok in tokens if tok in {"you", "ye", "your", "yours", "yourself"})

        is_superior = any(k in addressee_rank.lower() for k in ["king", "monarch", "duke", "prince"])
        expected_form = "V" if is_superior and affect != "comic_intimacy" else "flexible"
        status_flag = "COMPLIANT"
        if expected_form == "V" and t_forms > v_forms and affect not in ("affectionate_familiarity", "comic_insolence"):
            status_flag = "AUDIT_WARNING: High T-form frequency towards royal superior."

        return {
            "t_count": t_forms,
            "v_count": v_forms,
            "predominant_form": "T" if t_forms > v_forms else ("V" if v_forms > t_forms else "BALANCED"),
            "expected_form": expected_form,
            "status": status_flag
        }

    @staticmethod
    def detect_anachronisms(text: str) -> List[str]:
        tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
        return [w for w in ANACHRONISTIC_MODERNISMS if w in tokens]

    @staticmethod
    def measure_falstaffian_density(text: str) -> float:
        tokens = re.findall(r"\b[a-zA-Z']+\b", text.lower())
        if not tokens:
            return 0.0
        matches = sum(1 for tok in tokens if tok in FALSTAFFIAN_LEXICAL_MARKERS)
        return round((matches / len(tokens)) * 100, 2)
