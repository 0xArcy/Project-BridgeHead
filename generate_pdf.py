from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents


WORKSPACE = Path(__file__).resolve().parent
SOURCE = WORKSPACE / "PROJECT_CYBORGS_POST_INCIDENT_ARCHITECTURAL_DEFENSE_REPORT.md"
OUTPUT = WORKSPACE / "PROJECT_BRIDGEHEAD_POST_INCIDENT_ARCHITECTURAL_DEFENSE_REPORT.pdf"

IMAGE_RE = re.compile(r"!\[(?P<alt>.*?)\]\((?P<path>.*?)\)")
NUMBER_RE = re.compile(r"^(?P<num>\d+)\.\s+(?P<text>.+)$")
LINK_RE = re.compile(r"\[(?P<label>.*?)\]\((?P<path>.*?)\)")
TABLE_CAPTION_RE = re.compile(r"^Table\s+\d+:\s+.+$")

NAVY = colors.HexColor("#102a43")
SLATE = colors.HexColor("#334e68")
MUTED = colors.HexColor("#5b7083")
LINE = colors.HexColor("#d9e2ec")
ROW_ALT = colors.HexColor("#f8fafc")
HEADER_FILL = colors.HexColor("#e9eff5")
ACCENT = colors.HexColor("#b08968")


class ReportDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return

        style_name = flowable.style.name
        level_map = {
            "SectionHeading": 0,
            "SubHeading": 1,
            "MinorHeading": 2,
        }
        if style_name not in level_map:
            return

        text = flowable.getPlainText()
        level = level_map[style_name]
        self.notify("TOCEntry", (level, text, self.page))


def parse_args():
    parser = argparse.ArgumentParser(description="Render a markdown report into a styled PDF.")
    parser.add_argument("--source", default=str(SOURCE), help="Path to the markdown source file")
    parser.add_argument("--output", default=str(OUTPUT), help="Path to the PDF output file")
    parser.add_argument("--title", default="Project Bridgehead", help="Cover title")
    parser.add_argument("--subtitle", default="Post-Incident and Architectural Defense Report", help="Cover subtitle")
    parser.add_argument(
        "--summary",
        default="Comprehensive technical report consolidating infrastructure design, exploitation evidence, blue-team telemetry, defensive controls, and post-incident remediation across the current Project Bridgehead workspace evidence set.",
        help="Cover summary text",
    )
    parser.add_argument(
        "--cover-note",
        default="",
        help="Short note shown under the title on the cover page",
    )
    parser.add_argument("--classification", default="", help="Document classification label")
    parser.add_argument("--document-date", default="2026-04-17", help="Date shown on the cover page")
    parser.add_argument(
        "--audience",
        default="Executive Leadership, Technical Reviewers, and Internal Security Stakeholders",
        help="Audience text shown on the cover page",
    )
    parser.add_argument(
        "--prepared-by",
        default="Team Cyborg",
        help="Author or team name shown on the cover page",
    )
    parser.add_argument(
        "--student-number",
        default="",
        help="Secondary author line shown under the prepared-by field on the cover page",
    )
    parser.add_argument(
        "--skip-cover",
        action="store_true",
        help="Skip the generated cover page and start with the document body",
    )
    parser.add_argument(
        "--skip-toc",
        action="store_true",
        help="Skip the generated table of contents page",
    )
    parser.add_argument(
        "--skip-section-pagebreaks",
        action="store_true",
        help="Do not force page breaks before major numbered sections",
    )
    parser.add_argument(
        "--footer-label",
        default="Project Bridgehead Technical Report",
        help="Footer label shown on each page",
    )
    parser.add_argument(
        "--repo-url",
        default="https://github.com/0xArcy/Project-BridgeHead",
        help="GitHub repository URL shown on the cover and TOC pages",
    )
    return parser.parse_args()


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=30,
            alignment=TA_CENTER,
            spaceAfter=16,
            textColor=NAVY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=32,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.white,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11.5,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#e6edf3"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=SLATE,
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MinorHeading",
            parent=styles["Heading4"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=SLATE,
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TocHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TocItem",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            leftIndent=8,
            alignment=TA_LEFT,
            spaceAfter=4,
            textColor=SLATE,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TocItemLevel3",
            parent=styles["TocItem"],
            leftIndent=18,
            fontSize=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TocItemLevel4",
            parent=styles["TocItem"],
            leftIndent=30,
            fontSize=9.5,
            textColor=MUTED,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RepoLink",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            alignment=TA_CENTER,
            textColor=SLATE,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14.5,
            leading=19,
            spaceBefore=14,
            spaceAfter=8,
            textColor=NAVY,
            borderWidth=0,
            borderPadding=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtleLead",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14.5,
            alignment=TA_JUSTIFY,
            textColor=SLATE,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14.5,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            textColor=colors.HexColor("#1f2933"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyItalic",
            parent=styles["Body"],
            fontName="Helvetica-Oblique",
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletItem",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14.5,
            leftIndent=18,
            firstLineIndent=0,
            spaceAfter=5,
            textColor=colors.HexColor("#1f2933"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletItalic",
            parent=styles["BulletItem"],
            fontName="Helvetica-Oblique",
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=0,
            textColor=colors.HexColor("#1f2933"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeaderCell",
            parent=styles["TableCell"],
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            textColor=NAVY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            parent=styles["BodyText"],
            fontName="Courier",
            fontSize=9.3,
            leading=12,
            leftIndent=16,
            rightIndent=16,
            spaceBefore=4,
            spaceAfter=8,
            textColor=colors.HexColor("#243b53"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlockItalic",
            parent=styles["CodeBlock"],
            fontName="Courier-Oblique",
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=11,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Callout",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14.5,
            textColor=NAVY,
            spaceAfter=0,
        )
    )
    return styles


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, doc.pagesize[1] - 32, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 32)
    canvas.line(doc.leftMargin, 28, doc.pagesize[0] - doc.rightMargin, 28)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 16, doc.footer_label)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.black)
    canvas.drawRightString(doc.pagesize[0] - 36, 20, str(canvas.getPageNumber()))
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, doc.pagesize[1] - 220, doc.pagesize[0], 220, stroke=0, fill=1)
    canvas.setFillColor(ACCENT)
    accent_width = 210
    accent_x = (doc.pagesize[0] - accent_width) / 2.0
    canvas.rect(accent_x, doc.pagesize[1] - 78, accent_width, 6, stroke=0, fill=1)
    canvas.restoreState()


