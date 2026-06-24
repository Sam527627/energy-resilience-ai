"""
Foresight Voyage Risk Assessment — Branded PDF Generator
Produces a client-ready, HR Maritime / Foresight branded VRA PDF in seconds.
This is the monetisable deliverable: $150 per report, generated in 30 seconds.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from datetime import datetime
import io

# Foresight brand colours (teal/gold)
TEAL = HexColor("#0d6e6e")
DARK_TEAL = HexColor("#08484a")
GOLD = HexColor("#c8a14b")
LIGHT_GREY = HexColor("#f2f5f5")
DARK = HexColor("#1a2332")

RISK_COLORS = {
    "LOW": HexColor("#2e9e5b"),
    "MODERATE": HexColor("#d4a017"),
    "ELEVATED": HexColor("#e07b1a"),
    "HIGH": HexColor("#d63a2f"),
    "CRITICAL": HexColor("#7b0000"),
}


def generate_vra_pdf(vra: dict, output_path: str) -> str:
    """Generate a branded Foresight VRA PDF from a VRA dict."""

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=18*mm, bottomMargin=18*mm,
        leftMargin=16*mm, rightMargin=16*mm
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    brand = ParagraphStyle("brand", parent=styles["Normal"], fontSize=22,
                           textColor=TEAL, fontName="Helvetica-Bold", leading=24)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9,
                         textColor=GOLD, fontName="Helvetica-Bold", leading=12)
    h2 = ParagraphStyle("h2", parent=styles["Normal"], fontSize=12,
                        textColor=DARK_TEAL, fontName="Helvetica-Bold",
                        spaceBefore=10, spaceAfter=5, leading=14)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.5,
                         textColor=DARK, leading=14, alignment=TA_JUSTIFY)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8,
                          textColor=HexColor("#666666"), leading=11)
    white_bold = ParagraphStyle("wb", parent=styles["Normal"], fontSize=10,
                               textColor=HexColor("#ffffff"), fontName="Helvetica-Bold")

    vessel = vra.get("_vessel", {})

    # ── HEADER BANNER ──
    header_data = [[
        Paragraph("FORESIGHT", brand),
        Paragraph("INTELLIGENCE BRIEF<br/><font size=7 color='#666666'>HR MARITIME CONSULTANTS</font>", sub)
    ]]
    header_tbl = Table(header_data, colWidths=[100*mm, 70*mm])
    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(Spacer(1, 8))

    # ── TITLE ──
    title_style = ParagraphStyle("title", parent=styles["Normal"], fontSize=15,
                                 textColor=DARK_TEAL, fontName="Helvetica-Bold")
    story.append(Paragraph("VOYAGE RISK ASSESSMENT", title_style))
    story.append(Spacer(1, 6))

    # ── VESSEL INFO BOX ──
    risk_rating = vra.get("overall_risk_rating", "MODERATE")
    risk_color = RISK_COLORS.get(risk_rating, GOLD)
    risk_score = vra.get("risk_score", 50)

    info_data = [
        ["VESSEL", vra.get("vessel_name", vessel.get("name", "—")),
         "RISK RATING", Paragraph(f"<b>{risk_rating}</b> ({risk_score}/100)", white_bold)],
        ["IMO", vra.get("imo", vessel.get("imo", "—")),
         "TYPE", vessel.get("type", "—")],
        ["ROUTE", vra.get("route", vessel.get("current_route", "—")),
         "FLAG", vessel.get("flag", "—")],
        ["DATE", vra.get("assessment_date", datetime.now().strftime("%Y-%m-%d")),
         "ETA", vessel.get("eta", "—")],
    ]
    info_tbl = Table(info_data, colWidths=[22*mm, 68*mm, 25*mm, 55*mm])
    info_tbl.setStyle(TableStyle([
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0,0), (0,-1), TEAL),
        ("TEXTCOLOR", (2,0), (2,-1), TEAL),
        ("BACKGROUND", (3,0), (3,0), risk_color),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,0), (-1,-2), 0.4, HexColor("#dddddd")),
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
        ("BACKGROUND", (3,0), (3,0), risk_color),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 10))

    # ── EXECUTIVE SUMMARY ──
    story.append(Paragraph("EXECUTIVE SUMMARY", h2))
    story.append(Paragraph(vra.get("executive_summary", ""), body))
    story.append(Spacer(1, 6))

    # ── THREAT ASSESSMENT ──
    story.append(Paragraph("THREAT ASSESSMENT", h2))
    threats = vra.get("threat_assessment", {})
    threat_rows = [["THREAT VECTOR", "LEVEL", "ASSESSMENT"]]
    threat_labels = {
        "piracy_armed_robbery": "Piracy / Armed Robbery",
        "geopolitical_military": "Geopolitical / Military",
        "drone_missile_threat": "Drone / Missile Threat",
        "gps_spoofing_jamming": "GPS Spoofing / Jamming",
        "sea_state_weather": "Sea State / Weather",
    }
    for key, label in threat_labels.items():
        t = threats.get(key, {})
        threat_rows.append([
            label,
            t.get("level", "—"),
            Paragraph(t.get("detail", "—"), ParagraphStyle("td", parent=body, fontSize=8, leading=10))
        ])
    threat_tbl = Table(threat_rows, colWidths=[40*mm, 22*mm, 108*mm])
    threat_style = [
        ("BACKGROUND", (0,0), (-1,0), DARK_TEAL),
        ("TEXTCOLOR", (0,0), (-1,0), HexColor("#ffffff")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("GRID", (0,0), (-1,-1), 0.4, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [HexColor("#ffffff"), LIGHT_GREY]),
    ]
    # Colour the level cells
    for i, (key, label) in enumerate(threat_labels.items(), start=1):
        lvl = threats.get(key, {}).get("level", "")
        c = RISK_COLORS.get(lvl)
        if c:
            threat_style.append(("TEXTCOLOR", (1,i), (1,i), c))
    threat_tbl.setStyle(TableStyle(threat_style))
    story.append(threat_tbl)
    story.append(Spacer(1, 8))

    # ── CHOKEPOINTS ──
    chokepoints = vra.get("chokepoints", [])
    if chokepoints:
        story.append(Paragraph("CHOKEPOINT ADVISORIES", h2))
        for cp in chokepoints:
            cp_text = f"<b>{cp.get('name','')}</b> &nbsp;<font color='#d63a2f'>[{cp.get('risk','')}]</font> — {cp.get('advisory','')}"
            story.append(Paragraph(cp_text, ParagraphStyle("cp", parent=body, fontSize=8.5, leading=12, spaceAfter=3)))
        story.append(Spacer(1, 6))

    # ── RECOMMENDATIONS ──
    story.append(Paragraph("OPERATIONAL RECOMMENDATIONS", h2))
    for rec in vra.get("recommendations", []):
        story.append(Paragraph(f"▸ {rec}", ParagraphStyle("rec", parent=body, fontSize=9, leading=13, leftIndent=6, spaceAfter=2)))
    story.append(Spacer(1, 6))

    # ── HARDENING + REPORTING (two columns) ──
    hardening = vra.get("hardening_measures", [])
    reporting = vra.get("reporting_requirements", [])
    if hardening or reporting:
        h_text = "<b>SHIP HARDENING (BMP5)</b><br/>" + "<br/>".join([f"• {h}" for h in hardening])
        r_text = "<b>REPORTING REQUIREMENTS</b><br/>" + "<br/>".join([f"• {r}" for r in reporting])
        cols_tbl = Table([[
            Paragraph(h_text, ParagraphStyle("h", parent=body, fontSize=8, leading=11, textColor=DARK_TEAL)),
            Paragraph(r_text, ParagraphStyle("r", parent=body, fontSize=8, leading=11, textColor=DARK_TEAL)),
        ]], colWidths=[85*mm, 85*mm])
        cols_tbl.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("BOX", (0,0), (-1,-1), 0.5, HexColor("#cccccc")),
            ("LINEAFTER", (0,0), (0,0), 0.5, HexColor("#cccccc")),
        ]))
        story.append(cols_tbl)
        story.append(Spacer(1, 8))

    # ── INSURANCE NOTE ──
    ins = vra.get("insurance_note", "")
    if ins:
        story.append(Paragraph("WAR RISK / INSURANCE", h2))
        story.append(Paragraph(ins, ParagraphStyle("ins", parent=body, fontSize=8.5, leading=12)))
        story.append(Spacer(1, 6))

    # ── ANALYST NOTE ──
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD))
    story.append(Spacer(1, 4))
    note = vra.get("analyst_note", "")
    story.append(Paragraph(note, ParagraphStyle("note", parent=body, fontSize=8.5, leading=12, fontName="Helvetica-Oblique")))
    story.append(Spacer(1, 8))

    # ── SIGNATURE ──
    sig_data = [[
        Paragraph("<b>Capt. Ritesh Kapoor</b><br/><font size=7 color='#666666'>Director of Operations<br/>HR Maritime Consultants</font>",
                  ParagraphStyle("sig", parent=body, fontSize=9, leading=12, textColor=TEAL)),
        Paragraph(f"<font size=7 color='#666666'>Generated: {datetime.now().strftime('%d %b %Y %H:%M UTC')}<br/>Foresight Intelligence Platform<br/>Ref: FIP-VRA-{vra.get('imo','000')[-4:]}-{datetime.now().strftime('%m%d')}</font>",
                  ParagraphStyle("ref", parent=small, alignment=TA_LEFT))
    ]]
    sig_tbl = Table(sig_data, colWidths=[90*mm, 80*mm])
    sig_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
    ]))
    story.append(sig_tbl)

    # ── DISCLAIMER FOOTER ──
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cccccc")))
    disclaimer = ("This assessment is provided for the named vessel and voyage only, based on intelligence available at the time of issue. "
                  "Threat environments evolve rapidly; this VRA should be read in conjunction with live UKMTO/MSCHOA advisories. "
                  "© HR Maritime Consultants — Foresight Intelligence Platform. Confidential.")
    story.append(Paragraph(disclaimer, ParagraphStyle("disc", parent=small, fontSize=6.5, leading=8, textColor=HexColor("#999999"))))

    doc.build(story)
    return output_path
