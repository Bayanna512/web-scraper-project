import os
import io
import pandas as pd
import boto3
import dateparser
from src.html_scraper import fetch_press_releases
from src.pdf_parser import process_pdf
from src.translator import GoogleTranslator, translate_text
from config import CSV_OUTPUT_FILE, S3_BUCKET, S3_PREFIX

def normalize_date(date_str):
    dt = dateparser.parse(date_str, languages=['ja', 'en'])
    if dt:
        return dt.strftime('%Y-%m-%d')
    return date_str  # fallback if parsing fails

translator = GoogleTranslator(source='auto', target='en')
all_records = []

for idx, record in enumerate(fetch_press_releases(), 1):
    try:
        record["title_en"] = translate_text(record["title_jp"], translator)
    except Exception:
        record["title_en"] = "[TRANSLATION ERROR]"

    # Normalize Japanese dates dynamically (if date key exists)
    if "date" in record:
        record["date"] = normalize_date(record["date"])

    if record["pdf_link"].lower().endswith(".pdf"):
        process_pdf(record, translator, idx)
    else:
        record["pdf_text_en"] = "[NO PDF LINK]"

    all_records.append(record)

final_df = pd.DataFrame(all_records)

# Prepare CSV as in-memory string buffer
csv_buffer = io.StringIO()
final_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")

# Upload CSV content directly to S3
s3_client = boto3.client('s3')
s3_client.put_object(
    Bucket=S3_BUCKET,
    Key=f"{S3_PREFIX}{os.path.basename(CSV_OUTPUT_FILE)}",
    Body=csv_buffer.getvalue()
)

print("All done. Data uploaded directly to S3.")
