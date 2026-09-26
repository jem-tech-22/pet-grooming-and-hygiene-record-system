from datetime import datetime
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle


def export_report_pdf(file_path, report_type, headers, rows, filters=None):
	"""Write the supplied report preview data to a paginated PDF file."""
	page_size = landscape(A4)
	document = SimpleDocTemplate(
		str(file_path),
		pagesize=page_size,
		leftMargin=15 * mm,
		rightMargin=15 * mm,
		topMargin=16 * mm,
		bottomMargin=16 * mm
	)
	styles = getSampleStyleSheet()
	title_style = ParagraphStyle(
		"FurLogTitle", parent=styles["Title"], fontName="Helvetica-Bold",
		fontSize=20, leading=24, textColor=colors.HexColor("#173B2F"),
		alignment=TA_LEFT, spaceAfter=4
	)
	section_style = ParagraphStyle(
		"FurLogSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
		fontSize=13, leading=17, textColor=colors.HexColor("#2F8F63"),
		spaceBefore=4, spaceAfter=6
	)
	meta_style = ParagraphStyle(
		"FurLogMeta", parent=styles["Normal"], fontName="Helvetica",
		fontSize=9, leading=13, textColor=colors.HexColor("#425149"),
		spaceAfter=3
	)
	header_style = ParagraphStyle(
		"FurLogTableHeader", parent=styles["Normal"], fontName="Helvetica-Bold",
		fontSize=8, leading=10, textColor=colors.white
	)
	cell_style = ParagraphStyle(
		"FurLogTableCell", parent=styles["Normal"], fontName="Helvetica",
		fontSize=8, leading=10, textColor=colors.HexColor("#17231E")
	)

	def paragraph_text(value, style):
		text = escape(str(value)).replace("\r\n", "\n").replace("\n", "<br/>")
		return Paragraph(text or "-", style)

	story = [
		Paragraph("FurLog Report", title_style),
		Paragraph(escape(report_type), section_style),
		Paragraph(
			f"Date generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
			meta_style
		),
	]
	for label, value in (filters or {}).items():
		story.append(Paragraph(
			f"<b>{escape(str(label))}:</b> {escape(str(value))}", meta_style
		))
	story.append(Spacer(1, 5 * mm))

	if headers:
		table_data = [[paragraph_text(header, header_style) for header in headers]]
		table_data.extend([
			[paragraph_text(value, cell_style) for value in row]
			for row in rows
		])
		available_width = page_size[0] - document.leftMargin - document.rightMargin
		wide_columns = {"notes", "vitamins", "foods", "needs"}
		weights = [2.3 if header.lower() in wide_columns else 1.0 for header in headers]
		weight_total = sum(weights)
		column_widths = [available_width * weight / weight_total for weight in weights]
		table = LongTable(
			table_data,
			colWidths=column_widths,
			repeatRows=1,
			splitByRow=1,
			splitInRow=1,
			hAlign="LEFT"
		)
		table.setStyle(TableStyle([
			("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B2F")),
			("ROWBACKGROUNDS", (0, 1), (-1, -1), (
				colors.white, colors.HexColor("#F4F7F4")
			)),
			("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDE6E0")),
			("VALIGN", (0, 0), (-1, -1), "TOP"),
			("LEFTPADDING", (0, 0), (-1, -1), 6),
			("RIGHTPADDING", (0, 0), (-1, -1), 6),
			("TOPPADDING", (0, 0), (-1, -1), 6),
			("BOTTOMPADDING", (0, 0), (-1, -1), 6)
		]))
		story.append(table)
	else:
		story.append(Paragraph("No report columns are available.", meta_style))
	story.extend((
		Spacer(1, 5 * mm),
		Paragraph(f"<b>Total records:</b> {len(rows)}", meta_style)
	))

	def draw_page_number(canvas, doc):
		canvas.saveState()
		canvas.setFont("Helvetica", 8)
		canvas.setFillColor(colors.HexColor("#718079"))
		canvas.drawRightString(page_size[0] - document.rightMargin, 8 * mm, str(doc.page))
		canvas.restoreState()

	document.build(story, onFirstPage=draw_page_number, onLaterPages=draw_page_number)