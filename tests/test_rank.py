
from pathlib import Path
from resume_ranker.pipeline import rank

S = "Python SQL pandas data analysis"

def test_rank_runs(tmp_path: Path):
    jd = tmp_path / "jd.txt"; jd.write_text(S)
    res_dir = tmp_path / "res"; res_dir.mkdir()
    (res_dir / "a.txt").write_text("I love Python and SQL for analytics")
    (res_dir / "b.txt").write_text("Project manager, stakeholder comms")
    df = rank(jd, res_dir, top_k=2)
    assert list(df.columns) == [
        "candidate", "skills", "sim", "exp", "total"
    ]
    assert len(df) == 2
    assert df.iloc[0]["total"] >= df.iloc[1]["total"]
