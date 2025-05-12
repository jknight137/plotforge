# PlotForge

PlotForge is a local-first, model-flexible fiction-writing engine that guides your story one chapter at a time — using LLMs like OpenAI's GPT-4 or local Ollama models.

---

## Features

- Per-chapter and per-page generation workflow
- Dual-outline system: narrative + structured JSON
- Page-by-page context and approval loop
- Full support for OpenAI + Ollama models
- Theme and premise driven long-form writing
- Automatic chapter concatenation and summaries
- Extensible CLI built for authors

---

## Installation

1. Clone this repo and navigate into it:

   ```bash
   git clone https://github.com/your-user/plotforge.git
   cd plotforge
   ```

2. Set up your Python environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set your OpenAI key:
   - Create a `.env` file in the root:
     ```
     OPENAI_API_KEY=sk-...
     ```

---

## Usage

1. Prepare these input files:

   - `theme.txt` – 1-line abstract idea
   - `premise.txt` – 1–3 paragraph setup

2. Create a project:

   ```bash
   python src/main.py new "MyNovel"
   ```

3. Generate and approve the outline:

   ```bash
   python src/main.py generate-outline "MyNovel" --model gpt-4-1106-preview
   python src/main.py approve-outline "MyNovel"
   ```

4. Write a chapter (e.g., 8 pages):

   ```bash
   python src/main.py write-chapter "MyNovel" --number 1 --pages 8
   ```

5. Approve and summarize:
   ```bash
   python src/main.py approve-chapter "MyNovel" --number 1 --pages 8
   python src/main.py summarize-chapter "MyNovel" --number 1
   ```

---

## Project Structure

```
projects/MyNovel/
├── project.json
├── theme.txt, premise.txt
├── chapters/
│   └── chapter_1/
│       ├── page_1_draft.md
│       ├── ...
│       ├── chapter_1_final.md
│       └── chapter_1_summary.txt
├── summaries/
└── context/
    └── chapter_1_summary.txt
```

---

## Notes

- All page generation includes context-aware prompting using previous summaries
- If `outline_raw.txt` exists, it is preferred over `outline.json` for writing
- You can mix OpenAI and local models in the same project
