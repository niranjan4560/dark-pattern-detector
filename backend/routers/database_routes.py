from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional, List
from backend.utils.db import get_db
from backend.models.models import CommunityReport, AnalysisResult, DetectedPattern

router = APIRouter()

class CommunityReportRequest(BaseModel):
    url: str
    reported_pattern_type: str
    description: str
    severity_rating: int  # 1-5

class UpvoteRequest(BaseModel):
    report_id: int

@router.post("/report")
async def submit_community_report(
    request: CommunityReportRequest,
    db: Session = Depends(get_db)
):
    """Submit a community-reported dark pattern"""
    if request.severity_rating < 1 or request.severity_rating > 5:
        raise HTTPException(status_code=400, detail="Severity rating must be 1-5")

    domain = request.url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

    report = CommunityReport(
        url=request.url,
        domain=domain,
        reported_pattern_type=request.reported_pattern_type,
        description=request.description,
        severity_rating=request.severity_rating,
        upvotes=0
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {"message": "Report submitted successfully", "report_id": report.id}


@router.get("/reports")
async def get_community_reports(
    limit: int = 20,
    skip: int = 0,
    pattern_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get community-reported dark patterns"""
    query = db.query(CommunityReport)

    if pattern_type:
        query = query.filter(CommunityReport.reported_pattern_type == pattern_type)

    reports = query.order_by(desc(CommunityReport.upvotes))\
                   .offset(skip).limit(limit).all()

    return [
        {
            "id": r.id,
            "url": r.url,
            "domain": r.domain,
            "pattern_type": r.reported_pattern_type,
            "description": r.description,
            "severity_rating": r.severity_rating,
            "upvotes": r.upvotes,
            "verified": r.verified,
            "report_date": r.report_date.isoformat() if r.report_date else None
        }
        for r in reports
    ]


@router.post("/upvote/{report_id}")
async def upvote_report(report_id: int, db: Session = Depends(get_db)):
    """Upvote a community report"""
    report = db.query(CommunityReport).filter(CommunityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.upvotes = (report.upvotes or 0) + 1
    db.commit()

    return {"message": "Upvoted", "total_upvotes": report.upvotes}


@router.get("/leaderboard")
async def get_worst_offenders(limit: int = 10, db: Session = Depends(get_db)):
    """Get domains with most detected dark patterns (leaderboard of worst offenders)"""
    # From AI analyses
    ai_offenders = db.query(
        AnalysisResult.domain,
        func.count(DetectedPattern.id).label("pattern_count"),
        func.avg(AnalysisResult.credibility_score).label("avg_score")
    ).join(
        DetectedPattern, DetectedPattern.analysis_id == AnalysisResult.id
    ).group_by(
        AnalysisResult.domain
    ).order_by(
        desc("pattern_count")
    ).limit(limit).all()

    # From community reports
    community_offenders = db.query(
        CommunityReport.domain,
        func.count(CommunityReport.id).label("report_count"),
        func.avg(CommunityReport.severity_rating).label("avg_severity")
    ).group_by(
        CommunityReport.domain
    ).order_by(
        desc("report_count")
    ).limit(limit).all()

    return {
        "ai_detected_offenders": [
            {
                "domain": o.domain,
                "patterns_detected": o.pattern_count,
                "avg_credibility_score": round(o.avg_score, 1) if o.avg_score else None
            }
            for o in ai_offenders
        ],
        "community_reported_offenders": [
            {
                "domain": o.domain,
                "community_reports": o.report_count,
                "avg_severity_rating": round(o.avg_severity, 1) if o.avg_severity else None
            }
            for o in community_offenders
        ]
    }


@router.get("/search")
async def search_domain(domain: str, db: Session = Depends(get_db)):
    """Search for a specific domain in the database"""
    # Clean domain input
    domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

    analyses = db.query(AnalysisResult)\
        .filter(AnalysisResult.domain.ilike(f"%{domain}%"))\
        .order_by(desc(AnalysisResult.analysis_date))\
        .limit(5).all()

    community = db.query(CommunityReport)\
        .filter(CommunityReport.domain.ilike(f"%{domain}%"))\
        .order_by(desc(CommunityReport.upvotes))\
        .limit(5).all()

    return {
        "domain": domain,
        "ai_analyses": [
            {
                "id": a.id,
                "credibility_score": a.credibility_score,
                "patterns_found": a.total_patterns_found,
                "date": a.analysis_date.isoformat() if a.analysis_date else None
            }
            for a in analyses
        ],
        "community_reports": [
            {
                "pattern_type": c.reported_pattern_type,
                "description": c.description,
                "severity": c.severity_rating,
                "upvotes": c.upvotes
            }
            for c in community
        ]
    }
