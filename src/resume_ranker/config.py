# src/resume_ranker/config.py
from pydantic import BaseModel
from typing import List

class Weights(BaseModel):
    w_skills: float = 0.5
    w_sim: float = 0.4
    w_exp: float = 0.1

class Config(BaseModel):
    skills: List[str] = [
        "python", "sql", "pandas", "numpy", "scikit-learn",
        "streamlit", "etl", "mlops", "dashboarding",
    ]
    weights: Weights = Weights()
    default_exp_target_years: float = 3.0  # <— NEW
