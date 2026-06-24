# 🛡️ CodeSentinel – AI-Powered Pull Request Security Reviewer

CodeSentinel is an AI-powered GitHub App that automatically reviews Pull Requests for security vulnerabilities, code quality issues, performance bottlenecks, and potential bugs before code reaches production.

Built using FastAPI, Celery, Redis, GitHub Apps, RAG (Retrieval-Augmented Generation), and Large Language Models (Groq/OpenAI), CodeSentinel provides contextual, line-level code reviews directly inside GitHub Pull Requests.

---

# 🚀 Features

### 🔍 Automated Pull Request Review

* Reviews every incoming Pull Request automatically.
* Performs line-by-line analysis of code changes.
* Generates contextual findings with explanations and fixes.

### 🛡️ Security Analysis

Detects:

* Hardcoded secrets
* API key exposure
* Authentication issues
* Authorization flaws
* Input validation problems
* OWASP Top 10 vulnerabilities

### 📈 Code Quality Review

Identifies:

* Dead code
* Maintainability issues
* Error handling problems
* Complexity concerns
* Best-practice violations

### ⚡ Performance Analysis

Finds:

* Inefficient logic
* Expensive operations
* Redundant processing
* Potential bottlenecks

### 🧠 Intent-Aware Reviews

CodeSentinel:

1. Reads PR title and description.
2. Extracts linked issue information.
3. Understands developer intent.
4. Reviews code relative to intended behavior.

### 📚 RAG-Powered Context Retrieval

Uses Retrieval-Augmented Generation to:

* Retrieve related code context.
* Improve review accuracy.
* Reduce hallucinations.
* Provide more relevant suggestions.

### 💬 GitHub Native Comments

Posts:

* Inline code review comments
* Pull Request summaries
* Security findings
* Fix recommendations

---

# 🏗️ Architecture

```text
GitHub PR
    │
    ▼
GitHub Webhook
    │
    ▼
FastAPI Backend
    │
    ▼
Celery Queue
    │
    ▼
Intent Extraction
    │
    ▼
Diff Chunking
    │
    ▼
RAG Context Retrieval
    │
    ▼
LLM Security Review
    │
    ▼
Finding Extraction
    │
    ▼
GitHub Review Comments
```

---

# 🛠️ Tech Stack

## Backend

* FastAPI
* Python
* Celery
* Redis

## AI / LLM

* Groq API
* OpenAI (Fallback)
* Retrieval-Augmented Generation (RAG)

## GitHub Integration

* GitHub Apps
* GitHub Webhooks
* PyGithub

## Database

* PostgreSQL
* SQLAlchemy

## Deployment

* Docker
* Docker Compose

---

# 📂 Project Structure

```text
CodeSentinel/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   ├── models/
│   │   ├── webhook/
│   │   └── main.py
│   │
│   ├── prompts/
│   │   ├── system_prompt.txt
│   │   └── security_prompt.txt
│   │
│   └── worker/
│
├── frontend/
│
├── docker-compose.yml
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/CodeSentinel.git
cd CodeSentinel
```

## Create Virtual Environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
GITHUB_APP_ID=
GITHUB_PRIVATE_KEY=
GITHUB_WEBHOOK_SECRET=

GROQ_API_KEY=
OPENAI_API_KEY=

REDIS_URL=
DATABASE_URL=

STATUS_CONTEXT=CodeSentinel/review
```

---

# ▶️ Running the Backend

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

---

# ⚙️ Running Celery Worker

```bash
celery -A worker.celery_app worker -P solo -l info
```

---

# 🐳 Docker Deployment

```bash
docker-compose up --build
```

---

# 🔗 GitHub App Setup

1. Create a GitHub App.
2. Configure webhook URL.
3. Generate private key.
4. Install app on repository.
5. Grant:

   * Pull Requests (Read & Write)
   * Contents (Read)
   * Metadata (Read)
   * Commit Statuses (Read & Write)

---

# 🔄 Review Pipeline

1. GitHub webhook receives PR event.
2. FastAPI validates payload.
3. Celery queues review job.
4. Intent extractor analyzes PR purpose.
5. Diff is chunked for processing.
6. RAG retrieves related context.
7. LLM performs security review.
8. Findings are normalized.
9. GitHub comments are posted.
10. Review summary is generated.

---

# 📊 Example Finding

```json
{
  "severity": "HIGH",
  "category": "Security",
  "file_path": "auth.py",
  "line": 42,
  "issue": "Hardcoded API Key",
  "fix": "Move secret to environment variables.",
  "confidence": 0.94
}
```

---

# 🎯 Key Highlights

* AI-Powered Security Reviewer
* Intent-Aware Pull Request Analysis
* RAG-Enhanced Context Understanding
* GitHub Native Integration
* Automated Code Review Workflow
* Production-Ready Architecture
* Extensible LLM Framework

---

# 📈 Future Improvements

* Multi-Agent Review System
* CVE Database Integration
* Security Knowledge Graph
* Semantic Code Search
* Repository Memory
* PR Risk Scoring
* Developer Analytics Dashboard

---

# 👨‍💻 Author

**Shubham Gupta**

B.Tech CSIT (AI/ML)
Acropolis Institute of Technology and Research, Indore

GitHub: https://github.com/ShubhamGupta2610

---

# ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.
