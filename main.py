from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import csv
import pdfplumber
from datetime import datetime
import re

app = FastAPI()

# Enable CORS for frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_transaction_line(text_line):
    return re.match(r"^(\d{1,2}[\/\-\s]\d{1,2})", text_line)

def extract_fields(line, inferred_year):
    match = re.match(r"^(\d{1,2}[\/\-\s]\d{1,2})\s+(.*?)\s+(-?[\d,.]+)\s+(-?[\d,.]+)$", line)
    if match:
        date_str, desc, amount, balance = match.groups()
        date_full = f"{date_str.strip()}/{inferred_year}"
        try:
            date = datetime.strptime(date_full, "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            date = date_full
        return {
            "date": date,
            "description": desc.strip(),
            "amount": amount.replace(',', ''),
            "balance": balance.replace(',', '')
        }
    return None

@app.post("/parse")
async def parse_pdf(file: UploadFile = File(...), debug: bool = Query(False)):
    content = await file.read()
    transactions = []
    inferred_year = datetime.today().year
    debug_lines = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        current_transaction = None
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                debug_lines.append(f"--- Page {page_number} ---")
                debug_lines.extend(lines)
                for line in lines:
                    if is_transaction_line(line):
                        if current_transaction:
                            transactions.append(current_transaction)
                        fields = extract_fields(line, inferred_year)
                        if fields:
                            current_transaction = fields
                    else:
                        if current_transaction:
                            current_transaction['description'] += ' ' + line.strip()
        if current_transaction:
            transactions.append(current_transaction)

    if debug:
        return PlainTextResponse("\n".join(debug_lines), media_type="text/plain")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["date", "description", "amount", "balance"])
    writer.writeheader()
    for row in transactions:
        writer.writerow(row)
    output.seek(0)

    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename=parsed_{file.filename}.csv"
    })
