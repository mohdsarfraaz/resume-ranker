from pathlib import Path
import io

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from resume_ranker.pipeline import rank
from resume_ranker.config import Config, Weights

st.set_page_config(page_title="Resume Ranker", layout="wide")
# --- Reset hook (token-protected) --------------------------------------------
import os, shutil
import streamlit as st

def _get_query_params():
    # works on older/newer Streamlit
    try:
        return st.query_params  # type: ignore[attr-defined]
    except Exception:
        return st.experimental_get_query_params()

params = _get_query_params()
reset_flag  = (params.get("reset", ["0"])[0] == "1")
reset_token = params.get("token", [""])[0]
allow_token = st.secrets.get("RESET_TOKEN", "")

if reset_flag and allow_token and reset_token == allow_token:
    # Clear Streamlit caches (fast and safe)
    st.cache_data.clear()
    st.cache_resource.clear()

    # Optional: add &wipe_db=1 to also delete the local SQLite file
    if params.get("wipe_db", ["0"])[0] == "1":
        try:
            if os.path.exists("app_data.db"):
                os.remove("app_data.db")
            shutil.rmtree(".streamlit_tmp", ignore_errors=True)
        except Exception:
            pass

    st.write("✅ Reset completed.")
    st.stop()

st.markdown('<h1 class="page-title">Resume Ranker</h1>', unsafe_allow_html=True)


