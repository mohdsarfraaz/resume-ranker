
from dataclasses import asdict
from pathlib import Path
import pandas as pd
from .config import Config
from .io import load_jd_text, load_resumes
from .rank import score_candidate

def rank(jd_path: Path, resumes_dir: Path, top_k: int = 10, cfg: Config | None = None) -> pd.DataFrame:
    cfg = cfg or Config()
    jd_text = load_jd_text(jd_path)
    rows = []
    for name, text in load_resumes(resumes_dir):
        sb = score_candidate(text, jd_text, cfg)
        row = {
            "candidate": name,
            "skills": sb.skills,
            "sim": sb.sim,
            "exp_score": sb.exp_score,
            "exp_years": round(sb.exp_years, 2),
            "exp_target": sb.exp_target,
            "total": sb.total,
        }

        rows.append(row)
    df = pd.DataFrame(rows).sort_values("total", ascending=False)
    return df.head(top_k)
