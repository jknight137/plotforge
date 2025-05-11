# PlotForge

PlotForge is a local-first, AI-assisted fiction writing assistant designed for structured human-AI collaboration. It enables a human author to guide the narrative while delegating bulk drafting to a trusted language model.

## ✨ Features

- Project-based structure with git integration
- Theme and outline defined by the human
- Option to import or generate outline
- Long-form chapter generation (~5000 words)
- Model override and management
- Context-aware writing with memory of past chapters
- History logging of all generations

---

## 🔧 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-user/plotforge.git
cd plotforge
```

### 2. Create Virtual Environment (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Authenticate with Hugging Face (if using gated models)

```bash
huggingface-cli login
```

---

## 🚀 Commands

### Create a New Project

```bash
python src/main.py new "MyNovel"
```

You will be prompted to enter a theme or premise.

### Generate Outline via AI

```bash
python src/main.py outline "MyNovel"
```

### Import Your Own Outline

```bash
python src/main.py outline "MyNovel" --from-file outline.md
```

### Generate a Chapter

```bash
python src/main.py generate-chapter "MyNovel" --number 1
```

### Switch Model

```bash
python src/main.py models "MyNovel" --set mistralai/Mistral-7B-Instruct-v0.3
```

### List Available Models

```bash
python src/main.py models "MyNovel" --list
```

---

## 📁 File Structure

```
projects/MyNovel/
├── outline.md                  # Outline (generated or imported)
├── project.json                # Project metadata
├── context/
│   ├── story_so_far.md        # Canonical memory file
│   └── 01_summary.txt         # Per-chapter summary
├── chapters/
│   ├── 01_chapter.md          # Chapter drafts
│   └── history/
│       └── 01_gen1.md         # Generation attempts
├── history.jsonl              # JSON log of all outputs
```

---

## ✅ Future Plans

- Rewrite mode with feedback loops
- Character and location databases
- GUI using tkinter or Electron wrapper
- LLaMA.cpp / GGUF support for fully offline use

---

## License

MIT
