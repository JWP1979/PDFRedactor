import pdfplumber
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- FILE PATHS ---
PDF_PATH = "Statement_from_bank_accounts_27042020.pdf"
EXCEL_PATH = "2020 Output.xlsx"
OUTPUT_PDF_PATH = "Filtered_Statement_April2020.pdf"

# --- LOAD WITHDRAWALS FROM EXCEL ---
df = pd.read_excel(EXCEL_PATH)
withdrawals_raw = df["Withdrawals (PLN)"].dropna().astype(str)
withdrawals_cleaned = withdrawals_raw.str.replace(",", ".").str.strip()
withdrawal_amounts = set(f"{float(val):.2f}" for val in withdrawals_cleaned)

# --- SETUP OUTPUT PDF ---
c = canvas.Canvas(OUTPUT_PDF_PATH, pagesize=A4)
width, height = A4
y_position = height - 50
matched_rows = 0

# --- OPEN PDF WITH pdfplumber ---
with pdfplumber.open(PDF_PATH) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if not table:
            continue

        for row in table:
            if not row:
                continue

            # Check if any cell contains a matching withdrawal
            row_text = "   ".join(cell if cell else "" for cell in row)
            if any(w in row_text.replace(",", ".") for w in withdrawal_amounts):
                c.drawString(50, y_position, row_text)
                y_position -= 15
                matched_rows += 1

                if y_position < 50:
                    c.showPage()
                    y_position = height - 50

# Add message if nothing matched
if matched_rows == 0:
    c.drawString(50, height - 50, "⚠ No transactions matched the withdrawal list.")

# --- SAVE OUTPUT PDF ---
c.save()

print(f"✅ Done. {matched_rows} matching rows written to: {OUTPUT_PDF_PATH}")