
# Resume Ranker

> **Smart CV shortlisting** — extract text, match skills, and rank candidates against a job description using a hybrid of rule‑based checks and semantic similarity.

![Demo GIF goes here](docs/demo.gif)

<p align="center">
  <a href="#">Live Demo</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-how-it-works">How it works</a> •
  <a href="#-cli-usage">CLI</a> •
  <a href="#-streamlit-app">Streamlit</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## ✨ Features
- **Text extraction:** from PDFs/Docs to plain text
- **Skill matching:** exact + fuzzy (RapidFuzz)
- **Semantic similarity:** `sentence-transformers` embeddings
- **Weighted scoring:** combine experience, skills, and similarity
- **Outputs:** ranked table + CSV export
- **Two interfaces:** CLI (automation) and Streamlit app (interactive)

---

## 🚀 Quickstart

### Requirements
- Python 3.10+

```bash
# clone
git clone https://github.com/yourname/resume-ranker
cd resume-ranker

# install
pip install -e ".[cli,app]"  # editable install with extras

# run a quick check
resume-ranker --help
```

### Try the sample
```bash
# rank against a sample JD and resumes
resume-ranker rank   --jd samples/jd/product-analyst.txt   --resumes samples/resumes   --top-k 10   --out out/ranked.csv
```

---

## 🧠 How it works
1. **Extract**: parse resume text (PDF/Docx → plain text)
2. **Normalize**: cleanup, detect sections, deduplicate
3. **Match skills**: exact + fuzzy lookup (configurable skill set)
4. **Embed & compare**: compute JD/resume embeddings and cosine similarity
5. **Score**: `score = w1*skills + w2*similarity + w3*experience`
6. **Rank**: produce sorted table with per‑component scores

> **Transparency:** All weights, thresholds, and skill dictionaries are configurable in `config.yaml` or CLI flags.

---

## 🔧 CLI usage

```bash
# show help
resume-ranker --help

# basic ranking
resume-ranker rank --jd jd.txt --resumes ./resumes --out ranked.csv

# tweak weights and thresholds
resume-ranker rank --jd jd.txt --resumes ./resumes   --w-skills 0.5 --w-sim 0.4 --w-exp 0.1 --top-k 20

# generate an explainability report (per candidate)
resume-ranker explain --candidate ./resumes/Akash.pdf --jd jd.txt --out out/Akash_report.md
```

---

## 🖥 Streamlit app

```bash
streamlit run app/streamlit_app.py
```

Features:
- Upload a JD and multiple resumes
- Toggle weights and strict/semantic modes
- Preview ranked results; download CSV

---

## 📦 Outputs
- `ranked.csv` with columns: `candidate, skills_score, sim_score, exp_score, total_score`
- Optional per‑candidate explanation report (top matched skills, missing skills)

---

## 🧪 Testing

```bash
pytest -q
```

---

## 📈 Roadmap
- [ ] Add FastAPI microservice with `/rank` and `/explain`
- [ ] Model card + evaluation dataset
- [ ] Multilingual support
- [ ] Pluggable extraction backends

---

## 🔐 Ethics, bias, and privacy
This tool is **assistive**, not a decision‑maker. Automated screening can amplify bias. Always:
- Obtain explicit consent to process resumes
- Remove PII when possible
- Keep humans in the loop for hiring decisions

---

## 🛠 Development
```bash
# format & lint
ruff check . && black --check . && mypy

# pre-commit
pre-commit install
```

---

## 📄 License
MIT (see `LICENSE`)
