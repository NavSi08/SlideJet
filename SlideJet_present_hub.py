import os, json, glob
from pathlib import Path
import streamlit as st
import yaml
from PIL import Image

# ---------- Paths ----------
APP_DIR = Path(__file__).parent.resolve()                # .../SlideJet_Presentations
REPO_ROOT = APP_DIR.parent                               # repo root
DATA_DIR = APP_DIR / "SJ_DATA"                           # .../SlideJet_Presentations/SJ_DATA

# ---------- Helpers ----------
def _get_query_yaml():
    """Return a Path from ?yaml=... if present and valid, else None."""
    # Streamlit >=1.31 has st.query_params; older versions use experimental_get_query_params
    try:
        qp = st.query_params  # Mapping (new API)
        qval = qp.get("yaml", None)
        if isinstance(qval, list):  # rare edge
            qval = qval[-1] if qval else None
    except Exception:
        qp = st.experimental_get_query_params()  # {name: [values]}
        qvals = qp.get("yaml", [])
        qval = qvals[-1] if qvals else None

    if not qval:
        return None

    candidate = (REPO_ROOT / qval).resolve()
    try:
        candidate.relative_to(REPO_ROOT)  # safety
    except Exception:
        return None
    return candidate if candidate.exists() else None

@st.cache_data(show_spinner=False)
def load_yaml(yaml_path: Path):
    return yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

@st.cache_data(show_spinner=False)
def load_json(json_path: Path):
    return json.loads(json_path.read_text(encoding="utf-8"))

def render_presentation(cfg_path: Path):
    cfg = load_yaml(cfg_path)

    # Resolve presentation folder from config
    pres_folder = cfg.get("presentation_folder")
    if not pres_folder:
        st.error("`presentation_folder` missing in YAML.")
        return

    pres_dir = (REPO_ROOT / pres_folder).resolve()
    if not pres_dir.exists():
        st.error(f"Presentation folder not found: {pres_folder}")
        return

    json_file = pres_dir / "slide_data.json"
    if not json_file.exists():
        st.error(f"`slide_data.json` not found in: {pres_folder}")
        return

    slides = load_json(json_file)
    if not isinstance(slides, list) or not slides:
        st.warning("No slides found.")
        return

    # Header
    st.title(cfg.get("header_text", "SlideJet Presentation"))
    sub = cfg.get("subheader_text")
    if sub:
        st.caption(sub)

    # UI
    col_a, col_b = st.columns([1, 3])
    with col_a:
        idx = st.number_input("Slide", 1, len(slides), 1, key="slide_idx")
    rec = slides[int(idx) - 1]
    img_rel = rec.get("image", "")
    img_path = pres_dir / img_rel

    with col_b:
        if img_path.exists():
            st.image(str(img_path))
        else:
            st.error(f"Image missing: {img_rel}")

    st.markdown("**Notes**")
    st.write(rec.get("notes", ""))

def main():
    st.set_page_config(page_title="SlideJet Present Hub", page_icon="🖼️")

    st.sidebar.header("SlideJet Presentations")
    # Discover all config files
    yaml_files = sorted(glob.glob(str(APP_DIR / "*_SJconfig.yaml")))
    yaml_map = {Path(p).name: Path(p) for p in yaml_files}

    q_yaml = _get_query_yaml()
    if q_yaml:
        # If query param provided, honor it
        choice_path = q_yaml
        st.sidebar.success(f"Opened from URL: {choice_path.name}")
    else:
        if not yaml_files:
            st.sidebar.info("No *_SJconfig.yaml found.\nPush a deck and refresh.")
            st.title("SlideJet Present Hub")
            st.write(
                "Place your presentations here:\n\n"
                "`SlideJet_Presentations/SJ_DATA/<Deck>/images/*.png`\n"
                "`SlideJet_Presentations/SJ_DATA/<Deck>/slide_data.json`\n"
                "`SlideJet_Presentations/<Deck>_SJconfig.yaml`"
            )
            return

        choice_name = st.sidebar.selectbox("Choose a deck:", list(yaml_map.keys()))
        choice_path = yaml_map[choice_name]

    # Deep-link helper
    rel_for_link = choice_path.relative_to(REPO_ROOT).as_posix()
    base_url = st.secrets.get("BASE_URL", "")  # optional
    st.sidebar.markdown(
        f"[Open this deck via URL](?yaml={rel_for_link})"
    )
    if base_url:
        st.sidebar.markdown(
            f"[Public link]({base_url}?yaml={rel_for_link})"
        )

    render_presentation(choice_path)

if __name__ == "__main__":
    main()
