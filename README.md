# Prototype — Vision-Track (Counseling AI)

> **Prototype for the Vision-Track app** — a hackathon–ready, full‑stack counselling AI application with a React frontend, Django REST backend, and Groq API integration for LLM functionality.

---

## Table of contents

* [Project overview](#project-overview)
* [Demo / Screenshot ideas](#demo--screenshot-ideas)
* [Tech stack](#tech-stack)
* [Prerequisites](#prerequisites)
* [Repository structure](#repository-structure)
* [Quick start (recommended)](#quick-start-recommended)

  * [Clone repository](#clone-repository)
  * [Backend setup (Django)](#backend-setup-django)
  * [Frontend setup (React)](#frontend-setup-react)
  * [Start everything](#start-everything)
* [Environment variables / `.env` examples](#environment-variables--env-examples)
* [Groq API — setup & configuration](#groq-api---setup--configuration)
* [API endpoints & usage examples](#api-endpoints--usage-examples)
* [Development tips & debugging](#development-tips--debugging)
* [Docker (optional)](#docker-optional)
* [Testing](#testing)
* [Deployment notes](#deployment-notes)
* [Contributing](#contributing)
* [License & contact](#license--contact)

---

## Project overview

This repository contains a prototype of **Vision-Track / Counseling AI** — an application that provides an interactive AI-powered career-counseling experience. It consists of:

* A **Django** backend that exposes REST endpoints and orchestrates the LLM calls via Groq API.
* A **React** frontend that handles the user flow (questionnaire, chat UI, loading screens).
* Integration with **Groq API**, a fast and free cloud-based LLM service (models like `llama-3.1-8b-instant`, `mixtral-8x7b-32768`).

This README is written for a hackathon: fast to run, easy to demo, and easy to extend.

---

## Demo / Screenshot ideas

Add screenshots or short GIFs to the `frontend/public` folder and reference them here. Typical demo flow:

1. Set up Groq API key and ensure it's configured in your environment.
2. Start Django backend and React frontend.
3. Visit `http://localhost:3000` and walk through the questionnaire and chat.

---

## Tech stack

* Frontend: React, Tailwind CSS (config included), plain JS components
* Backend: Django, Django REST Framework
* LLM: Groq API (cloud-based, fast inference) with `llama-3.1-8b-instant` or other available models
* Data: SQLite (default for prototype)
* Other: `groq`, `langchain`, `django-cors-headers`, `python-dotenv`

---

## Prerequisites

* Git
* Python 3.10+
* Node.js 16+ and npm
* [Groq API account](https://console.groq.com/) and API key (free tier available)
* (Optional) Docker & Docker Compose if you prefer containerized runs

---

## Repository structure

```
counseling-ai-app/
├── backend/
│   ├── api/                # django app: models, views, serializers
│   ├── counseling_ai/      # django project settings
│   ├── venv/               
│   ├── db.sqlite3
│   ├── manage.py
│   ├── requirements.txt
│   └── .env               # environment variables (create this)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   └── services/
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env               
└── README.md
```

> Note: The repository already includes a working skeleton for both backend and frontend. Follow the Quick start below to run locally.

---

## Quick start (recommended)

Follow these steps in order. Use separate terminals for frontend and backend.

### 1) Clone repository

```bash
git clone https://github.com/Ayanokouji-sama/Prototype.git
cd Prototype
```

### 2) Backend setup (Django)

Open a terminal at `Prototype/backend`.

#### Unix / macOS

```bash
cd backend
python -m venv .venv      # create venv
source .venv/bin/activate
pip install --upgrade pip
# if a requirements.txt exists:
pip install -r requirements.txt
# otherwise install the main deps:
pip install django djangorestframework django-cors-headers python-decouple python-dotenv groq langchain
```

#### Windows (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### DB setup & migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create superuser (optional, for Django admin)

```bash
python manage.py createsuperuser
```

#### Run Django server

```bash
python manage.py runserver 8000
```

By default the backend will run at `http://127.0.0.1:8000/` (adjust if necessary).

> Keep this terminal running.

### 3) Frontend setup (React)

Open a new terminal at `Prototype/frontend`.

```bash
cd frontend
npm install
npm start
```

The dev server will usually open `http://localhost:3000` in your browser. If not, open it manually.

> Keep this terminal running.

### 4) Set up Groq API

Follow the dedicated [Groq API section](#groq-api---setup--configuration) below to get your API key and configure it.

---

## Environment variables / `.env` examples

Below are recommended `.env` variables for both backend and frontend. Place them in `backend/.env` and `frontend/.env`.

### Backend (`backend/.env`)

```
# Django
DJANGO_SECRET_KEY=replace_this_with_a_secure_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Groq API
GROQ_API_KEY=your_actual_groq_api_key_here

# Database (prototype uses sqlite by default so this is optional)
# DATABASE_URL=sqlite:///db.sqlite3
```

### Frontend (`frontend/.env`)

```
# Example used by React to call the backend API
REACT_APP_API_URL=http://127.0.0.1:8000/api
```

> **Important**: Never commit secrets into the repo. Use a `.gitignore` to exclude `.env` files.

---

## Groq API — setup & configuration

This project uses Groq API for fast, cloud-based LLM inference with generous free tier limits.

### 1. Get your Groq API key

1. Visit [console.groq.com](https://console.groq.com/)
2. Sign up for a free account (no credit card required)
3. Navigate to API Keys section
4. Generate a new API key

### 2. Configure your environment

Add your API key to `backend/.env`:

```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Available models

The application uses these Groq models:
- **`llama-3.1-8b-instant`** — Fast and efficient (default)
- **`mixtral-8x7b-32768`** — Good for longer contexts
- **`llama3-70b-8192`** — More capable but slower
- **`gemma2-9b-it`** — Google's Gemma model

### 4. Free tier limits

Groq offers generous free tier:
- **14,400 requests per day**
- **115,000 tokens per minute**
- Very fast inference speeds

### 5. Quick test

Test your API key with curl:

```bash
curl "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model": "llama-3.1-8b-instant"
  }'
```

---

## API endpoints & usage examples

The backend exposes REST endpoints to communicate with the LLM and manage conversations. The exact routes are in `backend/api/urls.py`; common endpoints likely look like:

* `GET /api/` — health / info
* `POST /api/chat/` — send a user message and receive a response
* `POST /api/submit_questionnaire/` — submit initial questionnaire data
* `POST /api/generate_roadmap/` — generate career roadmap

### Example `curl` to backend

```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"I want career advice for becoming a software developer","context":{}}'
```

### Example: calling Groq API directly (for debugging)

```bash
curl "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful career counselor."},
      {"role": "user", "content": "How should I prepare for internships?"}
    ],
    "model": "llama-3.1-8b-instant"
  }'
```

---

## Development tips & debugging

* If the frontend shows CORS errors, ensure `django-cors-headers` is configured and `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`.
* If you get Groq API errors, check:
  - API key is correctly set in `.env`
  - You haven't exceeded rate limits
  - Model name is correct and not deprecated
* Use `python manage.py runserver 0.0.0.0:8000` if you want the backend accessible externally (remember to adjust Django's `ALLOWED_HOSTS`).
* For fast iteration: enable Django debug and use React hot reload.
* Check current available models at: https://console.groq.com/docs/models

---

## Docker (optional)

You can containerize the app — the repo does not include a `docker-compose.yml` by default, but a minimal example follows.

**docker-compose.yml (example)**

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - '8000:8000'
    env_file: ./backend/.env
    volumes:
      - ./backend:/app
  frontend:
    build: ./frontend
    ports:
      - '3000:3000'
    env_file: ./frontend/.env
    volumes:
      - ./frontend:/app
```

Note: Since Groq is a cloud API, no additional container for LLM hosting is needed.

---

## Testing

* Backend: add Django unit tests for `api` views and serializers. Run:

```bash
python manage.py test
```

* Frontend: add basic Jest/React Testing Library tests, run `npm test`.

---

## Deployment notes

* Production Django: use a real DB (Postgres), set `DEBUG=False`, secure `SECRET_KEY`, serve behind Gunicorn + Nginx.
* Groq API: ensure your API key is securely stored (use environment variables or secrets manager).
* Environment and secrets: use a secrets manager or environment variables (don't commit `.env`).
* Rate limits: Monitor your Groq usage in production and implement appropriate rate limiting.

---

## Troubleshooting

* `BadRequestError` from Groq: check if the model name is correct and not deprecated.
* `Authentication error`: verify your `GROQ_API_KEY` is correct and properly loaded from `.env`.
* CORS errors: add the frontend origin to `CORS_ALLOWED_ORIGINS` in Django settings.
* `ModuleNotFoundError`: check Python venv is active and dependencies installed.
* Rate limit errors: check your usage at https://console.groq.com/

---

## Contributing

1. Fork the repo
2. Create a feature branch `git checkout -b feat/your-feature`
3. Commit changes and push
4. Open a pull request describing your changes

Add useful labels: `hackathon`, `feature`, `bug`, `docs`.

---
