from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


PROJECT_DIR = Path(__file__).resolve().parent
SOURCE = PROJECT_DIR / "PROJECT_USER_AND_VIVA_GUIDE.md"
OUTPUT = PROJECT_DIR / "PROJECT_USER_AND_VIVA_GUIDE.pdf"


def md_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text.replace("&", "&amp;").replace("&lt;", "&lt;").replace("&gt;", "&gt;")


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#8B5CF6"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(18 * mm, 9 * mm, "ThinkFirst AI — Project User and Viva Guide")
    canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ProjectTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=26, leading=31,
        textColor=colors.HexColor("#312E81"), alignment=TA_CENTER,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11, leading=16,
        textColor=colors.HexColor("#475569"), alignment=TA_CENTER,
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading1"],
        fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=colors.HexColor("#312E81"),
        spaceBefore=16, spaceAfter=8,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="Subsection", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=13, leading=17,
        textColor=colors.HexColor("#4F46E5"),
        spaceBefore=12, spaceAfter=6,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="Minor", parent=styles["Heading3"],
        fontName="Helvetica-Bold", fontSize=11, leading=14,
        textColor=colors.HexColor("#6D28D9"),
        spaceBefore=8, spaceAfter=4,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="Body", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=9.5, leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="GuideBullet", parent=styles["Body"],
        leftIndent=16, firstLineIndent=-8,
        bulletIndent=6, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="Quote", parent=styles["Body"],
        leftIndent=14, rightIndent=14,
        borderColor=colors.HexColor("#8B5CF6"),
        borderWidth=2, borderPadding=8,
        backColor=colors.HexColor("#F5F3FF"),
        textColor=colors.HexColor("#4338CA"),
    ))
    styles.add(ParagraphStyle(
        name="GuideCode", parent=styles["Body"],
        fontName="Courier", fontSize=8.5, leading=12,
        leftIndent=10, rightIndent=10,
        backColor=colors.HexColor("#F1F5F9"),
        borderColor=colors.HexColor("#CBD5E1"),
        borderWidth=0.5, borderPadding=8,
    ))

    markdown = SOURCE.read_text(encoding="utf-8")
    story = []

    title_table = Table([["THINKFIRST AI"]], colWidths=[174 * mm], rowHeights=[24 * mm])
    title_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#312E81")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 20),
    ]))
    story.extend([
        Spacer(1, 22 * mm),
        title_table,
        Spacer(1, 10 * mm),
        Paragraph("Project User Guide, Demonstration Guide, and Viva Preparation", styles["ProjectTitle"]),
        Paragraph("Reasoning-Aware Adaptive Learning Platform", styles["Subtitle"]),
        PageBreak(),
    ])

    in_code = False
    code_lines = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code:
                if code_lines:
                    story.append(Paragraph("<br/>".join(md_inline(x) for x in code_lines), styles["GuideCode"]))
                    story.append(Spacer(1, 5))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line or " ")
            continue

        if not line:
            story.append(Spacer(1, 3))
            continue

        if line.startswith("---"):
            story.append(Spacer(1, 6))
            continue

        if line.startswith("### "):
            story.append(Paragraph(md_inline(line[4:].strip()), styles["Minor"]))
        elif line.startswith("## "):
            story.append(Paragraph(md_inline(line[3:].strip()), styles["Section"]))
        elif line.startswith("# "):
            continue
        elif line.startswith("> "):
            story.append(Paragraph(md_inline(line[2:].strip()), styles["Quote"]))
        elif re.match(r"^[-*] ", line):
            story.append(Paragraph("• " + md_inline(line[2:].strip()), styles["GuideBullet"]))
        elif re.match(r"^\d+\. ", line):
            number_text = re.sub(r"^(\d+)\. ", r"\1. ", line)
            story.append(Paragraph(md_inline(number_text), styles["GuideBullet"]))
        else:
            story.append(Paragraph(md_inline(line), styles["Body"]))

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title="ThinkFirst AI — Project User and Viva Guide",
        author="ThinkFirst AI",
        subject="Project guide, demonstration guide and viva preparation",
    )
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
