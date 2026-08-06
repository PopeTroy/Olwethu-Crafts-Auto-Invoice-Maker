import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from fpdf import FPDF

# ---------------------------------------------------------
# 9-TAIL (KURAMA): Telemetry & Performance Tracking
# ---------------------------------------------------------
start_time = time.time()
print("🔥 [Kurama] Unsealing Tailed Beast Invoice Pipeline...")

# Configuration & Secrets
api_key = os.getenv("NVCF_TARGET_SERVICE_KEY", "")
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key if api_key else "dummy_key"
)

# ---------------------------------------------------------
# 1-TAIL (SHUKAKU): Strict Input Sanitization
# ---------------------------------------------------------
def sanitize_input(val: str, default: str = "") -> str:
    cleaned = val.strip() if val else default
    return cleaned.replace("<", "").replace(">", "") # Strip dangerous HTML tags

invoice_number = sanitize_input(os.getenv("INVOICE_NUMBER"), "INV-2026-001")
date = sanitize_input(os.getenv("INVOICE_DATE"), "2026-08-06")
client_name = sanitize_input(os.getenv("CLIENT_NAME"), "Valued Client")
client_address = sanitize_input(os.getenv("CLIENT_ADDRESS"), "Sandton, Johannesburg")
client_telephone = sanitize_input(os.getenv("CLIENT_TELEPHONE"), "082 000 0000")
client_email = sanitize_input(os.getenv("CLIENT_EMAIL"), "client@example.com")

# ---------------------------------------------------------
# 4-TAIL (SON GOKŪ): High-Precision Math & Data Parsing
# ---------------------------------------------------------
parsed_items = []
for i in range(1, 11):
    val = os.getenv(f"ITEM_{i}", "").strip()
    if val:
        parts = [p.strip() for p in val.split(",")]
        if len(parts) >= 3:
            try:
                qty = int(parts[1])
            except ValueError:
                qty = 1
            try:
                price = float(parts[2])
            except ValueError:
                price = 0.0
            parsed_items.append({"description": parts[0], "quantity": qty, "unit_price": price})

if not parsed_items:
    parsed_items = [{"description": "General Auto Service", "quantity": 1, "unit_price": 0.0}]

# ---------------------------------------------------------
# 3-TAIL (ISOBU) + 6-TAIL (SAIKEN): Resilient Network & Model Fallback
# ---------------------------------------------------------
def fetch_logo():
    logo_url = "https://celsiustechmediagroup.co.za/wp-content/uploads/2026/08/IMG-20260801-WA0000.jpg"
    logo_path = "company_logo.jpg"
    try:
        req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as response, open(logo_path, 'wb') as out_file:
            out_file.write(response.read())
        return logo_path
    except Exception:
        return None

def call_nim_with_fallback(primary_model: str, fallback_model: str, prompt: str) -> str:
    """6-Tail Logic: Tries primary model, seamlessly fails over to backup model."""
    if not api_key or api_key == "dummy_key":
        return ""
    
    for model in [primary_model, fallback_model]:
        try:
            response = nvidia_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                timeout=3.0
            )
            return response.choices[0].message.content.strip()
        except Exception:
            continue # Fallback to next model
    return ""

# ---------------------------------------------------------
# 5-TAIL (KOKUŌ): Concurrent Parallel Processing
# ---------------------------------------------------------
logo_file = None
nim_results = {}

with ThreadPoolExecutor(max_workers=3) as executor:
    future_logo = executor.submit(fetch_logo)
    future_terms = executor.submit(
        call_nim_with_fallback, 
        "nvidia/nemotron-4-340b-instruct", 
        "mistralai/mistral-large-2-instruct", 
        "Generate 1 short payment term sentence for auto repair."
    )
    future_thanks = executor.submit(
        call_nim_with_fallback, 
        "mistralai/mistral-large-2-instruct", 
        "meta/llama-3.1-70b-instruct", 
        f"Write a 1-sentence thank you to {client_name}."
    )

    logo_file = future_logo.result()
    nim_results["terms"] = future_terms.result()
    nim_results["thanks"] = future_thanks.result()

