
from pathlib import Path
from typing import List, Tuple
from .extract import from_pdf, from_docx

SUPPORTED = (".pdf", ".docx", ".txt")

def load_jd_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return from_pdf(path)
    if path.suffix.lower() == ".docx":
        return from_docx(path)
    return path.read_text(encoding="utf-8")

def load_resumes(folder: Path) -> List[Tuple[str, str]]:
    items = []
    for p in folder.glob("**/*"):
        if p.suffix.lower() not in SUPPORTED:
            continue
        if p.suffix.lower() == ".pdf":
            text = from_pdf(p)
        elif p.suffix.lower() == ".docx":
            text = from_docx(p)
        else:
            text = p.read_text(encoding="utf-8")
        items.append((p.stem, text))
    return items
