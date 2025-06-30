# 💎 Jewelry Inventory System

## Description

A modern, lightweight application to manage, catalog, and analyze a jewelry store’s inventory. Built with FastAPI, SQLModel, and AI integrations, this system offers:

* **Photo upload & processing** (Pillow → thumbnails)
* **Voice note transcription** (Whisper → GPT-4 metadata)
* **AI-powered auto-tagging** (CLIP + GPT-4)
* **Search, filter & CRUD** inventory items
* **Stats dashboard** (total value, distribution by material/gem)
* **Clean, mobile-friendly** admin UI
* **Dockerized deployment** + GitHub Actions CI/CD

## Tech Stack

| Layer          | Technology                                |
| -------------- | ----------------------------------------- |
| **Backend**    | Python 3.11, FastAPI, Uvicorn             |
| **Database**   | SQLModel (SQLite in dev, PostgreSQL prod) |
| **Templates**  | Jinja2, Tailwind CSS                      |
| **Media**      | Pillow, uuid                              |
| **AI**         | Whisper, CLIP, OpenAI GPT-4 API           |
| **Env Mgmt**   | python-dotenv                             |
| **Lint & QA**  | Ruff, Black, isort, pre-commit            |
| **CI/CD**      | GitHub Actions                            |
| **Deployment** | Docker, Fly.io                            |

## Prerequisites

* Git
* Python 3.11
* Poetry
* (Optional) pyenv for managing Python versions
* Docker (for container builds)

## Setup

1. **Clone & enter repo**

   ```bash
   git clone git@github.com:ikatechis/jewel-db.git
   cd jewel-db
   ```

2. **Configure Poetry & virtualenv**

   ```bash
   poetry config virtualenvs.in-project true
   poetry install
   ```

   Creates a local `.venv/` in the project root.

3. **Activate the environment**

   ```bash
   # Option A: Poetry shell
   poetry shell

   # Option B: Source the in-project venv
   source .venv/bin/activate
   ```

4. **Environment variables**
   Copy and edit the example:

   ```bash
   cp .env.example .env
   ```

   ```env
   DATABASE_URL=sqlite:///./app.db
   SECRET_KEY=your-secret-key
   DEBUG=true
   ```

5. **Install & activate pre-commit hooks**

   ```bash
   poetry run pre-commit install
   poetry run pre-commit run --all-files
   ```

6. **Make `run.sh` executable**

   ```bash
   chmod +x run.sh
   ```

## Usage

* **Run dev server**

  ```bash
  ./run.sh
  ```

  Access at `http://0.0.0.0:8000` with auto-reload.

* **Run tests**

  ```bash
  poetry run pytest
  ```

* **Lint & format**

  ```bash
  poetry run ruff --fix .
  poetry run black .
  poetry run isort .
  ```

## Continuous Integration

We enforce linting & formatting on every push & PR via GitHub Actions:

```yaml
# .github/workflows/pre-commit.yml
name: 🛠 Lint & Format

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          python -m pip install --upgrade pip
          pip install pre-commit
      - run: pre-commit run --all-files --show-diff-on-failure
```

## .gitignore

```gitignore
# Python bytecode
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
env/
ENV/

# Environment file
.env

# Database files
*.db
*.sqlite3

# Media uploads
media/

# Build artifacts
build/
dist/
*.egg-info/
.eggs/

# Docker
docker-compose.override.yml
*.log

# IDEs and editors
.vscode/
.idea/
*.sublime-project
*.sublime-workspace

# macOS
.DS_Store

# pyenv
.python-version
```

## Future Improvements

* Add **Alembic** migrations
* Integrate **mypy** or **pyright** for static typing
* Use **sqlfluff** for SQL linting
* Publish **API docs** via Redoc or MkDocs
* Enable **Dependabot** & **safety** scans
* Docker Compose for local multi-service development

---

✨ You’re all set! Next up: defining data models, building CRUD endpoints, and designing the dashboard. Let me know where you’d like to dive in!
