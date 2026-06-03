# 🚀 GPTFlow v2.0.0-RC

AI-powered Instagram content automation platform. Generate caption, carousel, reels script, dan story secara otomatis menggunakan AI, dengan approval workflow, scheduling, dan image generation.

## ✨ Features

- 🤖 **AI Content Generator** — Caption, carousel, reels script, story (hybrid Groq + OpenAI)
- ✏️ **Manual Content Creator** — Buat konten manual dengan field dinamis per tipe
- 💡 **AI Suggestions** — Usulan AI kontekstual di setiap field input
- 🎨 **AI Image Generation** — Generate gambar via OpenAI gpt-image-1
- 🔍 **Unsplash Image Search** — Pilih gambar dari Unsplash
- 📁 **Image Upload** — Upload gambar dari komputer
- 📱 **Instagram Preview** — Preview konten seperti tampilan IG asli
- 📅 **Content Calendar** — Kalender bulanan dengan color-coded content
- ✅ **Approval Workflow** — Submit → Approve/Reject → Schedule
- 📊 **Dashboard** — Overview stats (total, draft, pending, approved, scheduled)
- 👥 **User Management** — Admin bisa ubah role user (Creator/Manager/Admin)
- ⚙️ **Personal Config** — Setiap user bisa set API key pribadi (Groq, OpenAI, Instagram)
- 🔐 **Key Verification** — ✅/❌ status real-time untuk setiap API key
- 📅 **Date/Time Picker** — Schedule posting dengan picker visual
- 🎓 **Onboarding Tips** — Step-by-step guided tour + tips per halaman
- 🔐 **Auth** — Register/Login dengan JWT
- 🎨 **Dark Mode UI** — Modern, responsive

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI |
| Database | PostgreSQL (async) |
| AI Primary | Groq API (Llama 3.3 70B) — gratis |
| AI Fallback | OpenAI GPT-4o-mini |
| AI Image | OpenAI gpt-image-1 |
| Image Search | Unsplash API |
| Frontend | Vanilla HTML/CSS/JS (SPA) |
| Auth | JWT (python-jose + bcrypt) |

## 🚀 Quick Start

```bash
cp .env.example .env   # Edit: tambahkan API keys
./start.sh
```

Browser otomatis terbuka di http://localhost:8010

## 📁 Project Structure (AIDLC)

```
gptflow/
├── app/main.py              # Backend (FastAPI, all endpoints)
├── static/index.html        # Frontend (SPA dashboard)
├── start.sh                 # Launcher
├── requirements.txt         # Python dependencies
├── .env.example             # Template credentials
├── VERSION                  # 2.0.0-RC
│
├── inception/               # AIDLC Phase 1: Design
│   ├── intent/
│   ├── vision/
│   ├── user_stories/
│   ├── requirements/
│   ├── units/
│   ├── business_flow/
│   ├── functional_design/
│   ├── non_functional_design/
│   ├── wireframe/
│   ├── prompt_design/
│   └── tutorial/            # User guide & onboarding
│
├── construction/            # AIDLC Phase 2: Build
│   ├── architecture/
│   ├── technical_design/
│   ├── api_design/
│   ├── database_design/
│   ├── domain_design/
│   ├── logical_design/
│   ├── integration/
│   ├── prompt_engineering/
│   ├── workflow_automation/
│   ├── security/
│   ├── testing/
│   └── devops/
│
└── operation/               # AIDLC Phase 3: Run
    ├── deployment/
    ├── monitoring/
    ├── logging/
    ├── backup/
    ├── maintenance/
    ├── incident_management/
    ├── security_operation/
    ├── sop/
    ├── runbook/
    ├── analytics/
    └── ai_learning/
```

## 📋 API Endpoints

| Method | Path | Deskripsi |
|--------|------|-----------|
| POST | `/api/auth/register` | Register user baru |
| POST | `/api/auth/login` | Login |
| GET | `/api/settings` | Get user settings (masked) |
| PUT | `/api/settings` | Update API keys |
| GET | `/api/settings/verify` | Verify semua API keys |
| POST | `/api/content/generate` | AI generate content |
| POST | `/api/content/manual` | Simpan konten manual |
| GET | `/api/content` | List konten (filter by status) |
| POST | `/api/content/{id}/submit` | Submit for approval |
| POST | `/api/content/{id}/approve` | Approve content |
| POST | `/api/content/{id}/reject` | Reject + notes |
| POST | `/api/content/{id}/schedule` | Schedule posting |
| GET | `/api/schedule/calendar` | Calendar view |
| POST | `/api/suggest/{field}` | AI suggestions (generate) |
| POST | `/api/suggest-manual/{field}` | AI suggestions (manual) |
| POST | `/api/generate-image` | AI image generation |
| GET | `/api/unsplash/search` | Search Unsplash images |
| GET | `/api/users` | List users (admin/manager) |
| PUT | `/api/users/{id}/role` | Change user role (admin) |

## 🔑 Roles

| Role | Generate | Submit | Approve | Schedule | Manage Users |
|------|:---:|:---:|:---:|:---:|:---:|
| Creator | ✅ | ✅ | ❌ | ✅ | ❌ |
| Manager | ✅ | ✅ | ✅ | ✅ | View |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |

## Changelog

### v2.0.0-RC (2026-05-25)
- Manual content creator dengan field dinamis per tipe konten
- AI suggestions (💡 Usulan AI) di setiap field input (kontekstual)
- AI image generation (OpenAI gpt-image-1)
- Unified image picker (Pilih Gambar / Upload / Generate AI)
- Personal API config per user (Groq, OpenAI, Instagram)
- API key verification (✅/❌ real-time)
- Quota/error popup dengan redirect ke Config
- User management (admin ubah role via UI)
- Date/time picker untuk schedule
- Step-by-step onboarding tour
- Tips banner per halaman
- Menu numbering untuk navigasi
- Fix: bcrypt compatibility Python 3.14
- Fix: asyncpg/sqlalchemy/openai upgrade untuk Python 3.14

### v1.1.0-RC (2026-05-23)
- Initial release: AI generate, approval workflow, calendar, Unsplash, dark mode
