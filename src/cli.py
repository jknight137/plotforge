import json
import re
import time
from pathlib import Path
from models import AIModel

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"

# ───────────────────────── Project Management ──────────────────────────
def create_project(name: str):
    project_path = PROJECTS_DIR / name
    project_path.mkdir(parents=True, exist_ok=True)

    theme = (BASE_DIR / "theme.txt").read_text(encoding="utf-8").strip()
    premise = (BASE_DIR / "premise.txt").read_text(encoding="utf-8").strip()

    metadata = {
        "title": name,
        "theme": theme,
        "premise": premise,
        "models": {
            "primary": "mistral:7b-instruct-v0.3-q4_K_M",
            "available": ["mistral:7b-instruct-v0.3-q4_K_M"]
        },
        "chapters": []
    }

    with open(project_path / "project.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    for sub in ("chapters", "drafts", "summaries"):
        (project_path / sub).mkdir(exist_ok=True)

    print(f"[Project Created] {name}")

# ───────────────────────── Utility Helpers ─────────────────────────────
def load_metadata(project_path: Path):
    with open(project_path / "project.json", encoding="utf-8") as f:
        return json.load(f)

def load_prev_summary(summaries_path: Path, page_number: int) -> str:
    """Return previous page summary text (empty if first page)."""
    file = summaries_path / f"page_{page_number - 1}_summary.txt"
    return file.read_text(encoding="utf-8") if file.exists() else ""

def strip_heading(text: str) -> str:
    """Remove leading 'Page N Draft' or similar."""
    return re.sub(r"^Page\s+\d+\s+Draft[:\s-]*", "", text, flags=re.IGNORECASE).lstrip()

def sanitize_text(text: str) -> str:
    """Replace Unicode em‑dashes with simple hyphens."""
    return text.replace("\u2014", "-").replace("—", "-")

def save_summary(full_text: str, summaries_path: Path, page_number: int):
    cleaned = strip_heading(full_text)
    words = cleaned.split()
    take = min(250, max(100, len(words) // 2))  # 100–250 words, ~½ page
    summary = " ".join(words[:take])
    (summaries_path / f"page_{page_number}_summary.txt").write_text(
        summary, encoding="utf-8"
    )

# ───────────────────────── Prompt Composition ──────────────────────────
def build_prompt(prev_summary: str, premise: str, page_number: int) -> str:
    return (
        f"## DO NOT output any heading. Begin directly with story text.\n\n"
        f"PREMISE (must remain consistent):\n{premise}\n\n"
        f"PREVIOUS PAGE SUMMARY:\n{prev_summary}\n\n"
        "Write the next ~500 words that continue this dystopian AI‑ruled world. "
        "Preserve characters, setting, and plot threads; do not introduce medieval fantasy, taverns, or magic.\n"
    )

# ───────────────────────── Page Generation ─────────────────────────────
def generate_and_save_page(model_name: str,
                           prompt: str,
                           chapters_path: Path,
                           summaries_path: Path,
                           page_number: int,
                           test_mode: bool):
    model = AIModel(model_name)
    try:
        text, words, duration = model.generate(prompt, min_words=500)
    except Exception as e:
        print(f"[Error] {model_name}: {e}")
        return

    text = sanitize_text(text)
    text = strip_heading(text)

    suffix = f"_{model_name.replace('/', '_')}" if test_mode else ""
    draft_path = chapters_path / f"page_{page_number}_draft{suffix}.md"

    if text.strip():
        draft_path.write_text(text.strip(), encoding="utf-8")
        save_summary(text, summaries_path, page_number)
        print(f"[Saved] Page {page_number} draft{suffix} ({words} words, {duration:.2f}s)")
    else:
        print(f"[Skipped] Empty result from {model_name}")

def generate_page(project: str, page_number: int, model_override=None, test_models=False):
    project_path = PROJECTS_DIR / project
    if not (project_path / "project.json").exists():
        print(f"[Error] Project '{project}' not found.")
        return

    meta = load_metadata(project_path)
    chapters = project_path / "chapters"
    summaries = project_path / "summaries"

    models = meta["models"]["available"] if test_models else [
        model_override or meta["models"]["primary"]
    ]
    prev_summary = load_prev_summary(summaries, page_number)
    prompt = build_prompt(prev_summary, meta["premise"], page_number)

    for m in models:
        generate_and_save_page(m, prompt, chapters, summaries, page_number, test_models)

# ───────────────────────── Chapter Generation (unchanged) ─────────────
def generate_chapter(project: str, number: int, model_override=None, test_models=False):
    project_path = PROJECTS_DIR / project
    if not (project_path / "project.json").exists():
        print(f"[Error] Project '{project}' not found.")
        return

    meta = load_metadata(project_path)
    chapters = project_path / "chapters"
    prompt = (
        f"THEME:\n{meta['theme']}\n\n"
        f"PREMISE:\n{meta['premise']}\n\n"
        f"Write Chapter {number} (~5000 words) continuing the plot."
    )

    models = meta["models"]["available"] if test_models else [
        model_override or meta["models"]["primary"]
    ]
    for m in models:
        model = AIModel(m)
        try:
            text, words, duration = model.generate(prompt, min_words=5000)
        except Exception as e:
            print(f"[Error] {m}: {e}")
            continue

        text = sanitize_text(text)
        suffix = f"_{m.replace('/', '_')}" if test_models else ""
        (chapters / f"chapter_{number}_draft{suffix}.md").write_text(text, encoding="utf-8")
        print(f"[Saved] Chapter {number} draft{suffix} ({words} words, {duration:.2f}s)")

# ───────────────────────── Model Management ────────────────────────────
def manage_models(project: str, list_flag=False, set_primary=None):
    path = PROJECTS_DIR / project / "project.json"
    if not path.exists():
        print(f"[Error] Project '{project}' not found.")
        return
    meta = json.loads(path.read_text(encoding="utf-8"))

    if list_flag:
        print("[Models]")
        for m in meta["models"]["available"]:
            tag = " (primary)" if m == meta["models"]["primary"] else ""
            print(f"- {m}{tag}")
        return

    if set_primary:
        if set_primary not in meta["models"]["available"]:
            meta["models"]["available"].append(set_primary)
        meta["models"]["primary"] = set_primary
        path.write_text(json.dumps(meta, indent=4))
        print(f"[Model Updated] Primary set to {set_primary}")
