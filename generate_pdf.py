import yaml
from fpdf import FPDF

def create_invoice(yaml_path="invoice.yml", output_path="invoice.pdf"):
    # Load input parameters from YAML
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Business Header / Logo
    try:
        pdf.image("logo.png", x=10, y=8, w=50)
    except Exception:
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(0, 10, "OLWETHU CRAFTS AUTO", ln=True)

    # Business Contact Details (Top Right)
    pdf.set_font("Helvetica", size=9)
    pdf.set_xy(110, 10)
    pdf.multi_cell(0, 5, 
        "OLWETHU CRAFTS AUTO\n"
        "1 Apex Rd, Chloorkop, JHB\n"
        "Phone: 061 588 0157\n"
        "Email: info@olwethucrafts.co.za\n"
        "Email: osiyatula@gmail.com", align="R")

    pdf.ln(15)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Invoice & Client Details Section
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(100, 8, "INVOICE TO:", ln=False)
    pdf.cell(0, 8, f"INVOICE #: {data.get('invoice_number', 'N/A')}", ln=True, align="R")
    
    pdf.set_font("Helvetica", size=10)
    client = data.get("client", {})
    
    current_y = pdf.get_y()
    pdf.multi_cell(100, 5, 
        f"Name: {client.get('name', '')}\n"
        f"Address: {client.get('address', '')}\n"
        f"Phone: {client.get('telephone', '')}\n"
        f"Email: {client.get('email', '')}")
    
    pdf.set_xy(110, current_y)
    pdf.cell(0, 5, f"Date: {data.get('date', '')}", align="R")
    pdf.ln(20)

    # Table Header
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(90, 8, "Description", border=1, fill=True)
    pdf.cell(25, 8, "Qty", border=1, align="C", fill=True)
    pdf.cell(35, 8, "Unit Price (R)", border=1, align="R", fill=True)
    pdf.cell(40, 8, "Total (R)", border=1, align="R", fill=True)
    pdf.ln()

    # Table Body
    pdf.set_font("Helvetica", size=10)
    grand_total = 0.0
    for item in data.get("items", []):
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0.0)
        total = qty * price
        grand_total += total

        pdf.cell(90, 8, item.get("description", ""), border=1)
        pdf.cell(25, 8, str(qty), border=1, align="C")
        pdf.cell(35, 8, f"{price:.2f}", border=1, align="R")
        pdf.cell(40, 8, f"{total:.2f}", border=1, align="R")
        pdf.ln()

    # Total Row
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(150, 10, "Total Amount Due:", border=0, align="R")
    pdf.cell(40, 10, f"R {grand_total:.2f}", border=1, align="R")

    pdf.output(output_path)
    print(f"Invoice successfully generated: {output_path}")

if __name__ == "__main__":
    create_invoice()
