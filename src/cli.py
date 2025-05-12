import json
from json_repair import repair_json
import re
import time
from pathlib import Path
from models import AIModel
import ollama

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"

SUMMARY_MAX_WORDS = 250
SUMMARY_MIN_WORDS = 100

# ───────────────────────── Utility Helpers ─────────────────────────────
def load_metadata(project_path: Path):
    with open(project_path / "project.json", encoding="utf-8") as f:
        return json.load(f)

def load_prev_summary(summaries_path: Path, page_number: int) -> str:
    file = summaries_path / f"page_{page_number - 1}_summary.txt"
    return file.read_text(encoding="utf-8") if file.exists() else ""

def strip_heading(text: str) -> str:
    return re.sub(r"^Page\s+\d+\s+Draft[:\s-]*", "", text, flags=re.IGNORECASE).lstrip()

def sanitize_text(text: str) -> str:
    return text.replace("\u2014", "-").replace("—", "-")

def save_summary(full_text: str, summaries_path: Path, page_number: int):
    cleaned = strip_heading(full_text)
    words = cleaned.split()
    take = min(SUMMARY_MAX_WORDS, max(SUMMARY_MIN_WORDS, len(words) // 2))
    summary = " ".join(words[:take])
    (summaries_path / f"page_{page_number}_summary.txt").write_text(summary, encoding="utf-8")

def get_chapter_dir(project_path: Path, chapter_number: int) -> Path:
    chapter_dir = project_path / "chapters" / f"chapter_{chapter_number}"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    return chapter_dir

def get_chapter_summary(project_path: Path, chapter_number: int) -> str:
    raw_path = project_path / "chapters" / "outline_raw.txt"
    json_path = project_path / "chapters" / "outline.json"

    if raw_path.exists():
        text = raw_path.read_text(encoding="utf-8")
        pattern = rf"(?i)^chapter\s*{chapter_number}.*?(?:\n\n|\Z)(.*?)(?=\n\s*(?:Chapter\s*\d+|$))"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            return data.get("chapters", [])[chapter_number - 1].get("summary", "")
        except Exception:
            pass

    return ""

def create_project(name: str):
    project_path = PROJECTS_DIR / name
    project_path.mkdir(parents=True, exist_ok=True)

    theme = (BASE_DIR / "theme.txt").read_text(encoding="utf-8").strip()
    premise = (BASE_DIR / "premise.txt").read_text(encoding="utf-8").strip()

    ollama_models = [m["model"] for m in ollama.list()["models"]]
    openai_models = ["gpt-4-1106-preview", "gpt-4.1-2025-04-14"]
    available_models = openai_models + ollama_models

    print("[Available Models]")
    for idx, model in enumerate(available_models):
        print(f"{idx + 1}: {model}")
    choice = input("Select a primary model by number (default 1): ").strip()
    selected_index = int(choice) - 1 if choice.isdigit() else 0
    primary_model = available_models[selected_index]

    metadata = {
        "title": name,
        "theme": theme,
        "premise": premise,
        "models": {
            "primary": primary_model,
            "available": available_models
        },
        "chapters": [],
        "outline_approved": False
    }

    with open(project_path / "project.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    for sub in ("chapters", "drafts", "summaries", "context"):
        (project_path / sub).mkdir(exist_ok=True)

    print(f"[Project Created] {name}")

# ───────────────────────── Prompt Composition ──────────────────────────
def build_prompt(prev_summary: str, premise: str, page_number: int, project_path: Path = None, chapter_summary: str = "") -> str:
    prompt = (
        f"## DO NOT output any heading. Begin directly with story text.\n\n"
        f"PREMISE:\n{premise}\n\n"
    )
    if page_number > 1:
        prompt += f"PREVIOUS PAGE SUMMARY:\n{prev_summary}\n\n"
    if chapter_summary:
        prompt += f"CURRENT CHAPTER SUMMARY:\n{chapter_summary}\n\n"
    prompt += "Continue the story in the next ~500 words, preserving tone, characters, and continuity.\n"
    return prompt

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

# ───────────────────────── Chapter/Pages Generation ────────────────────
def generate_and_save_page(model_name: str, prompt: str, chapter_dir: Path, summaries_path: Path, page_number: int, test_mode: bool):
    model = AIModel(model_name)
    try:
        text, words, duration = model.generate(prompt, min_words=500)
    except Exception as e:
        print(f"[Error] {model_name}: {e}")
        return

    text = sanitize_text(text)
    text = strip_heading(text)
    suffix = f"_{model_name.replace('/', '_')}" if test_mode else ""
    draft_path = chapter_dir / f"page_{page_number}_draft{suffix}.md"

    if text.strip():
        draft_path.write_text(text.strip(), encoding="utf-8")
        save_summary(text, summaries_path, page_number)
        print(f"[Saved] Page {page_number} draft{suffix} ({words} words, {duration:.2f}s)")
    else:
        print(f"[Skipped] Empty result from {model_name}")

def generate_page(project: str, page_number: int, model_override=None, test_models=False, pages_per_chapter: int = 10):
    project_path = PROJECTS_DIR / project
    meta = load_metadata(project_path)
    if not meta.get("outline_approved", False):
        print("[Blocked] Outline not approved.")
        return

    chapter_number = (page_number - 1) // pages_per_chapter + 1
    chapter_dir = get_chapter_dir(project_path, chapter_number)
    summaries = project_path / "summaries"

    prev_summary = load_prev_summary(summaries, page_number)
    chapter_summary = get_chapter_summary(project_path, chapter_number)
    prompt = build_prompt(prev_summary, meta["premise"], page_number, project_path, chapter_summary)

    models = meta["models"]["available"] if test_models else [model_override or meta["models"]["primary"]]
    for m in models:
        generate_and_save_page(m, prompt, chapter_dir, summaries, page_number, test_mode=test_models)

def write_chapter(project: str, chapter_number: int, total_pages: int = 10, model_override=None, pages_per_chapter: int = 10):
    project_path = PROJECTS_DIR / project
    meta = load_metadata(project_path)
    if not meta.get("outline_approved", False):
        print("[Blocked] Outline not approved.")
        return

    summaries = project_path / "summaries"
    model_name = model_override or meta["models"]["primary"]
    chapter_summary = get_chapter_summary(project_path, chapter_number)
    chapter_dir = get_chapter_dir(project_path, chapter_number)

    print(f"[Writing Chapter {chapter_number}] Using model: {model_name}")
    for i in range(total_pages):
        page_number = (chapter_number - 1) * pages_per_chapter + i + 1
        prev_summary = load_prev_summary(summaries, page_number)
        prompt = build_prompt(prev_summary, meta["premise"], page_number, project_path, chapter_summary)
        generate_and_save_page(model_name, prompt, chapter_dir, summaries, page_number, test_mode=False)

    print(f"[Complete] Chapter {chapter_number} written ({total_pages} pages)")

# ───────────────────────── Chapter Approval & Summarization ────────────
def approve_chapter(project: str, chapter_number: int, pages_per_chapter: int = 10):
    project_path = PROJECTS_DIR / project
    chapter_dir = get_chapter_dir(project_path, chapter_number)

    page_numbers = range((chapter_number - 1) * pages_per_chapter + 1, chapter_number * pages_per_chapter + 1)
    for page_num in page_numbers:
        draft_file = chapter_dir / f"page_{page_num}_draft.md"
        if draft_file.exists():
            approval_file = chapter_dir / f"page_{page_num}_approved.txt"
            approval_file.write_text("auto-approved", encoding="utf-8")
            print(f"[Auto-Approved] Page {page_num}")

    approved_flag = chapter_dir / f"chapter_{chapter_number}_approved.txt"
    approved_flag.write_text("approved", encoding="utf-8")
    print(f"[Approved] Chapter {chapter_number} marked as approved.")
    concat_chapter(project, chapter_number, pages_per_chapter)

def concat_chapter(project: str, chapter_number: int, pages_per_chapter: int = 10):
    project_path = PROJECTS_DIR / project
    chapter_dir = get_chapter_dir(project_path, chapter_number)

    page_numbers = range((chapter_number - 1) * pages_per_chapter + 1, chapter_number * pages_per_chapter + 1)
    output = ""

    for n in page_numbers:
        page_file = chapter_dir / f"page_{n}_draft.md"
        if not page_file.exists():
            print(f"[Missing] Page {n} does not exist. Skipping.")
            continue
        approved = chapter_dir / f"page_{n}_approved.txt"
        if not approved.exists():
            print(f"[Warning] Page {n} not approved. Skipping.")
            continue
        output += page_file.read_text(encoding="utf-8").strip() + "\n\n"

    final_path = chapter_dir / f"chapter_{chapter_number}_final.md"
    final_path.write_text(output.strip(), encoding="utf-8")
    print(f"[Saved] {final_path}")
#generate outline
def generate_outline(project: str, model_override=None):
    project_path = PROJECTS_DIR / project
    meta_path = project_path / "project.json"
    if not meta_path.exists():
        print(f"[Error] Project '{project}' not found.")
        return

    meta = load_metadata(project_path)
    theme, premise = meta["theme"], meta["premise"]
    model_name = model_override or meta["models"]["primary"]
    model = AIModel(model_name)

    # ── Step 1: Generate human-readable outline ──────────────────────
    prose_prompt = (
        "You are a professional story architect. Given the theme and premise below, write a full novel outline in natural language. "
        "Organize your outline with the following sections:\n"
        "- Characters (names, roles, and personalities)\n"
        "- Setting (time, place, atmosphere)\n"
        "- Central Theme (ideological and emotional arc)\n"
        "- Key Scenes (5–10 major turning points)\n"
        "- Chapters: title, summary, and structure (intro, conflict, climax for each)\n\n"
        "Write clearly with section headers. Do NOT return any JSON, code blocks, or markdown.\n\n"
        f"THEME:\n{theme}\n\nPREMISE:\n{premise}\n"
    )

    try:
        prose_text, *_ = model.generate(prose_prompt, min_words=700)
        raw_path = project_path / "chapters" / "outline_raw.txt"
        raw_path.write_text(prose_text.strip(), encoding="utf-8")
        print(f"[Saved] {raw_path}")
    except Exception as e:
        print(f"[Error] Outline prose generation failed: {e}")
        return

    # ── Step 2: Ask model to convert raw outline to structured JSON ──
    json_prompt = (
        "Convert the following novel outline into valid JSON with this format:\n"
        "{\n"
        "  \"characters\": [ { \"name\": ..., \"role\": ..., \"traits\": [...] }, ... ],\n"
        "  \"setting\": \"...\",\n"
        "  \"theme\": \"...\",\n"
        "  \"key_scenes\": [ \"...\", \"...\" ],\n"
        "  \"chapters\": [\n"
        "    {\n"
        "      \"title\": \"...\",\n"
        "      \"summary\": \"...\",\n"
        "      \"structure\": { \"intro\": \"...\", \"conflict\": \"...\", \"climax\": \"...\" }\n"
        "    }, ...\n"
        "  ]\n"
        "}\n\n"
        "Be precise and use proper JSON syntax. Do not include commentary or markdown.\n\n"
        f"OUTLINE:\n{prose_text}"
    )

    try:
        json_text, *_ = model.generate(json_prompt, min_words=300)

        repaired_text = repair_json(json_text)
        outline = json.loads(repaired_text)

        outline_path = project_path / "chapters" / "outline.json"
        outline_path.write_text(json.dumps(outline, indent=4), encoding="utf-8")
        print(f"[Saved] {outline_path}")

    except Exception as e:
        print(f"[Error] Failed to convert outline to JSON: {e}")

# approve outline
def approve_outline(project: str):
    path = PROJECTS_DIR / project / "project.json"
    if not path.exists():
        print(f"[Error] Project '{project}' not found.")
        return
    meta = json.loads(path.read_text(encoding="utf-8"))
    meta["outline_approved"] = True
    path.write_text(json.dumps(meta, indent=4))
    print("[Approved] Outline locked in.")

def summarize_chapter(project: str, chapter_number: int, model_override=None):
    project_path = PROJECTS_DIR / project
    chapter_dir = get_chapter_dir(project_path, chapter_number)
    context_path = project_path / "context"
    context_path.mkdir(exist_ok=True)

    model_name = model_override or load_metadata(project_path)["models"]["primary"]
    model = AIModel(model_name)
    final_path = chapter_dir / f"chapter_{chapter_number}_final.md"

    if not final_path.exists():
        print(f"[Error] Chapter {chapter_number} not finalized.")
        return

    full_text = final_path.read_text(encoding="utf-8")
    prompt = (
        "You are a novel assistant. Summarize the chapter below into 1–3 concise paragraphs, capturing:\n"
        "- key plot points\n- character progressions\n- emerging themes\n\n"
        "CHAPTER CONTENT:\n" + full_text
    )

    try:
        summary, *_ = model.generate(prompt, min_words=200)
        summary_path = chapter_dir / f"chapter_{chapter_number}_summary.txt"
        summary_path.write_text(summary.strip(), encoding="utf-8")
        print(f"[Saved] {summary_path}")
    except Exception as e:
        print(f"[Error] Chapter summary failed: {e}")
