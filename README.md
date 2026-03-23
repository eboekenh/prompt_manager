# 📝 Prompt Manager — AI Prompt Library & Organizer

A collection of prompt management tools built with Streamlit and Flask for organizing, categorizing, searching, and reusing AI prompts across different LLM platforms.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Flask](https://img.shields.io/badge/Flask-API-green)
![License](https://img.shields.io/badge/License-MIT-green)

## Included Applications

### 1. Gemini Prompt Manager (`gemini_app.py`) — Recommended
Full-featured Streamlit app with SQLite persistence:
- Create, edit, delete, and search prompts
- Category-based organization
- Persistent storage via SQLite database

### 2. Simple Prompt Manager (`app.py`)
Lightweight Streamlit app with session-based storage:
- Quick add/delete/favorite prompts
- Category filtering and text search
- No database required (session-only)

### 3. Flask Prompt Manager (`prompt_manager_app.py`)
Multi-user web application with authentication:
- User registration and login
- Full CRUD for prompts, categories, and conversations
- REST API endpoint (`/api/prompts`)
- Conversation tracking with LLM model and rating

## Tech Stack

- **Streamlit** — Rapid web UI for data apps
- **Flask** — Full-featured web framework with auth
- **SQLite / SQLAlchemy** — Database persistence
- **python-dotenv** — Environment variable management

## Getting Started

```bash
git clone https://github.com/eboekenh/prompt_manager.git
cd prompt_manager
pip install -r requirements.txt
```

### Run Streamlit version (recommended):
```bash
streamlit run gemini_app.py
```

### Run Flask version:
```bash
python prompt_manager_app.py
```

## License

MIT
