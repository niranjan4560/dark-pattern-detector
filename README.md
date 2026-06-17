# 🔍 Dark Pattern Detector

> AI-powered tool to expose manipulative UI design patterns on websites.
> Built with **FastAPI · PostgreSQL · Google Gemini AI · Streamlit · Docker**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Try_it_now-6d28d9?style=flat-square)](https://dark-pattern-detector-1-66q6.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?style=flat-square)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-2.5_Flash-orange?style=flat-square)](https://aistudio.google.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square)](https://docker.com)

**🔗 Live App:** [dark-pattern-detector-1-66q6.onrender.com](https://dark-pattern-detector-1-66q6.onrender.com)
**🔗 API Docs:** [dark-pattern-detector-dz53.onrender.com/docs](https://dark-pattern-detector-dz53.onrender.com/docs)

---

## 🎯 What It Solves

Dark patterns are manipulative UI tricks companies use to deceive users — pre-selected checkboxes, fake countdown timers, hidden fees, guilt-trip decline buttons. This tool **automatically detects and scores** these patterns on any website using AI.

**Real impact:** Every Indian loses money to dark patterns monthly. IRCTC pre-selects travel insurance. Swiggy pre-checks donation. Amazon uses fake urgency. This tool exposes all of it with a structured 0-100 credibility score.

---

## ✨ Features

- **🔎 URL Analyzer** — Scrape and analyze any website with one click
- **📝 Text Analyzer** — Paste page content for instant analysis (works even when sites block scrapers)
- **🤖 Gemini AI** — Google's Gemini 2.5 Flash detects 10 dark pattern types with confidence scoring
- **📊 Credibility Score** — 0-100 score with Safe / Caution / Suspicious / Dangerous labels
- **📄 PDF Reports** — Downloadable professional analysis reports
- **🗄️ Community Database** — Report and upvote dark patterns crowdsourced from real users
- **📈 Analytics Dashboard** — Trends, most common patterns, worst offenders leaderboard
- **🐳 Docker Ready** — Containerized for consistent local + cloud deployment

---

## 🔍 Dark Patterns Detected

| Pattern | Description | Example |
|---|---|---|
| **Fake Urgency** | False time/scarcity pressure | "Only 2 left! Expires in 05:00" |
| **Hidden Costs** | Fees revealed only at checkout | ₹49 convenience fee at final step |
| **Trick Questions** | Confusing opt-in/opt-out | Pre-ticked newsletter checkbox |
| **Roach Motel** | Easy in, hard to leave | No visible cancel button |
| **Misdirection** | Attention manipulation | Decline button 5x smaller |
| **Forced Continuity** | Silent paid conversion | Free trial auto-charges |
| **Fake Social Proof** | Fabricated popularity | "1,247 people viewing this" |
| **Confirm Shaming** | Guilt-trip language | "No thanks, I hate saving money" |
| **Disguised Ads** | Ads styled as content | Sponsored results without label |
| **Privacy Zuckering** | Excessive data collection | Default max data sharing |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT FRONTEND  (Render Web Service)        │
│  Analyze URL · Paste Content · Database · Analytics          │
└──────────────────────┬─────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼─────────────────────────────────────┐
│               FASTAPI BACKEND  (Render Web Service)          │
│  /api/analyze  /api/reports  /api/patterns  /api/analytics   │
└──────────┬──────────────────────────┬────────────────────────┘
           │                          │
┌──────────▼──────────┐   ┌───────────▼───────────────────────┐
│  PostgreSQL (Render) │   │      GOOGLE GEMINI AI              │
│  analysis_results    │   │  gemini-2.5-flash (FREE tier)      │
│  detected_patterns   │   │  with automatic model fallback     │
│  community_reports   │   │  • Dark pattern detection          │
│  pattern_stats       │   │  • Credibility scoring             │
└──────────────────────┘   └────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1 — Run Locally (5 minutes)

```bash
git clone https://github.com/niranjan4560/dark-pattern-detector.git
cd dark-pattern-detector

cp .env.example .env
# Edit .env → add your GEMINI_API_KEY
# Get free key at: https://aistudio.google.com/app/apikey

pip install -r requirements.txt

# Terminal 1 — Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

Open **http://localhost:8501**

### Option 2 — Docker (One Command)

```bash
cp .env.example .env  # Add your GEMINI_API_KEY
docker-compose up --build
```

### Option 3 — Windows (Double-Click)

```
1. Extract zip
2. Add GEMINI_API_KEY to .env
3. Double-click start_windows.bat
```

---

## 🌐 Deploy on Render (Free)

This repo is already live on Render. To deploy your own copy:

```
1. Fork this repo to your GitHub
2. Go to render.com → New → Web Service (backend)
   Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
3. Go to render.com → New → Web Service (frontend)
   Start Command: streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
4. Create a free PostgreSQL database on Render, link DATABASE_URL to backend
5. Set GEMINI_API_KEY on the backend service
6. Set API_BASE (pointing to your backend URL + /api) on the frontend service
```

Full step-by-step guide in [`DEPLOY_RENDER.md`](DEPLOY_RENDER.md).

---

## 📁 Project Structure

```
dark-pattern-detector/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── models/models.py         # SQLAlchemy database models
│   ├── routers/
│   │   ├── analyze.py           # URL & text analysis endpoints
│   │   ├── reports.py           # PDF & JSON report generation
│   │   ├── database_routes.py   # Community reports & search
│   │   └── analytics.py         # Dashboard statistics
│   ├── services/
│   │   ├── ai_analyzer.py       # Gemini AI integration with model fallback
│   │   └── scraper.py           # Web scraping (httpx + BeautifulSoup)
│   └── utils/db.py              # Database setup (SQLite local / PostgreSQL prod)
├── frontend/app.py              # Streamlit UI — 5 pages
├── database/seed.py             # Sample data seeder
├── tests/test_api.py            # Unit tests
├── docker-compose.yml           # Full stack Docker setup
├── render.yaml                  # Render.com deployment config
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variables template
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze/url` | Analyze website URL |
| `POST` | `/api/analyze/text` | Analyze pasted content |
| `GET` | `/api/analyze/history` | Recent analysis history |
| `GET` | `/api/reports/{id}/pdf` | Download PDF report |
| `GET` | `/api/reports/{id}/json` | Get JSON report |
| `POST` | `/api/patterns/report` | Submit community report |
| `GET` | `/api/patterns/leaderboard` | Worst offenders |
| `GET` | `/api/analytics/summary` | Dashboard statistics |

**Interactive API docs:** [dark-pattern-detector-dz53.onrender.com/docs](https://dark-pattern-detector-dz53.onrender.com/docs)

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## 🐳 Docker Commands

```bash
docker-compose up --build          # Start everything
docker-compose up -d               # Background mode
docker-compose exec backend python database/seed.py  # Load sample data
docker-compose logs -f backend     # View backend logs
docker-compose down                # Stop all services
docker-compose down -v             # Stop + delete database
```

---

## 💡 Interview Talking Points

**"How does the AI detection work?"**
> "I engineered a structured prompt for Gemini 2.5 Flash that instructs it to analyze 10 specific dark pattern categories. The scraper extracts high-signal content — buttons, forms, price elements, urgency text — before sending it to Gemini. This keeps the AI focused on manipulation indicators rather than general page content. I also built a model fallback chain so if Google deprecates a model version, the app automatically tries the next one instead of breaking."

**"How would this scale to 1M users?"**
> "I'd add Redis caching for repeated URL analyses (same URL within 24h returns cached result), PostgreSQL read replicas for analytics queries, and Celery for async scraping to handle request spikes. The Gemini API has rate limits, so a job queue would prevent overwhelming it."

**"Why PostgreSQL over MongoDB?"**
> "The data is highly relational — analyses have patterns, patterns have community reports, all feeding analytics aggregations. SQL window functions make the leaderboard queries clean. A document store would complicate the join logic without adding value here."

**"What's the credibility scoring algorithm?"**
> "Each pattern has a severity weight — Critical=40, High=25, Medium=15, Low=5. I multiply by AI confidence score and deduct from 100. It reflects real harm potential — a high-confidence critical pattern tanks the score more than a low-confidence minor issue."

**"What was the hardest bug to fix?"**
> "Google deprecated the Gemini model I originally used mid-deployment — it returned a 404 in production despite working locally. I fixed it by adding a fallback chain that tries several model versions in order, with logging so I can see which one succeeds. That's the kind of resilience real production systems need."

---

## 👤 Author

**Niranjan N S** — Computer Science, Amrita Vishwa Vidyapeetham

[![LinkedIn](https://img.shields.io/badge/LinkedIn-niranjan--n--s-blue?style=flat-square)](https://linkedin.com/in/niranjan-n-s)
[![GitHub](https://img.shields.io/badge/GitHub-niranjan4560-black?style=flat-square)](https://github.com/niranjan4560)
[![Email](https://img.shields.io/badge/Email-niranjanns281%40gmail.com-red?style=flat-square)](mailto:niranjanns281@gmail.com)

---
