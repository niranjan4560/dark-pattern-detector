from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.utils.db import get_db
from backend.models.models import AnalysisResult, DetectedPattern
import io
from datetime import datetime

router = APIRouter()

@router.get("/{analysis_id}/pdf")
async def generate_pdf_report(analysis_id: int, db: Session = Depends(get_db)):
    """Generate a PDF report for a given analysis"""
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    patterns = db.query(DetectedPattern)\
        .filter(DetectedPattern.analysis_id == analysis_id).all()

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)

        styles = getSampleStyleSheet()
        story = []

        # Custom styles
        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                     fontSize=22, textColor=colors.HexColor('#1a1a2e'),
                                     spaceAfter=6)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                       fontSize=14, textColor=colors.HexColor('#16213e'),
                                       spaceAfter=4)
        body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                    fontSize=10, textColor=colors.HexColor('#333333'),
                                    spaceAfter=6, leading=14)
        label_style = ParagraphStyle('Label', parent=styles['Normal'],
                                     fontSize=9, textColor=colors.HexColor('#666666'))

        severity_colors = {
            "Critical": colors.HexColor('#c0392b'),
            "High": colors.HexColor('#e74c3c'),
            "Medium": colors.HexColor('#e67e22'),
            "Low": colors.HexColor('#f39c12')
        }

        # Header
        story.append(Paragraph("🔍 Dark Pattern Detector", title_style))
        story.append(Paragraph("Website Credibility & Manipulation Analysis Report", label_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
        story.append(Spacer(1, 0.15*inch))

        # Summary table
        score = analysis.credibility_score or 0
        if score >= 80:
            label = "SAFE"
            score_color = colors.HexColor('#27ae60')
        elif score >= 60:
            label = "CAUTION"
            score_color = colors.HexColor('#f39c12')
        elif score >= 40:
            label = "SUSPICIOUS"
            score_color = colors.HexColor('#e67e22')
        else:
            label = "DANGEROUS"
            score_color = colors.HexColor('#c0392b')

        summary_data = [
            ["Website", analysis.url[:60] + "..." if len(analysis.url) > 60 else analysis.url],
            ["Domain", analysis.domain or "N/A"],
            ["Industry", (analysis.industry_category or "Unknown").title()],
            ["Analysis Date", datetime.now().strftime("%d %B %Y, %I:%M %p")],
            ["Patterns Detected", str(len(patterns))],
            ["Credibility Score", f"{score}/100 ({label})"],
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 4.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('TEXTCOLOR', (1, 5), (1, 5), score_color),
            ('FONTNAME', (1, 5), (1, 5), 'Helvetica-Bold'),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.2*inch))

        # Dark patterns section
        if patterns:
            story.append(Paragraph(f"⚠️ Dark Patterns Found ({len(patterns)})", heading_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
            story.append(Spacer(1, 0.1*inch))

            for i, pattern in enumerate(patterns, 1):
                sev = pattern.severity or "Low"
                sev_color = severity_colors.get(sev, colors.HexColor('#f39c12'))

                pattern_data = [
                    [f"#{i} {pattern.pattern_name}", f"Severity: {sev}"],
                ]
                pt = Table(pattern_data, colWidths=[4.5*inch, 2*inch])
                pt.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff5f5')),
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('PADDING', (0, 0), (-1, -1), 8),
                    ('TEXTCOLOR', (1, 0), (1, 0), sev_color),
                    ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('LINEBELOW', (0, 0), (-1, -1), 1, sev_color),
                ]))
                story.append(pt)

                details = [
                    ["Type", (pattern.pattern_type or "").replace("_", " ").title()],
                    ["Evidence", pattern.evidence or "N/A"],
                    ["Location", pattern.location_hint or "N/A"],
                    ["Impact", pattern.description or "N/A"],
                    ["Confidence", f"{int((pattern.confidence_score or 0) * 100)}%"],
                ]
                dt = Table(details, colWidths=[1.2*inch, 5.3*inch])
                dt.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
                    ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#eeeeee')),
                ]))
                story.append(dt)
                story.append(Spacer(1, 0.15*inch))
        else:
            story.append(Paragraph("✅ No Dark Patterns Detected", heading_style))
            story.append(Paragraph("This website appears to follow ethical design practices.", body_style))

        # Footer
        story.append(Spacer(1, 0.2*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(
            "Generated by Dark Pattern Detector | AI-powered analysis using Google Gemini",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                          textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
        ))

        doc.build(story)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=dark_pattern_report_{analysis_id}.pdf"}
        )

    except ImportError:
        raise HTTPException(status_code=500, detail="PDF generation requires reportlab. Install with: pip install reportlab")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/{analysis_id}/json")
async def get_json_report(analysis_id: int, db: Session = Depends(get_db)):
    """Get full analysis as JSON"""
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    patterns = db.query(DetectedPattern)\
        .filter(DetectedPattern.analysis_id == analysis_id).all()

    return {
        "report": {
            "generated_at": datetime.now().isoformat(),
            "analysis_id": analysis_id,
            "website": {
                "url": analysis.url,
                "domain": analysis.domain,
                "title": analysis.page_title,
                "industry": analysis.industry_category,
            },
            "credibility": {
                "score": analysis.credibility_score,
                "label": "Safe" if (analysis.credibility_score or 0) >= 80 else
                         "Caution" if (analysis.credibility_score or 0) >= 60 else
                         "Suspicious" if (analysis.credibility_score or 0) >= 40 else "Dangerous",
                "total_patterns": len(patterns)
            },
            "dark_patterns": [
                {
                    "name": p.pattern_name,
                    "type": p.pattern_type,
                    "severity": p.severity,
                    "evidence": p.evidence,
                    "location": p.location_hint,
                    "confidence": p.confidence_score
                }
                for p in patterns
            ]
        }
    }
