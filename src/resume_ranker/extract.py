
from pathlib import Path
from pdfminer.high_level import extract_text as pdf_text
from docx import Document

def from_pdf(path: Path) -> str:
    return pdf_text(str(path))

def from_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)
