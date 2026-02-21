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

### Using Cursor with multibranch (evaluating commits)

Yes. Cursor’s Git integration works well with multiple branches and GitHub:

- **Switch branches**: Source Control or command palette → “Git: Checkout to…” so you can open any branch and run the app.
- **See what changed**: Click a file in Source Control or use the timeline to see per-file history; the diff view shows exactly what’s in each commit.
- **Evaluate commits**: Open the commit (or the branch that contains it), select the changed code, and use the AI (e.g. “Review this change” or “Explain this commit”) to get a plain-language summary, spot issues, or suggest improvements.
- **Compare branches**: Checkout `main`, then “Compare with…” another branch to see the full diff; you can ask the AI to review that diff.
- **Pull before work**: Use “Git: Pull” or sync so your local branches match GitHub; then create or checkout feature branches and push when ready.

So you can use Cursor to evaluate any commit or branch: open it, look at the diff, and use the AI to review or explain the changes.

---

## Security note

Because the API key was shared in chat, **consider regenerating it** in the [OpenAI API keys](https://platform.openai.com/api-keys) page and updating the value in your local `.env`. The old key can then be revoked if you want.

---

## WhatsApp + LLM: libraries and how it’s modelled

Goal: connect WhatsApp to an LLM so users can send messages and get simple answers from GenAI.

### High-level flow

1. User sends a WhatsApp message.
2. WhatsApp (via Meta or a provider) sends that message to **our server** (webhook).
3. Our server calls the **LLM** (OpenAI) with the user’s text.
4. We send the LLM’s reply back to the user on WhatsApp.

So we need: a small **web server** that receives webhooks, talks to **OpenAI**, and talks to **WhatsApp**.

### WhatsApp: official API

We use the **WhatsApp Cloud API** (Meta): one webhook URL receives incoming messages, and we send replies via Meta’s HTTP API. No third-party provider (e.g. Twilio) required.

### Libraries we’ll use (Python stack)

| Purpose | Library | Role |
|--------|---------|------|
| **Web server & webhook** | `fastapi` + `uvicorn` | Receives POSTs from WhatsApp Cloud API, returns 200 quickly, processes in the background |
| **WhatsApp (official)** | `httpx` or `requests` | Send replies to Meta’s WhatsApp Cloud API |
| **LLM** | `openai` | Send user message to GPT, get reply |
| **Config** | `python-dotenv` | Load `OPENAI_API_KEY`, `WHATSAPP_TOKEN`, etc. from `.env` |

### FastAPI vs Flask (for this webhook)

**Both can do the same job** for our use case: one (or a few) webhook routes that receive POSTs, call OpenAI, and send a reply. You could build this with Flask and it would work fine.

| | **FastAPI** | **Flask** |
|---|-------------|-----------|
| **Webhooks** | ✅ | ✅ |
| **Async** | Native `async`/`await` (good when calling external APIs like OpenAI and WhatsApp) | Sync by default; async possible but not the default style |
| **Automatic API docs** | Built-in OpenAPI (Swagger) at `/docs` | Via extensions (e.g. Flasgger) |
| **Validation & types** | Request/response models with Pydantic | Manual or with extensions |
| **Maturity** | Newer, very popular in modern Python APIs | Older, huge ecosystem and tutorials |

So: **Flask would achieve the same capabilities** for this project. We’re using FastAPI because it’s a good fit for a small, async-friendly API (calling OpenAI and WhatsApp over the network) and gives us typed payloads and docs out of the box—not because Flask couldn’t do it.

### How it’s modelled (components)

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  WhatsApp   │────▶│  Our backend     │────▶│  OpenAI     │
│  (user)     │     │  (FastAPI)       │     │  (LLM)      │
└─────────────┘     └──────────────────┘     └─────────────┘
       ▲                      │                       │
       │                      │ 1. Receive message    │
       │                      │ 2. Call OpenAI        │
       │                      │ 3. Send reply         │
       └──────────────────────┘                       │
              Reply to user ◀─────────────────────────┘
```

- **Webhook endpoint** (e.g. `POST /webhook/whatsapp`): validates the request, reads the incoming message and user id, calls the LLM, then sends the reply back via WhatsApp API. Respond with 200 quickly so the provider doesn’t retry.
- **LLM module**: one function that takes `(user_message, conversation_id?)`, calls OpenAI (e.g. `chat.completions.create`), returns the assistant text. We can add conversation history later for follow-up questions.
- **Config**: all keys and URLs in `.env` (e.g. `OPENAI_API_KEY`, `WHATSAPP_TOKEN`, `WEBHOOK_VERIFY_TOKEN`), loaded with `load_dotenv()`.

No database is required for “simple questions”: stateless request → LLM → reply. We can add a small in-memory or Redis store later if we want multi-turn context per user.

### Suggested next steps

1. Add to `requirements.txt`: `fastapi`, `uvicorn`, `httpx`, keep `openai` and `python-dotenv`.
2. Implement: one webhook route (WhatsApp Cloud API), one LLM call, one “send reply” call to Meta’s API; run locally and expose with **ngrok** (or similar) so WhatsApp can reach your machine.
3. Optional: add a “health” route (e.g. `GET /health`) and use Cursor + Git branches to iterate and evaluate each commit as you go.
