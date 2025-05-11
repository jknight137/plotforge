import os
import json
from pathlib import Path
from datetime import datetime
from git_manager import init_git_repo
from models import AIModel

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"

def get_project_path(name):
    return PROJECTS_DIR / name

def load_metadata(project_path):
    with open(project_path / "project.json", encoding="utf-8") as f:
        return json.load(f)

def save_metadata(project_path, metadata):
    with open(project_path / "project.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def ensure_dirs(project_path):
    (project_path / "chapters").mkdir(parents=True, exist_ok=True)
    (project_path / "context").mkdir(parents=True, exist_ok=True)
    (project_path / "chapters" / "history").mkdir(parents=True, exist_ok=True)

def log_history(project_path, entry):
    history_path = project_path / "history.jsonl"
    entry["timestamp"] = datetime.now().isoformat(timespec="seconds")
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def create_project(name):
    project_path = get_project_path(name)
    ensure_dirs(project_path)

    theme_path = BASE_DIR / "theme.txt"
    premise_path = BASE_DIR / "premise.txt"

    if not theme_path.exists():
        raise FileNotFoundError("theme.txt not found in project root.")
    if not premise_path.exists():
        raise FileNotFoundError("premise.txt not found in project root.")

    theme = theme_path.read_text(encoding="utf-8").strip()
    premise = premise_path.read_text(encoding="utf-8").strip()

    metadata = {
        "title": name,
        "theme": theme,
        "premise": premise,
        "models": {
            "primary": "mistralai/Mistral-7B-Instruct-v0.3",
            "available": ["mistralai/Mistral-7B-Instruct-v0.3"]
        },
        "chapters": [],
        "status": "initialized"
    }

    with open(project_path / "project.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    (project_path / "outline.md").touch()
    (project_path / "context" / "story_so_far.md").touch()

    init_git_repo(project_path)
    print(f"Project '{name}' created successfully.")

def generate_outline(name, model_override=None, from_file=None):
    project_path = get_project_path(name)
    if not (project_path / "project.json").exists():
        print(f"Project '{name}' does not exist. Run 'new' first.")
        return

    metadata = load_metadata(project_path)

    if from_file:
        outline_text = Path(from_file).read_text(encoding="utf-8")
    else:
        model_id = model_override or metadata["models"]["primary"]
        theme = metadata["theme"]
        prompt = (
            f"Using the following theme: '{theme}', generate an outline for a fiction novel.\n"
            "Include 10 chapters with short summaries."
        )
        model = AIModel(model_id)
        outline_text = model.generate(prompt, max_new_tokens=800)

    with open(project_path / "outline.md", "w", encoding="utf-8") as f:
        f.write(outline_text)

    log_history(project_path, {
        "type": "outline",
        "model": model_override or metadata["models"]["primary"],
        "prompt": "manual" if from_file else prompt,
        "output": outline_text
    })

    print("Outline saved successfully.")

def summarize_chapter(text):
    return text[:250].replace("\n", " ") + "..."

def generate_chapter(name, chapter_number, model_override=None):
    project_path = get_project_path(name)
    metadata = load_metadata(project_path)
    model_id = model_override or metadata["models"]["primary"]
    model = AIModel(model_id)

    outline_path = project_path / "outline.md"
    if not outline_path.exists():
        print("Outline not found. Generate or provide one first.")
        return

    chapter_title = f"Chapter {chapter_number}"
    outline = outline_path.read_text(encoding="utf-8")
    context_path = project_path / "context" / "story_so_far.md"
    story_so_far = context_path.read_text(encoding="utf-8")

    prompt = (
        f"The story theme is: {metadata['theme']}\n\n"
        f"Premise: {metadata['premise']}\n\n"
        f"Story so far:\n{story_so_far}\n\n"
        f"Outline:\n{outline}\n\n"
        f"Write a full detailed version of {chapter_title} in about 5000 words."
        " Maintain continuity, character voice, and consistent plot logic."
    )

    output = model.generate(prompt, max_new_tokens=3500)

    chapter_file = project_path / "chapters" / f"{chapter_number:02}_chapter.md"
    chapter_file.write_text(output, encoding="utf-8")

    summary = summarize_chapter(output)
    with open(project_path / "context" / f"{chapter_number:02}_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    with open(context_path, "a", encoding="utf-8") as f:
        f.write(f"{chapter_title}: {summary}\n")

    hist_file = project_path / "chapters" / "history" / f"{chapter_number:02}_gen1.md"
    hist_file.write_text(output, encoding="utf-8")

    log_history(project_path, {
        "type": "chapter_draft",
        "chapter": chapter_number,
        "model": model_id,
        "prompt": prompt,
        "output": output
    })

    metadata["chapters"].append({"number": chapter_number, "status": "draft"})
    save_metadata(project_path, metadata)

    print(f"Chapter {chapter_number} generated and saved.")

def manage_models(name, list_flag=False, set_primary=None):
    project_path = get_project_path(name)
    metadata = load_metadata(project_path)

    if list_flag:
        print("Available models:")
        for m in metadata["models"]["available"]:
            tag = " (primary)" if m == metadata["models"]["primary"] else ""
            print(f" - {m}{tag}")
        return

    if set_primary:
        if set_primary not in metadata["models"]["available"]:
            metadata["models"]["available"].append(set_primary)
        metadata["models"]["primary"] = set_primary
        save_metadata(project_path, metadata)
        print(f"Primary model set to: {set_primary}")
