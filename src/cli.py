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

    metadata = {
        "title": name,
        "theme": "",
        "models": {
            "primary": "meta-llama/Llama-2-7b-chat-hf",
            "available": ["meta-llama/Llama-2-7b-chat-hf"]
        },
        "chapters": []
    }

    with open(project_path / "project.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    (project_path / "outline.md").touch()
    (project_path / "context" / "story_so_far.md").touch()

    init_git_repo(project_path)
    print(f"Project '{name}' created successfully.")

def generate_outline(name, model_override=None):
    project_path = get_project_path(name)
    if not (project_path / "project.json").exists():
        print(f"Project '{name}' does not exist. Run 'new' first.")
        return

    metadata = load_metadata(project_path)
    model_id = model_override or metadata["models"]["primary"]

    prompt = (
        f"Generate an engaging outline for a fiction novel titled '{metadata['title']}'. "
        "Include 10 chapters with short summaries."
    )

    model = AIModel(model_id)
    outline = model.generate(prompt)

    with open(project_path / "outline.md", "w", encoding="utf-8") as f:
        f.write(outline)

    log_history(project_path, {
        "type": "outline",
        "model": model_id,
        "prompt": prompt,
        "output": outline
    })

    print("Outline generated successfully.")

def summarize_chapter(text):
    return text[:250].replace("\n", " ") + "..."

def generate_chapter(name, chapter_number, model_override=None):
    project_path = get_project_path(name)
    metadata = load_metadata(project_path)
    model_id = model_override or metadata["models"]["primary"]
    model = AIModel(model_id)

    outline_path = project_path / "outline.md"
    if not outline_path.exists():
        print("Outline not found. Generate one first.")
        return

    chapter_title = f"Chapter {chapter_number}"
    outline = outline_path.read_text(encoding="utf-8")
    context_path = project_path / "context" / "story_so_far.md"
    story_so_far = context_path.read_text(encoding="utf-8")

    prompt = (
        f"{story_so_far}\n\n"
        f"Using the outline:\n{outline}\n\n"
        f"Write the full text for {chapter_title} in a compelling and consistent narrative style."
    )

    output = model.generate(prompt, max_length=800)

    chapter_file = project_path / "chapters" / f"{chapter_number:02}_chapter.md"
    chapter_file.write_text(output, encoding="utf-8")

    # Save summary for future context
    summary = summarize_chapter(output)
    with open(project_path / "context" / f"{chapter_number:02}_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    # Update story so far
    with open(context_path, "a", encoding="utf-8") as f:
        f.write(f"{chapter_title}: {summary}\n")

    # Save to history
    hist_file = project_path / "chapters" / "history" / f"{chapter_number:02}_gen1.md"
    hist_file.write_text(output, encoding="utf-8")

    log_history(project_path, {
        "type": "chapter_draft",
        "chapter": chapter_number,
        "model": model_id,
        "prompt": prompt,
        "output": output
    })

    print(f"Chapter {chapter_number} generated successfully.")

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
