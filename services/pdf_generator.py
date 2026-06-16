from fpdf import FPDF

def generate_simple_report(filename: str, report_title: str, content_lines: list[str]) -> str:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, report_title, ln=True, align="C")

    # Відступ
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)

    for line in content_lines:
        pdf.cell(0, 10, line, ln=True)

    filepath = f"./{filename}"
    pdf.output(filepath)

    return filepath
