import os
import json
from git_manager import init_git_repo

def create_project(name):
    project_path = f"../projects/{name}"
    os.makedirs(f"{project_path}/chapters", exist_ok=True)
    
    metadata = {
        "title": name,
        "theme": "",
        "chapters": [],
        "model": "meta-llama/Llama-2-7b-chat-hf"
    }

    with open(f"{project_path}/project.json", "w") as f:
        json.dump(metadata, f, indent=4)

    open(f"{project_path}/outline.md", "w").close()

    init_git_repo(project_path)
    print(f"Project '{name}' created successfully.")
    
from models import AIModel

def generate_outline(name):
    project_path = f"../projects/{name}"
    with open(f"{project_path}/project.json") as f:
        metadata = json.load(f)

    prompt = f"Generate an engaging outline for a fiction novel titled '{metadata['title']}'. Include 10 chapters with short summaries."
    model = AIModel(metadata["model"])
    outline = model.generate(prompt)

    with open(f"{project_path}/outline.md", "w", encoding="utf-8") as f:
        f.write(outline)

    print("Outline generated successfully.")
