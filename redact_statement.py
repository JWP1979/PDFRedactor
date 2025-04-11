import pdfplumber
import pandas as pd
import fitz  # PyMuPDF

# --- FILE PATHS ---
PDF_PATH = "Statement_from_bank_accounts_27042020.pdf"
EXCEL_PATH = "2020 Output.xlsx"
OUTPUT_PDF_PATH = "Filtered_Statement_April2020.pdf"

# --- LOAD WITHDRAWALS FROM EXCEL (CLEANED) ---
df = pd.read_excel(EXCEL_PATH)
withdrawals_raw = df["Withdrawals (PLN)"].dropna().astype(str)

# Clean: remove PLN, replace comma with dot, trim spaces
amounts = withdrawals_raw.str.replace("PLN", "", regex=False)\
                         .str.replace(",", ".", regex=False)\
                         .str.strip().astype(float)

amounts_set = set(f"{amt:.2f}" for amt in amounts)

# --- OPEN PDF ---
pdf = pdfplumber.open(PDF_PATH)
original_doc = fitz.open(PDF_PATH)
new_doc = fitz.open()  # Will hold the final redacted version

for i, page in enumerate(pdf.pages):
    text_lines = page.extract_text().split("\n")
    original_page = original_doc[i]
    new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)

    for line in text_lines:
        line_clean = line.replace(",", "").strip()
        for amount in amounts_set:
            if f"{amount} PLN" in line_clean:
                # Draw the line on the new PDF page
                new_page.insert_text((50, 50 + 12 * text_lines.index(line)), line, fontsize=9)
                break

pdf.close()
original_doc.close()

# --- SAVE THE NEW PDF ---
new_doc.save(OUTPUT_PDF_PATH)
new_doc.close()

print(f"✅ Done! Filtered PDF saved as: {OUTPUT_PDF_PATH}")