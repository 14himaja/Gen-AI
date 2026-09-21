import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle

def generate_pdf():
    txt_path = Path("docs/ApolloCare_Hospital_Policies_Schemes_Guidelines.txt")
    if not txt_path.exists():
        print("Error: Source txt file not found!")
        return

    # Also save a copy as docs/apollocare.txt if not exists
    apollocare_txt = Path("docs/apollocare.txt")
    apollocare_txt.write_text(txt_path.read_text(encoding="utf-8"), encoding="utf-8")

    pdf_path_1 = Path("docs/ApolloCare_Hospital_Policies_Schemes_Guidelines.pdf")
    pdf_path_2 = Path("docs/apollocare.pdf")

    for pdf_out in [pdf_path_1, pdf_path_2]:
        doc = SimpleDocTemplate(
            str(pdf_out),
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=HexColor('#0d9488'),
            alignment=1, # Center
            spaceAfter=12
        )

        meta_style = ParagraphStyle(
            'DocMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=HexColor('#57534e'),
            alignment=1,
            spaceAfter=14
        )

        h1_style = ParagraphStyle(
            'SectionH1',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=HexColor('#0f766e'),
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )

        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14,
            textColor=HexColor('#1c1917'),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=HexColor('#292524'),
            spaceAfter=4
        )

        bullet_style = ParagraphStyle(
            'BulletText',
            parent=body_style,
            leftIndent=15,
            spaceAfter=3
        )

        story = []

        # Title block
        story.append(Paragraph("APOLLOCARE SMART HOSPITAL", title_style))
        story.append(Paragraph("<b>Master Hospital Policies, Government Schemes & Patient Guidelines</b><br/>Version 3.2 (2026 Edition) • Effective Date: January 1, 2026", meta_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor('#0d9488'), spaceBefore=2, spaceAfter=12))

        lines = txt_path.read_text(encoding="utf-8").splitlines()

        in_header_banner = True
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith('==='):
                continue
            if 'APOLLOCARE SMART HOSPITAL' in line_str or 'Document ID:' in line_str or 'Approved By:' in line_str or 'Effective Date:' in line_str:
                continue

            if line_str.startswith('SECTION '):
                story.append(Spacer(1, 8))
                story.append(HRFlowable(width="100%", thickness=0.8, color=HexColor('#cbd5e1'), spaceBefore=4, spaceAfter=6))
                story.append(Paragraph(line_str, h1_style))
                story.append(Spacer(1, 4))
            elif line_str.startswith('1.') or line_str.startswith('2.') or line_str.startswith('3.') or line_str.startswith('4.') or line_str.startswith('5.') or line_str.startswith('6.'):
                story.append(Paragraph(line_str, h2_style))
            elif line_str.startswith('-') or line_str.startswith('•'):
                text = line_str.lstrip('-• ').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f"• {text}", bullet_style))
            elif line_str[0:2].isdigit() and line_str[2] == '.':
                text = line_str.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(text, bullet_style))
            else:
                text = line_str.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(text, body_style))

        doc.build(story)
        print(f"Generated PDF: {pdf_out}")

if __name__ == "__main__":
    generate_pdf()