# ---------------------------------------------------------
# 8-TAIL (GYŪKI): Dynamic PDF Layout & Styling Engine
# ---------------------------------------------------------
class BeastInvoicePDF(FPDF):
    def footer(self):
        self.set_y(-22)
        self.set_font("Helvetica", size=8)
        self.set_text_color(120, 120, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        footer_text = (
            "Olwethu Crafts Auto | 1 Apex Rd, Chloorkop, JHB | "
            "Tel: 061 588 0157 | Email: info@olwethucrafts.co.za\n"
            "Thank you for your business. Standard service warranty applies to all work completed."
        )
        self.multi_cell(0, 4, footer_text, align="C")

pdf = BeastInvoicePDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=25)

# Render Logo if present
if logo_file and os.path.exists(logo_file):
    try:
        pdf.image(logo_file, x=10, y=8, w=42)
    except Exception:
        pass

# Header Section
pdf.set_font("Helvetica", style="B", size=14)
pdf.set_xy(110, 10)
pdf.multi_cell(0, 5, "OLWETHU CRAFTS AUTO", align="R")

pdf.set_font("Helvetica", size=9)
pdf.set_xy(110, 17)
pdf.multi_cell(0, 4, 
    "1 Apex Rd, Chloorkop, JHB\n"
    "Tel: 061 588 0157\n"
    "Email: info@olwethucrafts.co.za\n"
    "Email: osiyatula@gmail.com", align="R")

pdf.ln(15)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(8)

# Client Details
pdf.set_font("Helvetica", style="B", size=10)
pdf.cell(100, 6, "INVOICE TO:", ln=False)
pdf.cell(0, 6, f"INVOICE NO: {invoice_number}", ln=True, align="R")

pdf.set_font("Helvetica", size=9)
start_y = pdf.get_y()

client_info = (
    f"Client Name: {client_name}\n"
    f"Address: {client_address}\n"
    f"Tel: {client_telephone}\n"
    f"Email: {client_email}"
)
pdf.multi_cell(100, 5, client_info)

pdf.set_xy(110, start_y)
pdf.cell(0, 5, f"Date: {date}", align="R")
pdf.ln(20)

# Table Header
pdf.set_font("Helvetica", style="B", size=9)
pdf.set_fill_color(230, 235, 240)
pdf.cell(90, 8, "Description", border=1, fill=True)
pdf.cell(25, 8, "Qty", border=1, align="C", fill=True)
pdf.cell(35, 8, "Unit Price (R)", border=1, align="R", fill=True)
pdf.cell(40, 8, "Total (R)", border=1, align="R", fill=True)
pdf.ln()

# Table Body with Alternating Colors (2-Tail Speed Optimization)
pdf.set_font("Helvetica", size=9)
grand_total = 0.0

for idx, item in enumerate(parsed_items):
    desc = str(item.get("description", ""))
    qty = int(item.get("quantity", 1))
    price = float(item.get("unit_price", 0.0))
    total = qty * price
    grand_total += total

    # Alternating row highlight
    bg = True if idx % 2 == 1 else False
    if bg:
        pdf.set_fill_color(248, 249, 250)

    pdf.cell(90, 7, desc, border=1, fill=bg)
    pdf.cell(25, 7, str(qty), border=1, align="C", fill=bg)
    pdf.cell(35, 7, f"{price:.2f}", border=1, align="R", fill=bg)
    pdf.cell(40, 7, f"{total:.2f}", border=1, align="R", fill=bg)
    pdf.ln()

# Grand Total
pdf.set_font("Helvetica", style="B", size=10)
pdf.cell(150, 9, "Total Amount Due:", border=0, align="R")
pdf.cell(40, 9, f"R {grand_total:.2f}", border=1, align="R")
pdf.ln(12)

# AI Notes Output
ai_notes = [v for v in nim_results.values() if v]
if ai_notes:
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.multi_cell(0, 4, "\n".join(ai_notes))

# Export PDF File
pdf.output("invoice.pdf")

# Output Kurama Performance Report
elapsed = time.time() - start_time
print(f"⚡ [Kurama] Tailed Beast Invoice generated in {elapsed:.2f} seconds!")
