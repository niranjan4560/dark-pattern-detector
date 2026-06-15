from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routers import analyze, reports, database_routes, analytics
from backend.utils.db import init_db
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Dark Pattern Detector API",
    description="""
## 🔍 Dark Pattern Detector

AI-powered tool to expose manipulative UI design patterns on websites.

### Features
- **URL Analysis** — Scrape and analyze any website
- **Text Analysis** — Paste page content for analysis
- **10 Dark Pattern Types** — Fake urgency, hidden costs, trick questions, and more
- **PDF Reports** — Downloadable analysis reports
- **Community Database** — Report and upvote patterns
- **Analytics Dashboard** — Trends and statistics

### Built With
FastAPI · PostgreSQL · Google Gemini AI · Streamlit · Docker
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Niranjan N S",
        "email": "niranjanns281@gmail.com",
        "url": "https://linkedin.com/in/niranjan-n-s"
    }
)

# CORS — allow all origins (needed for Streamlit → FastAPI communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router,          prefix="/api/analyze",   tags=["Analysis"])
app.include_router(reports.router,          prefix="/api/reports",   tags=["Reports"])
app.include_router(database_routes.router,  prefix="/api/patterns",  tags=["Community"])
app.include_router(analytics.router,        prefix="/api/analytics", tags=["Analytics"])

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "running",
        "message": "Dark Pattern Detector API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "analyze_url":  "/api/analyze/url",
            "analyze_text": "/api/analyze/text",
            "analytics":    "/api/analytics/summary",
            "community":    "/api/patterns/reports",
        }
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": "1.0.0"}
