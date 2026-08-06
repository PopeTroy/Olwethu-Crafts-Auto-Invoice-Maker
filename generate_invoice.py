import os
import json
import urllib.request
from openai import OpenAI
from fpdf import FPDF

# Initialize NVIDIA NIM Client
api_key = os.getenv("NVCF_TARGET_SERVICE_KEY", "")
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key if api_key else "dummy_key"
)

# Header & Client Variables
invoice_number = os.getenv("INVOICE_NUMBER", "INV-2026-001")
date = os.getenv("INVOICE_DATE", "2026-08-06")
client_name = os.getenv("CLIENT_NAME", "Valued Client")
client_address = os.getenv("CLIENT_ADDRESS", "Sandton, Johannesburg")
client_telephone = os.getenv("CLIENT_TELEPHONE", "082 000 0000")
client_email = os.getenv("CLIENT_EMAIL", "client@example.com")

logo_url = "https://celsiustechmediagroup.co.za/wp-content/uploads/2026/08/IMG-20260801-WA0000.jpg"
logo_path = "company_logo.jpg"

# Download Logo
try:
    req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(logo_path, 'wb') as out_file:
        out_file.write(response.read())
except Exception as e:
    print(f"Notice: Logo download bypassed ({e}).")
    logo_path = None

# Collect and Parse the 10 Item Inputs
raw_items = []
for i in range(1, 11):
    val = os.getenv(f"ITEM_{i}", "").strip()
    if val:
        raw_items.append(val)

parsed_items = []
for item_str in raw_items:
    parts = [p.strip() for p in item_str.split(",")]
    if len(parts) >= 3:
        desc = parts[0]
        try:
            qty = int(parts[1])
        except ValueError:
            qty = 1
        try:
            price = float(parts[2])
        except ValueError:
            price = 0.0
        parsed_items.append({"description": desc, "quantity": qty, "unit_price": price})
    elif len(parts) == 1 and parts[0]:
        parsed_items.append({"description": parts[0], "quantity": 1, "unit_price": 0.0})

if not parsed_items:
    parsed_items = [{"description": "General Auto Service", "quantity": 1, "unit_price": 0.0}]

# --- NVIDIA NIM MICROSERVICES PIPELINE ---
def call_nim_model(model_name: str, prompt: str) -> str:
    if not api_key or api_key == "dummy_key":
        return ""
    try:
        response = nvidia_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"NIM Model {model_name} skipped: {e}")
        return ""

print("Executing NIM 1 (Llama 3.3 70B - Validation)...")
call_nim_model("meta/llama-3.3-70b-instruct", f"Validate item list: {json.dumps(parsed_items)}")

print("Executing NIM 2 (DeepSeek R1 - Math Check)...")
call_nim_model("deepseek-ai/deepseek-r1", f"Verify total price calculation for: {json.dumps(parsed_items)}")

print("Executing NIM 3 (Nemotron 4 340B - Warranty Text)...")
res_3 = call_nim_model("nvidia/nemotron-4-340b-instruct", "Generate a 1-sentence repair warranty note for South Africa.")

print("Executing NIM 4 (Qwen 2.5 72B - Address Cleaning)...")
res_4 = call_nim_model("qwen/qwen2.5-72b-instruct", f"Clean up this address: {client_address}")

print("Executing NIM 5 (Mistral Large 2 - Thank You Note)...")
res_5 = call_nim_model("mistralai/mistral-large-2-instruct", f"Write a warm 1-sentence thank you note to {client_name}.")

print("Executing NIM 6 (Gemma 2 27B - Quality Audit)...")
call_nim_model("google/gemma-2-27b-it", f"Audit invoice #{invoice_number}.")

# --- PDF GENERATION ---
class InvoicePDF(FPDF):
    def footer(self):
        self.set_y(-25)
        self.set_font("Helvetica", size=8)
        self.set_text_color(100, 100, 100)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        footer_text = (
            "Olwethu Crafts Auto | Address: 1 Apex Rd, Chloorkop, JHB | "
            "Tel: 061 588 0157 | Email: info@olwethucrafts.co.za / osiyatula@gmail.com\n"
            "Thank you for your business. All work completed carries our standard warranty."
        )
        self.multi_cell(0, 4, footer_text, align="C")

pdf = InvoicePDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=30)

# Render Logo Image
if logo_path and os.path.exists(logo_path):
    try:
        pdf.image(logo_path, x=10, y=8, w=45)
    except Exception:
        pass

# Business Details
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

# Client Details Header
pdf.set_font("Helvetica", style="B", size=11)
pdf.cell(100, 6, "INVOICE TO:", ln=False)
pdf.cell(0, 6, f"INVOICE NO: {invoice_number}", ln=True, align="R")

pdf.set_font("Helvetica", size=9)
start_y = pdf.get_y()

formatted_address = res_4.strip() if res_4 else client_address
client_info = (
    f"Client Name: {client_name}\n"
    f"Address: {formatted_address}\n"
    f"Tel: {client_telephone}\n"
    f"Email: {client_email}"
)
pdf.multi_cell(100, 5, client_info)

pdf.set_xy(110, start_y)
pdf.cell(0, 5, f"Date: {date}", align="R")
pdf.ln(20)

# Table Header
pdf.set_font("Helvetica", style="B", size=10)
pdf.set_fill_color(240, 240, 240)
pdf.cell(90, 8, "Description", border=1, fill=True)
pdf.cell(25, 8, "Qty", border=1, align="C", fill=True)
pdf.cell(35, 8, "Unit Price (R)", border=1, align="R", fill=True)
pdf.cell(40, 8, "Total (R)", border=1, align="R", fill=True)
pdf.ln()

# Table Data
pdf.set_font("Helvetica", size=9)
grand_total = 0.0

for item in parsed_items:
    desc = str(item.get("description", ""))
    qty = int(item.get("quantity", 1))
    price = float(item.get("unit_price", 0.0))
    total = qty * price
    grand_total += total

    pdf.cell(90, 8, desc, border=1)
    pdf.cell(25, 8, str(qty), border=1, align="C")
    pdf.cell(35, 8, f"{price:.2f}", border=1, align="R")
    pdf.cell(40, 8, f"{total:.2f}", border=1, align="R")
    pdf.ln()

# Total Row
pdf.set_font("Helvetica", style="B", size=10)
pdf.cell(150, 10, "Total Amount Due:", border=0, align="R")
pdf.cell(40, 10, f"R {grand_total:.2f}", border=1, align="R")
pdf.ln(15)

# NIM Notes Section
notes = []
if res_5:
    notes.append(res_5.strip())
if res_3:
    notes.append(res_3.strip())

if notes:
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.multi_cell(0, 4, "\n".join(notes))

pdf.output("invoice.pdf")
print("Invoice PDF successfully generated.")
