"""Универсальный конвертер Markdown -> PDF (кириллица, таблицы, заголовки).

Запуск (обязательно через .venv, где есть reportlab):
    ./.venv/Scripts/python.exe tools/md_to_pdf.py research/category_verification.md output/pdf/category-verification.pdf
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table,
    TableStyle,
)


def font_paths():
    for regular, bold in [
        (Path("C:/Windows/Fonts/DejaVuSans.ttf"), Path("C:/Windows/Fonts/DejaVuSans-Bold.ttf")),
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]:
        if regular.exists() and bold.exists():
            return regular, bold
    raise RuntimeError("Unicode-шрифт с кириллицей не найден.")


def strip_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.S)
    text = re.sub(r"__(.+?)__", r"\1", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"(?m)^\s*[-*]\s+", "• ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    return text


def para(value, style, bold=False):
    content = html.escape(str(value)).replace("\n", "<br/>")
    content = re.sub(r"&lt;br/&gt;", "<br/>", content)
    return Paragraph(content, style)


def split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s:|-]+\|?\s*$", line)) and "-" in line


def build(md_path: Path, out_path: Path, title: str) -> None:
    regular, bold = font_paths()
    pdfmetrics.registerFont(TTFont("DSSSans", str(regular)))
    pdfmetrics.registerFont(TTFont("DSSSans-Bold", str(bold)))

    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="DSSSans",
                          fontSize=8.8, leading=12.4, textColor=colors.HexColor("#23313b"),
                          spaceAfter=5, alignment=TA_LEFT)
    small = ParagraphStyle("Small", parent=body, fontSize=7.0, leading=9.0, spaceAfter=0)
    h1 = ParagraphStyle("H1", parent=body, fontName="DSSSans-Bold", fontSize=15,
                        leading=19, textColor=colors.HexColor("#0d4f6d"),
                        spaceBefore=12, spaceAfter=8, keepWithNext=True)
    h2 = ParagraphStyle("H2", parent=body, fontName="DSSSans-Bold", fontSize=11.5,
                        leading=15, textColor=colors.HexColor("#245d74"),
                        spaceBefore=9, spaceAfter=6, keepWithNext=True)
    h3 = ParagraphStyle("H3", parent=body, fontName="DSSSans-Bold", fontSize=9.6,
                        leading=12.5, textColor=colors.HexColor("#3a6b7d"),
                        spaceBefore=7, spaceAfter=4, keepWithNext=True)
    th = ParagraphStyle("TH", parent=small, fontName="DSSSans-Bold", textColor=colors.white)
    note = ParagraphStyle("Note", parent=body, fontSize=8.2, leading=11,
                          textColor=colors.HexColor("#4c5962"), backColor=colors.HexColor("#edf5f7"),
                          borderColor=colors.HexColor("#b6d4dd"), borderWidth=0.5,
                          borderPadding=6, spaceBefore=4, spaceAfter=7)
    title_style = ParagraphStyle("Title", parent=body, fontName="DSSSans-Bold",
                                 fontSize=21, leading=26, textColor=colors.HexColor("#102b3c"),
                                 spaceAfter=10)

    def header_footer(canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(colors.HexColor("#d3e2e7"))
        canvas.line(18 * mm, h - 14 * mm, w - 18 * mm, h - 14 * mm)
        canvas.setFont("DSSSans", 7)
        canvas.setFillColor(colors.HexColor("#60727b"))
        canvas.drawString(18 * mm, h - 10 * mm, "Game Development DSS — верификация Категорий 1 и 2")
        canvas.drawRightString(w - 18 * mm, 9 * mm, str(doc.page))
        canvas.restoreState()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(out_path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=21 * mm, bottomMargin=16 * mm, title=title, author="Game Development DSS")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header_footer)])

    lines = md_path.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        # table
        if s.startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]):
            headers = split_row(s)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            ncol = len(headers)
            data = [[para(h, th) for h in headers]]
            for r in rows:
                r = (r + [""] * ncol)[:ncol]
                data.append([para(strip_md(c), small) for c in r])
            avail = doc.width
            if ncol >= 6:
                widths = [avail / ncol] * ncol
            else:
                widths = [avail / ncol] * ncol
            t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d4f6d")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd9de")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f7f8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]))
            story.append(t)
            story.append(Spacer(1, 4 * mm))
            continue
        if s.startswith("```"):
            i += 1
            continue
        if s.startswith("### "):
            story.append(para(strip_md(s[4:]), h3))
        elif s.startswith("## "):
            story.append(para(strip_md(s[3:]), h2))
        elif s.startswith("# "):
            story.append(para(strip_md(s[2:]), h1))
        elif s.startswith("> "):
            story.append(para(strip_md(s[2:]), note))
        elif s.startswith("---"):
            story.append(Spacer(1, 3 * mm))
        elif re.match(r"^\s*[-*]\s+", line):
            story.append(para("• " + strip_md(re.sub(r"^\s*[-*]\s+", "", line)), body))
        elif re.match(r"^\s*\d+\.\s+", line):
            story.append(para(strip_md(s), body))
        else:
            story.append(para(strip_md(s), body))
        i += 1

    # Титул
    front = [Spacer(1, 30 * mm), para(title, title_style),
             para("Сводное исследование по чек-листу CATEGORY_VERIFICATION_PLAN.md", body),
             Spacer(1, 3 * mm), PageBreak()]
    doc.build(front + story)
    print("PDF ->", out_path.resolve())


if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    build(src, dst, "Верификация Категорий 1 и 2 — Game Development DSS")