def flush_paragraph(story, buffer, styles, style_name="Body"):
    if not buffer:
        return
    text = " ".join(part.strip() for part in buffer if part.strip())
    if text:
        story.append(Paragraph(normalize_inline_markdown(text), styles[style_name]))
    buffer.clear()


def escape_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def normalize_inline_markdown(text: str) -> str:
    text = LINK_RE.sub(lambda match: match.group("label"), text)
    text = escape_text(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = text.replace("`", "")
    return text


def format_external_link(label: str, url: str) -> str:
    return f'<link href="{escape_text(url)}" color="{SLATE.hexval()}">{escape_text(label)}</link>'


def split_intro_and_body(lines: list[str]) -> tuple[list[str], list[str]]:
    content_lines = list(lines)
    if content_lines and content_lines[0].strip().startswith("# "):
        content_lines = content_lines[1:]

    toc_index = None
    for index, line in enumerate(content_lines):
        if line.strip() == "## Table of Contents":
            toc_index = index
            break

    if toc_index is None:
        return [], content_lines

    intro_lines = content_lines[:toc_index]
    while intro_lines and not intro_lines[-1].strip():
        intro_lines.pop()
    if intro_lines and intro_lines[-1].strip() in {"---", "***"}:
        intro_lines.pop()
    while intro_lines and not intro_lines[-1].strip():
        intro_lines.pop()

    body_start = toc_index + 1
    while body_start < len(content_lines):
        stripped = content_lines[body_start].strip()
        if stripped.startswith("## ") and stripped != "## Table of Contents":
            break
        body_start += 1

    return intro_lines, content_lines[body_start:]


def extract_preface_sections(lines: list[str], section_titles: list[str]) -> tuple[list[list[str]], list[str]]:
    sections: list[list[str]] = []
    remaining: list[str] = []
    index = 0
    wanted = set(section_titles)

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("## ") and stripped[3:].strip() in wanted:
            current: list[str] = [lines[index]]
            index += 1
            while index < len(lines):
                next_stripped = lines[index].strip()
                if next_stripped.startswith("## "):
                    break
                current.append(lines[index])
                index += 1
            sections.append(current)
            continue

        remaining.append(lines[index])
        index += 1

    return sections, remaining


def is_table_line(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def parse_table_row(text: str) -> list[str]:
    return [cell.strip() for cell in text.strip()[1:-1].split("|")]


def is_separator_row(text: str) -> bool:
    cells = parse_table_row(text)
    return all(cell and set(cell) <= {"-", ":", " "} for cell in cells)


def add_markdown_table(story, table_lines: list[str], styles, doc_width: float):
    rows = [parse_table_row(line) for line in table_lines if not is_separator_row(line)]
    if not rows:
        return

    col_count = max(len(row) for row in rows)
    rows = [row + [""] * (col_count - len(row)) for row in rows]
    header_cells = [cell.strip().lower() for cell in rows[0]] if rows else []
    is_table_index_list = col_count == 3 and header_cells == ["table", "title", "location"]
    is_figure_index_list = col_count == 3 and header_cells == ["figure", "title", "location"]

    wrapped = []
    for row_index, row in enumerate(rows):
        style_name = "TableCell"
        if row_index == 0:
            style_name = "TableHeaderCell"
        wrapped_row = []
        for cell_index, cell in enumerate(row):
            cell_text = normalize_inline_markdown(cell)
            if row_index > 0 and cell_index == 0 and (is_table_index_list or is_figure_index_list):
                cell_text = cell_text.replace(" ", "&nbsp;")
            wrapped_row.append(Paragraph(cell_text, styles[style_name]))
        wrapped.append(wrapped_row)

    if is_table_index_list:
        col_widths = [doc_width * 0.11, doc_width * 0.76, doc_width * 0.13]
    elif is_figure_index_list:
        col_widths = [doc_width * 0.13, doc_width * 0.74, doc_width * 0.13]
    else:
        col_width = doc_width / col_count
        col_widths = [col_width] * col_count

    table = Table(wrapped, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_FILL),
                ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.14 * inch))


