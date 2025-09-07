
import typer
from pathlib import Path
from typing import Optional
from .pipeline import rank

app = typer.Typer(add_completion=False)

@app.command(name="rank")
def rank_cmd(
    jd: Path = typer.Option(..., exists=True, help="Path to job description (txt/pdf/docx)"),
    resumes: Path = typer.Option(..., exists=True, file_okay=False, help="Folder of resumes"),
    out: Optional[Path] = typer.Option(None, help="Where to write ranked CSV"),
    top_k: int = typer.Option(10, min=1, help="Top K candidates to return"),
    w_skills: float = 0.5,
    w_sim: float = 0.4,
    w_exp: float = 0.1,
):
    """Rank resumes against a job description."""
    from .config import Config, Weights

    cfg = Config()
    cfg.weights = Weights(w_skills=w_skills, w_sim=w_sim, w_exp=w_exp)
    df = rank(jd, resumes, top_k=top_k, cfg=cfg)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        typer.echo(f"Wrote {out}")
    else:
        typer.echo(df.to_string(index=False))

if __name__ == "__main__":
    app()
