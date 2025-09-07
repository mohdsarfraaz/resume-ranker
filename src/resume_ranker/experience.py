from __future__ import annotations
import re
import unicodedata
from datetime import datetime
from typing import List, Optional, Tuple

# ── helpers ───────────────────────────────────────────────────────────────────

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

def _norm(text: str) -> str:
    # normalize unicode & unify dashes
    t = unicodedata.normalize("NFKC", text or "")
    return t.replace("—", "-").replace("–", "-").replace("−", "-").replace("’", "'")

def _to_year(val: str) -> Optional[int]:
    val = val.strip().lower()
    if val in {"present", "current", "now", "date", "till date", "to date"}:
        return datetime.now().year
    if re.fullmatch(r"\d{4}", val):
        return int(val)
    if re.fullmatch(r"\d{2}", val):
        # assume 20xx for 2-digit years in resumes
        return 2000 + int(val)
    return None

def _to_month(val: str) -> Optional[int]:
    v = val.strip().lower()
    if v in MONTH_MAP:
        return MONTH_MAP[v]
    if re.fullmatch(r"\d{1,2}", v):
        m = int(v)
        if 1 <= m <= 12:
            return m
    return None

def _to_index(year: int, month: int) -> int:
    # month index for merging: Jan 2000 -> 2000*12 + 0
    return year * 12 + (month - 1)

def _merge(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        ps, pe = merged[-1]
        if s <= pe:  # overlap/touch
            merged[-1] = (ps, max(pe, e))
        else:
            merged.append((s, e))
    return merged

# ── regexes ───────────────────────────────────────────────────────────────────

# e.g., "Aug 2021 - Jun 2024" or "Jun 2024 - Present"
NAME_RANGE_RE = re.compile(
    r"(?P<sm>[A-Za-z]{3,9})\s+(?P<sy>\d{2,4})\s*[-to]+\s*(?P<em>[A-Za-z]{3,9})\s+(?P<ey>\d{2,4}|present|current|now|date)",
    re.IGNORECASE,
)

# e.g., "08/2021 - 06/2024"
NUM_RANGE_RE = re.compile(
    r"(?P<sm>\d{1,2})[\/\.-](?P<sy>\d{2,4})\s*[-to]+\s*(?P<em>\d{1,2})[\/\.-](?P<ey>\d{2,4}|present|current|now|date)",
    re.IGNORECASE,
)

# e.g., "6+ years of experience", "3 yrs experience"
EXPLICIT_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
    re.IGNORECASE,
)

YEAR_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")

# ── main extractors ───────────────────────────────────────────────────────────

def _collect_intervals(text: str) -> List[Tuple[int, int]]:
    T = _norm(text)
    intervals: List[Tuple[int, int]] = []

    # Month name ranges
    for m in NAME_RANGE_RE.finditer(T):
        sm, sy, em, ey = m.group("sm", "sy", "em", "ey")
        syi = _to_year(sy); smi = _to_month(sm)
        eyi = _to_year(ey); emi = _to_month(em)
        if syi and smi and eyi and emi:
            s = _to_index(syi, smi)
            e = _to_index(eyi, emi)
            if e > s:
                intervals.append((s, e))

    # Numeric ranges
    for m in NUM_RANGE_RE.finditer(T):
        sm, sy, em, ey = m.group("sm", "sy", "em", "ey")
        syi = _to_year(sy); smi = _to_month(sm)
        eyi = _to_year(ey); emi = _to_month(em)
        if syi and smi and eyi and emi:
            s = _to_index(syi, smi)
            e = _to_index(eyi, emi)
            if e > s:
                intervals.append((s, e))

    return _merge(intervals)

def estimate_experience_years(text: str) -> float:
    """Month-accurate estimation of total experience (merged, no double-count)."""
    T = _norm(text)

    # Prefer explicit statements if present
    m = EXPLICIT_RE.search(T)
    if m:
        try:
            v = float(m.group(1))
            return max(0.0, min(v, 40.0))
        except Exception:
            pass

    intervals = _collect_intervals(T)
    if intervals:
        months = sum(e - s for (s, e) in intervals)  # already merged
        return round(months / 12.0, 2)

    # Fallback: span between earliest and latest year mention
    years = [int(y) for y in YEAR_RE.findall(T)]
    years = [y for y in years if 1980 <= y <= datetime.now().year]
    if len(years) >= 2:
        return float(max(years) - min(years))
    return 0.0

def target_years_from_jd(jd_text: str, default: float = 3.0) -> float:
    T = _norm(jd_text or "")
    m = EXPLICIT_RE.search(T)
    if m:
        try:
            v = float(m.group(1))
            return max(0.5, min(v, 20.0))
        except Exception:
            pass
    return default

def score_experience(resume_text: str, jd_text: str, default_target: float = 3.0) -> float:
    yrs = estimate_experience_years(resume_text)
    target = target_years_from_jd(jd_text, default_target)
    if target <= 0:
        target = default_target
    return float(min(yrs / target, 1.0))