st.markdown("""
<style>
/* More breathing room at the very top so the first H1 never clips */
.block-container {
  padding-top: 2.5rem !important;   /* was 1rem */
  padding-bottom: 2rem;
  max-width: 1200px;
  overflow: visible;                 /* extra safety on some browsers */
}

/* Headings: ensure they can't clip due to line-height */
h1 { font-size: 2rem; font-weight: 800; letter-spacing: -0.01em;
     line-height: 1.25; margin: .25rem 0 1rem; }
h2 { font-size: 1.3rem; font-weight: 700; line-height: 1.3; margin: .6rem 0 .25rem; }
h3 { font-size: 1.1rem; font-weight: 600; line-height: 1.3; }

/* Optional muted helper */
.muted { color:#6b7280; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

# Keep raw uploaded files (for download buttons later)
if "raw_files" not in st.session_state:
    # { candidate_name: (original_filename, raw_bytes) }
    st.session_state.raw_files = {}

# --- Sidebar controls ---------------------------------------------------------
with st.sidebar:
    st.header("Scoring & filters")

    # Weights
    w_skills = st.slider("Skills weight", 0.0, 1.0, 0.5, 0.05)
    w_sim = st.slider("Similarity weight", 0.0, 1.0, 0.4, 0.05)
    w_exp = st.slider("Experience weight", 0.0, 1.0, 0.1, 0.05)

    st.markdown("---")

    # Qualification logic
    min_total = st.slider("Min TOTAL score to qualify", 0.0, 1.0, 0.5, 0.01)
    use_component_thresholds = st.checkbox("Also require per-component minimums", value=False)
    min_skills = st.slider("Min skills match (0-1)", 0.0, 1.0, 0.3, 0.01, disabled=not use_component_thresholds)
    min_sim = st.slider("Min similarity (0-1)", 0.0, 1.0, 0.3, 0.01, disabled=not use_component_thresholds)

    st.markdown("---")
    top_n_plot = st.slider("Top N for bar chart", 3, 30, 10, 1)

# --- JD input -----------------------------------------------------------------
st.subheader("Job Description")
jd_mode = st.radio("How do you want to provide the JD?", ["Upload file", "Paste text"], horizontal=True)

jd_file = None
jd_text = None

if jd_mode == "Upload file":
    jd_file = st.file_uploader("Upload JD (txt/pdf/docx)", type=["txt", "pdf", "docx"], key="jd_uploader")
else:
    jd_text = st.text_area("Paste JD text here", height=200, key="jd_textarea")

# Optional key skills override (comma-separated)
skills_input = st.text_input(
    "Optional: key skills that strongly impact this JD (comma-separated)",
    placeholder="python, sql, pandas, streamlit"
)

# --- Resume input -------------------------------------------------------------
st.subheader("Resumes")
resumes = st.file_uploader("Upload resumes", type=["txt", "pdf", "docx"], accept_multiple_files=True)

# --- Action -------------------------------------------------------------------
if st.button("Rank candidates", type="primary"):
    if (jd_mode == "Upload file" and not jd_file) or (jd_mode == "Paste text" and not jd_text):
        st.error("Please provide the Job Description (upload a file or paste text).")
        st.stop()
    if not resumes:
        st.error("Please upload at least one resume.")
        st.stop()

    # Prepare temp workspace
    tmp = Path(".streamlit_tmp")
    tmp.mkdir(exist_ok=True)
    res_dir = tmp / "resumes"
    res_dir.mkdir(exist_ok=True)

    # Reset raw files map each run
    st.session_state.raw_files = {}

    # Save JD (even in paste mode, write a temp file to reuse pipeline.rank)
    if jd_mode == "Upload file":
        jd_path = tmp / jd_file.name
        jd_path.write_bytes(jd_file.read())
    else:
        jd_path = tmp / "jd.txt"
        jd_path.write_text(jd_text, encoding="utf-8")

    # Save resumes to disk + keep raw bytes for download
    for f in resumes:
        raw = f.read()
        (res_dir / f.name).write_bytes(raw)
        candidate_name = Path(f.name).stem
        st.session_state.raw_files[candidate_name] = (f.name, raw)

    # Build config (apply custom skill list if provided)
    cfg = Config()
    if skills_input.strip():
        skills = [s.strip() for s in skills_input.split(",") if s.strip()]
        if skills:
            cfg.skills = skills
    cfg.weights = Weights(w_skills=w_skills, w_sim=w_sim, w_exp=w_exp)

    # Rank
    df: pd.DataFrame = rank(jd_path, res_dir, top_k=9999, cfg=cfg)
    # Enforce numeric bounds (similarity can be [-1, 1], clip for UI thresholds)
    df["skills"] = df["skills"].clip(0.0, 1.0)
    df["sim"] = df["sim"].clip(0.0, 1.0)
    df["exp_score"] = df["exp_score"].clip(0.0, 1.0)
    df["total"] = df["total"].clip(0.0, 1.0)


    # Qualification logic
    if use_component_thresholds:
        qual_mask = (df["total"] >= min_total) & (df["skills"] >= min_skills) & (df["sim"] >= min_sim)
    else:
        qual_mask = (df["total"] >= min_total)

    df["qualified"] = qual_mask
    qualified_df = df[df["qualified"]].copy()
    disqualified_df = df[~df["qualified"]].copy()

    # --- Summary KPIs ---------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Total candidates", len(df))
    c2.metric("Qualified", len(qualified_df))
    c3.metric("Disqualified", len(disqualified_df))

    st.markdown("---")

    # --- Charts ---------------------------------------------------------------
    st.subheader("Scores overview")

    # Put charts in a narrower column so they don't span full width
    plot_col, _ = st.columns([2, 1])

    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.dpi": 160,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 8,
        "ytick.labelsize": 9,
    })

    top_df = df.sort_values("total", ascending=False).head(top_n_plot)

    with plot_col:
        # Bar: compact size, don't stretch to container width
        fig1, ax1 = plt.subplots(figsize=(6.2, 3.0))
        ax1.bar(top_df["candidate"], top_df["total"])
        ax1.set_ylabel("Total score")
        ax1.set_title(f"Top {len(top_df)} candidates")
        ax1.set_ylim(0, 1)
        ax1.tick_params(axis="x", rotation=30)
        st.pyplot(fig1, use_container_width=False)

    with plot_col:
        # Scatter: compact
        fig2, ax2 = plt.subplots(figsize=(5.5, 3.2))
        ax2.scatter(df["sim"], df["skills"])
        ax2.set_xlabel("Similarity (0–1)")
        ax2.set_ylabel("Skills match (0–1)")
        ax2.set_title("Similarity vs Skills")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2, use_container_width=False)


    # --- Qualified table + downloads -----------------------------------------
    st.markdown('<p class="muted">Experience columns: <b>exp_years</b> (real) · '
            '<b>exp_target</b> (JD or default) · <b>exp_score</b> (normalized 0–1)</p>',
            unsafe_allow_html=True)

    st.subheader("Qualified")
    if len(qualified_df) == 0:
        st.info("No candidates met the qualification criteria.")
    else:
        st.dataframe(
            qualified_df[["candidate", "skills", "sim", "exp_years", "exp_target", "exp_score", "total"]].reset_index(drop=True),
      use_container_width=True,
        )
        st.download_button(
            "Download Qualified (CSV)",
            data=qualified_df.to_csv(index=False),
            file_name="qualified.csv",
        )

        with st.expander("Download raw resumes (qualified)"):
            for _, row in qualified_df.iterrows():
                cand = str(row["candidate"])
                if cand in st.session_state.raw_files:
                    fname, raw = st.session_state.raw_files[cand]
                    st.download_button(
                        f"Download {fname}",
                        data=raw,
                        file_name=fname,
                        mime="application/octet-stream",
                        key=f"qdl_{fname}",
                    )

    st.markdown("---")

    # --- Disqualified table + downloads --------------------------------------
    st.subheader("Disqualified")
    if len(disqualified_df) == 0:
        st.info("Everyone qualified 🎉")
    else:
        st.dataframe(
            disqualified_df[["candidate", "skills", "sim", "exp_years", "exp_target", "exp_score", "total"]].reset_index(drop=True),
            use_container_width=True,
        )
        st.download_button(
            "Download Disqualified (CSV)",
            data=disqualified_df.to_csv(index=False),
            file_name="disqualified.csv",
        )

        with st.expander("Download raw resumes (disqualified)"):
            for _, row in disqualified_df.iterrows():
                cand = str(row["candidate"])
                if cand in st.session_state.raw_files:
                    fname, raw = st.session_state.raw_files[cand]
                    st.download_button(
                        f"Download {fname}",
                        data=raw,
                        file_name=fname,
                        mime="application/octet-stream",
                        key=f"ddl_{fname}",
                    )
