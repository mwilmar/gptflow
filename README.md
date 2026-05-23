# 🚀 GPTFlow v1.1.0-RC

AI-powered Instagram content automation platform untuk sekolah training/edukasi. Generate caption, carousel, reels script, dan story secara otomatis menggunakan AI, dengan approval workflow dan scheduling.

## ✨ Features

- 🤖 **AI Content Generator** — Caption, carousel, reels script, story (hybrid Groq + OpenAI)
- 📷 **Image Picker** — Auto-search Unsplash + upload dari komputer
- 📱 **Instagram Preview** — Preview konten seperti tampilan IG asli (dengan gambar)
- 📅 **Content Calendar** — Kalender bulanan dengan color-coded content
- ✅ **Approval Workflow** — Submit → Approve/Reject → Schedule
- 📊 **Dashboard** — Overview stats (total, draft, pending, approved, scheduled)
- 🔐 **Auth** — Register/Login dengan JWT
- 🎨 **Dark Mode UI** — Modern, responsive

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI |
| Database | PostgreSQL (async) |
| AI Primary | Groq API (Llama 3.3 70B) — gratis |
| AI Fallback | OpenAI GPT-4o-mini |
| Frontend | Vanilla HTML/CSS/JS (SPA) |
| Auth | JWT (python-jose + bcrypt) |

## 🚀 Quick Start

```bash
# 1. Setup credentials
cp .env.example .env   # Edit: tambahkan API keys

# 2. Run
./start.sh
```

Browser otomatis terbuka di http://localhost:8000

## 📁 Project Structure (AIDLC)

```
gptflow/
├── app/main.py              # Backend (FastAPI, all endpoints)
├── static/index.html        # Frontend (SPA dashboard)
├── start.sh                 # Launcher
├── requirements.txt         # Python dependencies
├── .env                     # Credentials (not in git)
├── VERSION                  # 1.0.0-RC
│
├── inception/               # AIDLC Phase 1: Design
│   ├── intent/              # Problem statement, objectives
│   ├── vision/              # Product vision, roadmap
│   ├── user_stories/        # 13 user stories
│   ├── requirements/        # Functional & non-functional
│   ├── units/               # Domain decomposition (DDD)
│   ├── business_flow/       # Workflow diagrams
│   ├── functional_design/   # I/O schemas, API contracts
│   ├── non_functional_design/ # Performance, security, scalability
│   ├── wireframe/           # UI mockups + specs
│   └── prompt_design/       # AI prompt templates
│
├── construction/            # AIDLC Phase 2: Build
│   ├── domain_design/       # DDD entities, aggregates
│   ├── logical_design/      # System architecture flow
│   ├── technical_design/    # Tech decisions, project structure
│   ├── architecture/        # System diagrams, Docker, K8s
│   ├── database_design/     # Schema (8 tables, DDL)
│   ├── api_design/          # Full REST API spec
│   ├── prompt_engineering/   # Model config, validation
│   ├── workflow_automation/  # Celery tasks, n8n
│   ├── integration/         # OpenAI, Instagram, OAuth
│   ├── security/            # Auth, RBAC, encryption
│   ├── devops/              # CI/CD, Docker
│   └── testing/             # Test strategy
│
└── operation/               # AIDLC Phase 3: Run
    ├── deployment/          # Checklist, rollback
    ├── monitoring/          # Prometheus, Grafana
    ├── logging/             # Structured JSON logging
    ├── incident_management/ # Severity, playbooks
    ├── analytics/           # Metrics pipeline
    ├── ai_learning/         # Feedback loop
    ├── maintenance/         # Scheduled tasks
    ├── backup/              # Strategy, RTO/RPO
    ├── security_operation/  # Scans, rotation
    ├── runbook/             # 7 operational runbooks
    └── sop/                 # 8 SOPs
```

## ⚙️ Configuration (.env)

```env
OPENAI_API_KEY=sk-...          # OpenAI (fallback)
GROQ_API_KEY=gsk_...           # Groq (primary, free)
AI_PROVIDER=hybrid             # groq | openai | hybrid
UNSPLASH_ACCESS_KEY=...        # Image search (free)
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=<random-32-chars>
```

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login → JWT |
| POST | /api/content/generate | AI generate content |
| GET | /api/content | List content (filterable) |
| POST | /api/content/{id}/submit | Submit for approval |
| POST | /api/content/{id}/approve | Approve |
| POST | /api/content/{id}/reject | Reject |
| POST | /api/content/{id}/schedule | Schedule posting |
| GET | /api/schedule/calendar | Calendar view |
| GET | /api/dashboard | Stats overview |

## 🗺 Roadmap

- [x] v1.0.0-RC — AI generation, approval, scheduling, IG preview
- [x] v1.1.0-RC — Image picker (Unsplash + upload), hybrid AI (Groq + OpenAI)
- [ ] v1.2.0 — Instagram Graph API auto-posting
- [ ] v1.3.0 — Analytics + AI recommendation engine
- [ ] v1.4.0 — Multi-account, role management
- [ ] v2.0.0 — Visual carousel generator, n8n automation

## 📄 License

Private — PT GPTFlow Digital Indonesia
