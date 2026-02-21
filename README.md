# WhatsApp + LLM Project

Project to connect WhatsApp with an LLM (OpenAI).

## API key (safe usage)

- Your OpenAI key is stored in **`.env`** (not committed to Git).
- In code, load it from the environment, e.g. with `python-dotenv`:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

- **Never** put the real key in code or commit `.env` to GitHub.
- New clones: copy `.env.example` to `.env` and add your key locally.

---

## venv vs load_dotenv (what’s the difference?)

| | **venv** (virtual environment) | **load_dotenv()** (python-dotenv) |
|---|---|---|
| **What it does** | Isolates your project’s Python and installed packages | Loads variables from a `.env` file into your app (e.g. API keys) |
| **Solves** | “Which Python and which packages?” | “Where do config and secrets come from?” |
| **Example** | `python -m venv .venv` then `pip install -r requirements.txt` | `load_dotenv()` then `os.getenv("OPENAI_API_KEY")` |

- **venv** = dependency isolation (so this project doesn’t mix with others or the system).
- **load_dotenv** = safe config/secrets (so the key lives in `.env`, not in code).

You can use both: create a venv for the project and use `load_dotenv()` in your code to read the API key from `.env`.

**Optional – use a venv for this project:**

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

---

## Git and GitHub

### Is it a good idea to use GitHub?

**Yes**, for:

- Version history and backups
- Collaboration and portfolio
- Easy deployment (e.g. GitHub Actions)

**Your `.env` is safe** as long as it stays in `.gitignore` (it is). Only `.env.example` (without the real key) should be committed.

### First-time Git setup (one time per machine)

1. **Install Git**: https://git-scm.com/download/win  
2. **Configure your name and email** (used in commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Turn this folder into a Git repo and push to GitHub

1. **Initialize Git** in the project folder:

```bash
cd "c:\Users\jlbma\OneDrive\6.0 Desenvolvimentos\1.0 - GenAI project"
git init
```

2. **Add and commit** your files (`.env` will be ignored):

```bash
git add .
git status   # confirm .env is NOT listed
git commit -m "Initial commit: project setup and safe env config"
```

3. **Create a repo on GitHub**  
   - Go to https://github.com/new  
   - Create a new repository (e.g. `whatsapp-llm`).  
   - Do **not** add a README, .gitignore, or license (you already have them).

4. **Connect and push** (replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub repo):

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Daily workflow (short)

- After changing files:  
  `git add .` → `git commit -m "Describe what you did"` → `git push`

---

## Security note

Because the API key was shared in chat, **consider regenerating it** in the [OpenAI API keys](https://platform.openai.com/api-keys) page and updating the value in your local `.env`. The old key can then be revoked if you want.
