from dataclasses import dataclass
from .skills import score_skills
from .embed import similarity
from .config import Config
from .experience import estimate_experience_years, target_years_from_jd

@dataclass
class ScoreBreakdown:
    skills: float
    sim: float
    exp_score: float      # 0..1 used in total
    exp_years: float      # real years extracted
    exp_target: float     # target years from JD (or default)
    total: float

def score_candidate(resume_text: str, jd_text: str, cfg: Config) -> ScoreBreakdown:
    s_skills = score_skills(resume_text, cfg.skills)
    s_sim = similarity(resume_text, jd_text)
    yrs = estimate_experience_years(resume_text)
    tgt = target_years_from_jd(jd_text, cfg.default_exp_target_years)
    s_exp = min(yrs / tgt, 1.0) if tgt > 0 else 0.0
    total = cfg.weights.w_skills*s_skills + cfg.weights.w_sim*s_sim + cfg.weights.w_exp*s_exp
    return ScoreBreakdown(s_skills, s_sim, s_exp, yrs, tgt, total)
