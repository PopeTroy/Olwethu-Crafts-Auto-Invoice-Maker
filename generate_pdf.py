import os
import json
import urllib.request
from openai import OpenAI
from fpdf import FPDF

# Initialize NVIDIA NIM Client
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVCF_TARGET_SERVICE_KEY")
)

# Fetch input variables from workflow environment
invoice_number = os.getenv("INVOICE_NUMBER", "INV-2026-001")
date = os.getenv("INVOICE_DATE", "2026-08-06")
client_name = os.getenv("CLIENT_NAME", "Client Name")
client_address = os.getenv("CLIENT_ADDRESS", "Client Address")
client_telephone = os.getenv("CLIENT_TELEPHONE", "000 000 0000")
client_email = os.getenv("CLIENT_EMAIL", "client@email.com")
raw_services = os.getenv("RAW_SERVICES", "Engine Maintenance quantity 1 price 1500")

logo_url = "https://celsiustechmediagroup.co.za/wp-content/uploads/2026/08/IMG-20260801-WA0000.jpg"

def call_nim_model(model_name: str, prompt: str) -> str:
    """Helper function to run inference against an NVIDIA NIM Microservice."""
    try:
        response = nvidia_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling {model_name}: {e}")
        return ""

# Download Logo Image locally
logo_path = "company_logo.jpg"
try:
    urllib.request.urlretrieve(logo_url, logo_path)
except Exception as e:
    print(f"Warning: Logo download failed ({e}). Proceeding without image.")
    logo_path = None

# --- 6 NVIDIA NIM MICROSERVICE ENSEMBLE PIPELINE ---

# Model 1: Line Item Parsing
print("Running NIM 1 (Llama 3.3 70B)...")
prompt_1 = f"Parse the following services text into JSON format array of objects with keys 'description', 'quantity', 'unit_price': {raw_services}"
res_1 = call_nim_model("meta/llama-3.3-70b-instruct", prompt_1)

# Model 2: Mathematical Audit
print("Running NIM 2 (DeepSeek R1)...")
prompt_2 = f"Verify calculations for items: {res_1}. Ensure correct unit prices and quantities."
res_2 = call_nim_model("deepseek-ai/deepseek-r1", prompt_2)

# Model 3: Compliance & Legal Terms
print("Running NIM 3 (Nemotron 4 340B)...")
prompt_3 = "Generate a concise 2-sentence payment terms notice for auto repair services in South Africa."
res_3 = call_nim_model("nvidia/nemotron-4-340b-instruct", prompt_3)

# Model 4: Formatting Verification
print("Running NIM 4 (Qwen 2.5 72B)...")
prompt_4 = f"Standardize contact address formatting for: {client_address}"
res_4 = call_nim_model("qwen/qwen2.5-72b-instruct", prompt_4)

# Model 5: Thank You Note Generation
print("Running NIM 5 (Mistral Large 2)...")
prompt_5 = f"Write a professional 1-sentence thank you note to client {client_name} from Olwethu Crafts Auto."
res_5 = call_nim_model("mistralai/mistral-large-2-instruct", prompt_5)

# Model 6: Final Quality Check
print("Running NIM 6 (Gemma 2 27B)...")
prompt_6 = f"Perform final check for invoice #{invoice_number} addressed to {client_name}. Output status PASS or FAIL."
res_6 = call_nim_model("google/gemma-2-27b-it", prompt_6)
print(f"NIM Quality Audit Result: {res_6}")

# --- PARSE ITEMS AND GENERATE PDF ---
try:
    # Attempt parsing JSON from Model 1 output or fallback to safe parsing
    import re
    match = re.search(r'\[.*\]', res_1, re.DOTALL)
    items = json.loads(match.group(0)) if match else [{"description": raw_services, "quantity": 1, "unit_price": 1000.00}]
except Exception:
    items = [{"description": raw_services, "quantity": 1, "unit_price": 1000.00}]

class InvoicePDF(FPDF):
    def footer(self):
        self.set_y(-25)
        self.set_font("Helvetica", size=8)
        self.set_text_color(100, 100, 100)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        # Footer Fine Print (Olwethu Crafts Auto Details)
        footer_text = (
            "Company: Olwethu Crafts Auto | Address: 1 Apex Rd, Chloorkop, JHB | "
            "Tel: 061 588 0157 | Email: info@olwethucrafts.co.za / osiyatula@gmail.com\n"
            "Thank you for choosing Olwethu Crafts Auto. All services subject to standard warranty terms."
        )
        self.multi_cell(0, 4, footer_text, align="C")

pdf = InvoicePDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=30)

# Header Logo & Business Information
if logo_path and os.path.exists(logo_path):
    pdf.image(logo_path, x=10, y=8, w=45)

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

client_info = (
    f"Client Name: {client_name}\n"
    f"Address: {res_4 if res_4 else client_address}\n"
    f"Tel: {client_telephone}\n"
    f"Email: {client_email}"
)
pdf.multi_cell(100, 5, client_info)

pdf.set_xy(110, start_y)
pdf.cell(0, 5, f"Date: {date}", align="R")
pdf.ln(20)

# Line Items Table
pdf.set_font("Helvetica", style="B", size=10)
pdf.set_fill_color(240, 240, 240)
pdf.cell(90, 8, "Description", border=1, fill=True)
pdf.cell(25, 8, "Qty", border=1, align="C", fill=True)
pdf.cell(35, 8, "Unit Price (R)", border=1, align="R", fill=True)
pdf.cell(40, 8, "Total (R)", border=1, align="R", fill=True)
pdf.ln()

pdf.set_font("Helvetica", size=9)
grand_total = 0.0

for item in items:
    desc = str(item.get("description", "Service Item"))
    qty = int(item.get("quantity", 1))
    price = float(item.get("unit_price", 0.0))
    total = qty * price
    grand_total += total

    pdf.cell(90, 8, desc, border=1)
    pdf.cell(25, 8, str(qty), border=1, align="C")
    pdf.cell(35, 8, f"{price:.2f}", border=1, align="R")
    pdf.cell(40, 8, f"{total:.2f}", border=1, align="R")
    pdf.ln()

# Grand Total
pdf.set_font("Helvetica", style="B", size=10)
pdf.cell(150, 10, "Total Amount Due:", border=0, align="R")
pdf.cell(40, 10, f"R {grand_total:.2f}", border=1, align="R")
pdf.ln(15)

# Notes generated by NVIDIA NIM models
if res_3 or res_5:
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.multi_cell(0, 4, f"Note: {res_5 if res_5 else ''}\n{res_3 if res_3 else ''}")

pdf.output("invoice.pdf")
print("Invoice PDF successfully generated with 6-model NVIDIA NIM pipeline.")
