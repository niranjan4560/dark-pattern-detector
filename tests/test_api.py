"""
Basic tests for Dark Pattern Detector API
Run with: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Mock database dependency ──────────────────────────────────────────────────
def mock_get_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock(side_effect=lambda x: setattr(x, 'id', 1))
    db.query = MagicMock()
    yield db


# ── Mock AI analyzer ──────────────────────────────────────────────────────────
MOCK_AI_RESULT = {
    "page_title": "Test Website",
    "industry_category": "e-commerce",
    "overall_credibility_score": 58,
    "summary": "Test analysis found several dark patterns.",
    "dark_patterns": [
        {
            "pattern_type": "fake_urgency",
            "pattern_name": "Countdown Timer",
            "severity": "High",
            "confidence_score": 0.89,
            "evidence": "Found countdown timer with no real deadline",
            "location_hint": "Product page",
            "user_impact": "Creates false urgency"
        }
    ],
    "positive_practices": ["Clear return policy"],
    "recommendations": ["Remove countdown timers"]
}

MOCK_SCRAPE_RESULT = {
    "url": "https://test.com",
    "domain": "test.com",
    "title": "Test Website",
    "content": "Sample website content with countdown timer only 2 left hurry",
    "html_length": 5000,
    "error": None
}


# ── Tests ─────────────────────────────────────────────────────────────────────
class TestHealthEndpoint:
    def test_health_check(self):
        """API health endpoint should return healthy"""
        with patch('backend.utils.db.init_db'):
            from backend.main import app
            from backend.utils.db import get_db
            app.dependency_overrides[get_db] = mock_get_db
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        """Root endpoint should return API info"""
        with patch('backend.utils.db.init_db'):
            from backend.main import app
            from backend.utils.db import get_db
            app.dependency_overrides[get_db] = mock_get_db
            client = TestClient(app)
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "version" in data


class TestTextAnalysis:
    def test_text_analysis_success(self):
        """Text analysis endpoint should return results"""
        with patch('backend.utils.db.init_db'), \
             patch('backend.services.ai_analyzer.analyze_text_content') as mock_ai:

            mock_ai.return_value = MOCK_AI_RESULT

            from backend.main import app
            from backend.utils.db import get_db
            app.dependency_overrides[get_db] = mock_get_db
            client = TestClient(app)

            response = client.post("/api/analyze/text", json={
                "content": "Buy now! Only 2 left! Offer expires in 10 minutes! Click here to subscribe. No thanks I don't want to save money.",
                "url": "https://test.com"
            })

            assert response.status_code == 200
            data = response.json()
            assert "credibility_score" in data
            assert "dark_patterns" in data
            assert "analysis_id" in data

    def test_text_analysis_too_short(self):
        """Text analysis should reject too-short content"""
        with patch('backend.utils.db.init_db'):
            from backend.main import app
            from backend.utils.db import get_db
            app.dependency_overrides[get_db] = mock_get_db
            client = TestClient(app)

            response = client.post("/api/analyze/text", json={
                "content": "short",
                "url": "https://test.com"
            })
            assert response.status_code == 400


class TestURLAnalysis:
    def test_url_analysis_with_mock_scraper(self):
        """URL analysis should work with mocked scraper"""
        with patch('backend.utils.db.init_db'), \
             patch('backend.services.scraper.scrape_website') as mock_scrape, \
             patch('backend.services.ai_analyzer.analyze_with_gemini') as mock_ai:

            mock_scrape.return_value = MOCK_SCRAPE_RESULT
            mock_ai.return_value = MOCK_AI_RESULT

            from backend.main import app
            from backend.utils.db import get_db
            app.dependency_overrides[get_db] = mock_get_db
            client = TestClient(app)

            response = client.post("/api/analyze/url", json={
                "url": "https://test.com"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["domain"] == "test.com"
            assert "credibility_score" in data
            assert "dark_patterns" in data


class TestAIAnalyzer:
    def test_mock_analysis_returns_valid_structure(self):
        """Mock analysis should return correct structure"""
        from backend.services.ai_analyzer import _mock_analysis
        result = _mock_analysis("https://test.com")

        assert "dark_patterns" in result
        assert "overall_credibility_score" in result
        assert "summary" in result
        assert "positive_practices" in result
        assert "recommendations" in result
        assert isinstance(result["dark_patterns"], list)

    def test_credibility_score_calculation(self):
        """Credibility score should decrease with more severe patterns"""
        from backend.services.ai_analyzer import calculate_credibility_score

        no_patterns = calculate_credibility_score([])
        assert no_patterns == 90.0

        high_patterns = calculate_credibility_score([
            {"severity": "High", "confidence_score": 0.9},
            {"severity": "High", "confidence_score": 0.9},
        ])
        assert high_patterns < no_patterns

        critical_patterns = calculate_credibility_score([
            {"severity": "Critical", "confidence_score": 1.0},
            {"severity": "Critical", "confidence_score": 1.0},
        ])
        assert critical_patterns < high_patterns

    def test_credibility_score_never_negative(self):
        """Credibility score should never go below 0"""
        from backend.services.ai_analyzer import calculate_credibility_score

        many_critical = [
            {"severity": "Critical", "confidence_score": 1.0}
            for _ in range(20)
        ]
        score = calculate_credibility_score(many_critical)
        assert score >= 0

    def test_severity_labels(self):
        """Severity labels should map correctly to score ranges"""
        from backend.services.ai_analyzer import get_severity_label

        assert get_severity_label(85) == "Safe"
        assert get_severity_label(70) == "Caution"
        assert get_severity_label(50) == "Suspicious"
        assert get_severity_label(30) == "Dangerous"


class TestScraper:
    def test_extract_domain(self):
        """Domain extraction should work correctly"""
        from backend.services.scraper import extract_domain

        assert extract_domain("https://www.amazon.in/product") == "amazon.in"
        assert extract_domain("http://swiggy.com/order") == "swiggy.com"
        assert extract_domain("https://example.com") == "example.com"

    def test_extract_content_from_html(self):
        """Content extraction should handle basic HTML"""
        from backend.services.scraper import extract_content

        sample_html = """
        <html>
            <head><title>Test Shop</title></head>
            <body>
                <button class="btn-buy">Buy Now</button>
                <p>Only 2 left in stock!</p>
                <input type="checkbox" checked id="newsletter">
                <label for="newsletter">Subscribe to newsletter</label>
                <div class="price">₹999</div>
                <footer>Return policy | Contact us</footer>
            </body>
        </html>
        """
        result = extract_content(sample_html, "https://test.com")

        assert result["title"] == "Test Shop"
        assert result["error"] is None
        assert len(result["content"]) > 0
        # Should detect urgency text
        assert "Only 2 left" in result["content"] or "URGENCY" in result["content"]


class TestCommunityRoutes:
    def test_submit_community_report(self):
        """Community report submission should work"""
        with patch('backend.utils.db.init_db'):
            from backend.main import app
            from backend.utils.db import get_db

            db_mock = MagicMock()
            db_mock.add = MagicMock()
            db_mock.commit = MagicMock()
            db_mock.refresh = MagicMock(side_effect=lambda x: setattr(x, 'id', 1))

            def mock_db():
                yield db_mock

            app.dependency_overrides[get_db] = mock_db
            client = TestClient(app)

            response = client.post("/api/patterns/report", json={
                "url": "https://test.com/checkout",
                "reported_pattern_type": "fake_urgency",
                "description": "Countdown timer with no real deadline found on product page",
                "severity_rating": 4
            })

            assert response.status_code == 200
            data = response.json()
            assert "report_id" in data

    def test_invalid_severity_rating(self):
        """Severity rating outside 1-5 should be rejected"""
        with patch('backend.utils.db.init_db'):
            from backend.main import app
            from backend.utils.db import get_db

            app.dependency_overrides[get_db] = mock_get_db
            client = TestClient(app)

            response = client.post("/api/patterns/report", json={
                "url": "https://test.com",
                "reported_pattern_type": "fake_urgency",
                "description": "Test pattern found here with detailed description",
                "severity_rating": 10  # Invalid — should be 1-5
            })
            assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
