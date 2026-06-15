"""
Seed the database with sample data for demo/testing purposes.
Run with: python database/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Base, AnalysisResult, DetectedPattern, CommunityReport
from datetime import datetime, timedelta
import random

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://darkpattern_user:darkpattern_pass@localhost:5432/darkpattern_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

SAMPLE_ANALYSES = [
    {
        "url": "https://amazon.in/gp/cart/view.html",
        "domain": "amazon.in",
        "credibility_score": 55.0,
        "total_patterns_found": 3,
        "page_title": "Amazon.in Shopping Cart",
        "industry_category": "e-commerce",
        "patterns": [
            {
                "pattern_type": "fake_urgency",
                "pattern_name": "Low Stock Warning",
                "severity": "High",
                "description": "Creates rush buying decisions",
                "evidence": "'Only 3 left in stock - order soon' displayed on multiple items",
                "location_hint": "Product listing, next to Add to Cart",
                "confidence_score": 0.91
            },
            {
                "pattern_type": "social_proof_manipulation",
                "pattern_name": "Real-time Viewer Count",
                "severity": "Medium",
                "description": "Unverifiable social pressure",
                "evidence": "'15 people are viewing this right now'",
                "location_hint": "Product detail page",
                "confidence_score": 0.78
            },
            {
                "pattern_type": "misdirection",
                "pattern_name": "Subscribe & Save Pre-selection",
                "severity": "Medium",
                "description": "Auto-selects subscription over one-time purchase",
                "evidence": "Subscribe & Save option pre-selected by default",
                "location_hint": "Purchase option selector",
                "confidence_score": 0.85
            }
        ]
    },
    {
        "url": "https://swiggy.com/checkout",
        "domain": "swiggy.com",
        "credibility_score": 62.0,
        "total_patterns_found": 2,
        "page_title": "Swiggy Checkout",
        "industry_category": "food-delivery",
        "patterns": [
            {
                "pattern_type": "trick_questions",
                "pattern_name": "Pre-selected Donation",
                "severity": "Medium",
                "description": "Pre-selects charity donation without explicit consent",
                "evidence": "'Donate ₹5 to Feeding India' checkbox pre-ticked at checkout",
                "location_hint": "Checkout page, payment section",
                "confidence_score": 0.93
            },
            {
                "pattern_type": "hidden_costs",
                "pattern_name": "Platform Fee Disclosure",
                "severity": "Low",
                "description": "Platform fee added at final checkout step",
                "evidence": "₹5 platform fee appears only at final payment step",
                "location_hint": "Final checkout page",
                "confidence_score": 0.72
            }
        ]
    },
    {
        "url": "https://netflix.com/signup",
        "domain": "netflix.com",
        "credibility_score": 72.0,
        "total_patterns_found": 1,
        "page_title": "Netflix Sign Up",
        "industry_category": "subscription",
        "patterns": [
            {
                "pattern_type": "forced_continuity",
                "pattern_name": "Auto-Renewal Without Reminder",
                "severity": "Medium",
                "description": "No email reminder before annual subscription renews",
                "evidence": "Annual plan auto-renews without 7-day advance reminder",
                "location_hint": "Subscription terms, fine print",
                "confidence_score": 0.80
            }
        ]
    },
    {
        "url": "https://irctc.co.in/nget/booking",
        "domain": "irctc.co.in",
        "credibility_score": 38.0,
        "total_patterns_found": 4,
        "page_title": "IRCTC Train Booking",
        "industry_category": "travel",
        "patterns": [
            {
                "pattern_type": "hidden_costs",
                "pattern_name": "Booking Agent Insurance Pre-selection",
                "severity": "High",
                "description": "Travel insurance pre-selected and hard to remove",
                "evidence": "Travel insurance ₹35 pre-ticked, requires active unchecking",
                "location_hint": "Passenger details form",
                "confidence_score": 0.95
            },
            {
                "pattern_type": "trick_questions",
                "pattern_name": "Confusing Opt-out Language",
                "severity": "High",
                "description": "Double negative language in consent checkboxes",
                "evidence": "'Uncheck if you do not wish to not receive offers'",
                "location_hint": "Registration form",
                "confidence_score": 0.88
            },
            {
                "pattern_type": "fake_urgency",
                "pattern_name": "Seat Availability Pressure",
                "severity": "Medium",
                "description": "Rapidly decreasing seat counter to rush booking",
                "evidence": "Seat count visibly decreasing every few seconds on search results",
                "location_hint": "Train search results page",
                "confidence_score": 0.76
            },
            {
                "pattern_type": "misdirection",
                "pattern_name": "Ad-Styled Booking Options",
                "severity": "Medium",
                "description": "Paid partner options visually indistinct from regular results",
                "evidence": "Sponsored hotel and cab options styled identically to organic results",
                "location_hint": "Post-booking cross-sell page",
                "confidence_score": 0.82
            }
        ]
    },
    {
        "url": "https://zomato.com/order",
        "domain": "zomato.com",
        "credibility_score": 68.0,
        "total_patterns_found": 2,
        "page_title": "Zomato Food Ordering",
        "industry_category": "food-delivery",
        "patterns": [
            {
                "pattern_type": "social_proof_manipulation",
                "pattern_name": "Trending Badge Manipulation",
                "severity": "Low",
                "description": "Trending labels applied broadly without clear criteria",
                "evidence": "25+ restaurants on same page all marked as 'Trending Now'",
                "location_hint": "Restaurant listing page",
                "confidence_score": 0.68
            },
            {
                "pattern_type": "hidden_costs",
                "pattern_name": "Rain/Surge Fee Late Disclosure",
                "severity": "Medium",
                "description": "Surge delivery fee only disclosed at cart stage",
                "evidence": "Rain surge fee of ₹30 added at cart, not shown on restaurant page",
                "location_hint": "Cart / checkout page",
                "confidence_score": 0.84
            }
        ]
    }
]

SAMPLE_COMMUNITY_REPORTS = [
    {
        "url": "https://amazon.in",
        "domain": "amazon.in",
        "reported_pattern_type": "fake_urgency",
        "description": "Lightning deals show countdown timers that reset when you reload the page. The urgency is completely fabricated.",
        "severity_rating": 4,
        "upvotes": 23,
        "verified": True
    },
    {
        "url": "https://irctc.co.in",
        "domain": "irctc.co.in",
        "reported_pattern_type": "hidden_costs",
        "description": "Travel insurance is pre-selected during booking and requires 3 different clicks to remove. Many users miss it entirely.",
        "severity_rating": 5,
        "upvotes": 47,
        "verified": True
    },
    {
        "url": "https://linkedin.com/premium",
        "domain": "linkedin.com",
        "reported_pattern_type": "roach_motel",
        "description": "Cancelling LinkedIn Premium requires navigating through 7 screens and multiple confirmation dialogs designed to make you give up.",
        "severity_rating": 4,
        "upvotes": 31,
        "verified": False
    },
    {
        "url": "https://swiggy.com",
        "domain": "swiggy.com",
        "reported_pattern_type": "trick_questions",
        "description": "Donate to Feeding India is pre-checked by default at checkout. Most users don't notice they're donating ₹5 with every order.",
        "severity_rating": 3,
        "upvotes": 18,
        "verified": True
    },
    {
        "url": "https://myntra.com",
        "domain": "myntra.com",
        "reported_pattern_type": "fake_urgency",
        "description": "Sale banners show 'X% off — ends today' but the same sale continues the next day. Verified over multiple weeks.",
        "severity_rating": 3,
        "upvotes": 12,
        "verified": False
    },
    {
        "url": "https://makemytrip.com",
        "domain": "makemytrip.com",
        "reported_pattern_type": "hidden_costs",
        "description": "Flight prices shown on search results do not include mandatory seat selection fees, which are revealed only at final checkout.",
        "severity_rating": 4,
        "upvotes": 28,
        "verified": True
    }
]


def seed_database():
    """Insert sample data into database"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(AnalysisResult).count()
        if existing > 0:
            print(f"⚠️  Database already has {existing} analyses. Skipping seed.")
            print("   To reseed, clear the database first: docker-compose down -v")
            return

        print("🌱 Seeding database with sample data...")

        # Seed analyses
        days_ago = len(SAMPLE_ANALYSES)
        for i, sample in enumerate(SAMPLE_ANALYSES):
            analysis = AnalysisResult(
                url=sample["url"],
                domain=sample["domain"],
                credibility_score=sample["credibility_score"],
                total_patterns_found=sample["total_patterns_found"],
                page_title=sample["page_title"],
                industry_category=sample["industry_category"],
                html_length=random.randint(5000, 50000),
                analysis_duration_seconds=round(random.uniform(1.5, 8.0), 2),
                analysis_date=datetime.utcnow() - timedelta(days=days_ago - i)
            )
            db.add(analysis)
            db.flush()  # Get ID without committing

            for pattern_data in sample["patterns"]:
                pattern = DetectedPattern(
                    analysis_id=analysis.id,
                    pattern_type=pattern_data["pattern_type"],
                    pattern_name=pattern_data["pattern_name"],
                    severity=pattern_data["severity"],
                    description=pattern_data["description"],
                    evidence=pattern_data["evidence"],
                    location_hint=pattern_data["location_hint"],
                    confidence_score=pattern_data["confidence_score"]
                )
                db.add(pattern)

        print(f"   ✅ Added {len(SAMPLE_ANALYSES)} website analyses")

        # Seed community reports
        for report_data in SAMPLE_COMMUNITY_REPORTS:
            report = CommunityReport(
                url=report_data["url"],
                domain=report_data["domain"],
                reported_pattern_type=report_data["reported_pattern_type"],
                description=report_data["description"],
                severity_rating=report_data["severity_rating"],
                upvotes=report_data["upvotes"],
                verified=report_data["verified"],
                report_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(report)

        print(f"   ✅ Added {len(SAMPLE_COMMUNITY_REPORTS)} community reports")

        db.commit()
        print("\n✅ Database seeded successfully!")
        print("   Open http://localhost:8501 to see the dashboard with sample data")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
