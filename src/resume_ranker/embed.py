
from sentence_transformers import SentenceTransformer, util

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def similarity(a: str, b: str) -> float:
    m = get_model()
    ea, eb = m.encode([a, b], normalize_embeddings=True)
    return float(util.cos_sim(ea, eb)[0][0])
