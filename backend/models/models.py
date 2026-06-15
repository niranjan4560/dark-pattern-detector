from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    domain = Column(String(200))
    analysis_date = Column(DateTime, default=datetime.utcnow)
    credibility_score = Column(Float)
    total_patterns_found = Column(Integer, default=0)
    screenshot_path = Column(String(500), nullable=True)
    page_title = Column(String(500), nullable=True)
    industry_category = Column(String(100), nullable=True)
    html_length = Column(Integer, nullable=True)
    analysis_duration_seconds = Column(Float, nullable=True)
    is_community_reported = Column(Boolean, default=False)

class DetectedPattern(Base):
    __tablename__ = "detected_patterns"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, nullable=False)
    pattern_type = Column(String(100), nullable=False)
    pattern_name = Column(String(200), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text)
    evidence = Column(Text)
    location_hint = Column(String(500), nullable=True)
    confidence_score = Column(Float)
    detected_date = Column(DateTime, default=datetime.utcnow)

class CommunityReport(Base):
    __tablename__ = "community_reports"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    domain = Column(String(200))
    reported_pattern_type = Column(String(100))
    description = Column(Text)
    severity_rating = Column(Integer)
    report_date = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    upvotes = Column(Integer, default=0)

class PatternStats(Base):
    __tablename__ = "pattern_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_analyses = Column(Integer, default=0)
    total_patterns_detected = Column(Integer, default=0)
    most_common_pattern = Column(String(100))
    avg_credibility_score = Column(Float)
    most_analyzed_domain = Column(String(200))