def add_callout(story, text: str, styles, doc_width: float):
    box = Table(
        [[Paragraph(normalize_inline_markdown(text), styles["Callout"])]],
        colWidths=[doc_width],
        hAlign="LEFT",
    )
    box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.55, LINE),
                ("LINEBEFORE", (0, 0), (0, -1), 4, ACCENT),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(box)
    story.append(Spacer(1, 0.12 * inch))


def add_image(story, image_path: Path, caption: str, doc_width: float, max_height: float, styles):
    if not image_path.exists():
        story.append(Paragraph(f"Missing image: {escape_text(str(image_path))}", styles["Caption"]))
        return

    with PILImage.open(image_path) as img:
        width_px, height_px = img.size

    width = float(width_px)
    height = float(height_px)

    width_scale = doc_width / width
    height_scale = max_height / height
    scale = min(width_scale, height_scale, 1.0)

    reportlab_image = Image(str(image_path), width=width * scale, height=height * scale)
    reportlab_image.hAlign = "CENTER"

    elements = [reportlab_image]
    if caption:
        elements.append(Paragraph(escape_text(caption), styles["Caption"]))
    else:
        elements.append(Spacer(1, 8))
    story.append(KeepTogether(elements))


def build_story(args):
    styles = build_styles()
    doc = ReportDocTemplate(
        str(Path(args.output)),
        pagesize=A4,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=args.title,
        author="GitHub Copilot",
    )
    doc.footer_label = args.footer_label
    doc.classification = args.classification

    story = []
    paragraph_buffer: list[str] = []
    lines = Path(args.source).read_text(encoding="utf-8").splitlines()
    intro_lines, body_lines = split_intro_and_body(lines)
    preface_sections, body_lines = extract_preface_sections(body_lines, ["List of Tables", "List of Figures"])

    if not args.skip_cover:
        story.append(Spacer(1, 0.7 * inch))
        story.append(Paragraph(escape_text(args.title), styles["CoverTitle"]))
        story.append(Paragraph(escape_text(args.subtitle), styles["CoverSubtitle"]))
        if args.cover_note:
            story.append(Paragraph(escape_text(args.cover_note), styles["CoverSubtitle"]))
        story.append(Spacer(1, 1.0 * inch))
        meta_cells = [
            Paragraph(f"<b>Document Date</b><br/>{escape_text(args.document_date)}", styles["CoverMeta"]),
            Paragraph(f"<b>Audience</b><br/>{escape_text(args.audience)}", styles["CoverMeta"]),
        ]
        if args.prepared_by:
            prepared_by_text = f"<b>Prepared By</b><br/>{escape_text(args.prepared_by)}"
            if args.student_number:
                prepared_by_text += f"<br/>{args.student_number}"
            meta_cells.append(Paragraph(prepared_by_text, styles["CoverMeta"]))

        meta_table = Table(
            [meta_cells],
            colWidths=[doc.width / float(len(meta_cells))] * len(meta_cells),
            hAlign="CENTER",
        )
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(meta_table)
        story.append(Spacer(1, 0.3 * inch))
        cover_box = Table(
            [[Paragraph(escape_text(args.summary), styles["SubtleLead"])]],
            colWidths=[doc.width * 0.86],
            hAlign="CENTER",
        )
        cover_box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                    ("LINEBEFORE", (0, 0), (0, -1), 4, ACCENT),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(cover_box)
        story.append(Spacer(1, 0.18 * inch))
        story.append(
            Paragraph(
                f"<b>GitHub Repository</b><br/>{format_external_link(args.repo_url, args.repo_url)}",
                styles["RepoLink"],
            )
        )
        story.append(PageBreak())

    if not args.skip_toc:
        story.append(Paragraph("Table of Contents", styles["TocHeading"]))
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                name="WordLikeToc1",
                parent=styles["TocItem"],
                fontName="Helvetica",
                fontSize=10.5,
                leading=12.5,
                leftIndent=0,
                firstLineIndent=0,
                spaceBefore=0,
                spaceAfter=2,
            ),
            ParagraphStyle(
                name="WordLikeToc2",
                parent=styles["TocItemLevel3"],
                fontName="Helvetica",
                fontSize=10,
                leading=12,
                leftIndent=32,
                firstLineIndent=0,
                spaceBefore=0,
                spaceAfter=1,
            ),
            ParagraphStyle(
                name="WordLikeToc3",
                parent=styles["TocItemLevel4"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=11.5,
                leftIndent=46,
                firstLineIndent=0,
                spaceBefore=0,
                spaceAfter=1,
            ),
        ]
        toc.dotsMinLevel = 0
        story.append(toc)
        story.append(PageBreak())

    if preface_sections:
        for section in preface_sections:
            active_preface = list(section)
            preface_index = 0
            while preface_index < len(active_preface):
                line = active_preface[preface_index].rstrip()
                stripped = line.strip()

                if not stripped:
                    preface_index += 1
                    continue

                if stripped.startswith("## "):
                    story.append(Paragraph(normalize_inline_markdown(stripped[3:].strip()), styles["SectionHeading"]))
                    story.append(HRFlowable(width="100%", thickness=0.7, color=LINE, hAlign="CENTER"))
                    story.append(Spacer(1, 0.08 * inch))
                    preface_index += 1
                    continue

                if TABLE_CAPTION_RE.match(stripped):
                    story.append(Paragraph(escape_text(stripped), styles["Caption"]))
                    preface_index += 1
                    continue

                if is_table_line(stripped):
                    table_lines = []
                    while preface_index < len(active_preface) and is_table_line(active_preface[preface_index].strip()):
                        table_lines.append(active_preface[preface_index].strip())
                        preface_index += 1
                    add_markdown_table(story, table_lines, styles, doc.width)
                    continue

                story.append(Paragraph(normalize_inline_markdown(stripped), styles["Body"]))
                preface_index += 1

            story.append(PageBreak())

    if intro_lines:
        story.append(Paragraph("Introduction", styles["SectionHeading"]))
        story.append(HRFlowable(width="100%", thickness=0.7, color=LINE, hAlign="CENTER"))
        story.append(Spacer(1, 0.08 * inch))

    index = 0
    in_note_section = False
    active_lines = intro_lines + ([""] if intro_lines else []) + body_lines
    while index < len(active_lines):
        line = active_lines[index].rstrip()
        stripped = line.strip()
        paragraph_style = "BodyItalic" if in_note_section else "Body"
        bullet_style = "BulletItalic" if in_note_section else "BulletItem"
        code_style = "CodeBlockItalic" if in_note_section else "CodeBlock"

        if not stripped:
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            index += 1
            continue

        if is_table_line(stripped):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            table_lines = []
            while index < len(active_lines) and is_table_line(active_lines[index].strip()):
                table_lines.append(active_lines[index].strip())
                index += 1
            add_markdown_table(story, table_lines, styles, doc.width)
            continue

        if TABLE_CAPTION_RE.match(stripped):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            story.append(Paragraph(escape_text(stripped), styles["Caption"]))
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            index += 1
            code_lines = []
            while index < len(active_lines) and not active_lines[index].strip().startswith("```"):
                code_lines.append(active_lines[index].rstrip())
                index += 1
            if index < len(active_lines) and active_lines[index].strip().startswith("```"):
                index += 1
            code_text = "<br/>".join(escape_text(code_line) for code_line in code_lines)
            story.append(Paragraph(code_text, styles[code_style]))
            continue

        image_match = IMAGE_RE.match(stripped)
        if image_match:
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            image_path = WORKSPACE / unquote(image_match.group("path"))
            caption = image_match.group("alt")
            add_image(story, image_path, caption, doc.width, doc.height * 0.55, styles)
            index += 1
            continue

        if stripped.startswith("# "):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            in_note_section = False
            index += 1
            continue

        if stripped.startswith("## "):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            in_note_section = False
            heading = stripped[3:].strip()
            if not args.skip_section_pagebreaks and heading.startswith(("2.1", "3.1", "4.1", "5.1", "References")):
                story.append(PageBreak())
            story.append(Paragraph(normalize_inline_markdown(heading), styles["SectionHeading"]))
            story.append(HRFlowable(width="100%", thickness=0.7, color=LINE, hAlign="CENTER"))
            story.append(Spacer(1, 0.08 * inch))
            index += 1
            continue

        if stripped.startswith("### "):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            subheading = stripped[4:].strip()
            in_note_section = subheading in {"Assessment Notes", "Operator Excerpts"}
            story.append(Paragraph(normalize_inline_markdown(subheading), styles["SubHeading"]))
            index += 1
            continue

        if stripped.startswith("#### "):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            minor_heading = stripped[5:].strip()
            story.append(Paragraph(normalize_inline_markdown(minor_heading), styles["MinorHeading"]))
            index += 1
            continue

        if stripped.startswith("> "):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            callout_lines = []
            while index < len(active_lines) and active_lines[index].strip().startswith("> "):
                callout_lines.append(active_lines[index].strip()[2:].strip())
                index += 1
            add_callout(story, " ".join(callout_lines), styles, doc.width)
            continue

        if stripped in {"---", "***"}:
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            story.append(HRFlowable(width="100%", thickness=0.7, color=LINE, hAlign="CENTER"))
            story.append(Spacer(1, 0.08 * inch))
            index += 1
            continue

        if stripped.startswith("- "):
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            story.append(Paragraph(f"• {normalize_inline_markdown(stripped[2:].strip())}", styles[bullet_style]))
            index += 1
            continue

        numbered = NUMBER_RE.match(stripped)
        if numbered:
            flush_paragraph(story, paragraph_buffer, styles, paragraph_style)
            story.append(
                Paragraph(
                    f"{numbered.group('num')}. {normalize_inline_markdown(numbered.group('text').strip())}",
                    styles[bullet_style],
                )
            )
            index += 1
            continue

        paragraph_buffer.append(stripped)
        index += 1

    flush_paragraph(story, paragraph_buffer, styles, "BodyItalic" if in_note_section else "Body")
    return doc, story


def main():
    args = parse_args()
    doc, story = build_story(args)
    first_page_callback = page_number if args.skip_cover else first_page
    doc.multiBuild(story, onFirstPage=first_page_callback, onLaterPages=page_number)
    print(f"Created PDF: {Path(args.output)}")


if __name__ == "__main__":
    main()