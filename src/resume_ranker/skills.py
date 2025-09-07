
from typing import Iterable
from rapidfuzz import fuzz

def score_skills(text: str, skills: Iterable[str]) -> float:
    text_low = text.lower()
    skills_list = list(skills)
    hits = 0
    for s in skills_list:
        s_low = s.lower()
        exact = s_low in text_low
        fuzzy = fuzz.partial_ratio(s_low, text_low) > 90
        hits += 1 if (exact or fuzzy) else 0
    return hits / max(len(skills_list), 1)
