import io
import requests
import pdfplumber
import pandas as pd
from src.translator import translate_dataframe, translate_text, chunk_text
from src.s3_utils import upload_file_to_s3_buffer  # New helper to upload from buffer
from config import TABLES_DIR, TABLES_TRANSLATED_DIR, S3_BUCKET, S3_PREFIX


def process_pdf(record, translator, idx):
    link = record["pdf_link"]
    try:
        response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        response.raise_for_status()

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            translated = "\n".join(translate_text(chunk, translator) for chunk in chunk_text(full_text))
            record["pdf_text_en"] = translated if translated.strip() else "[NO TEXT IN PDF]"

            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if tables and len(tables) > 0:
                    table = tables[0]
                    if table and len(table) >= 2:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df.columns = df.columns.str.strip()

                        # Original table CSV buffer
                        orig_buffer = io.StringIO()
                        df.to_csv(orig_buffer, index=False)
                        orig_buffer.seek(0)

                        # Upload original CSV buffer to S3
                        s3_key_orig = f"{S3_PREFIX}{TABLES_DIR}/table_{idx}_{page_num}_1.csv"
                        upload_file_to_s3_buffer(orig_buffer, S3_BUCKET, s3_key_orig)

                        # Translated table CSV buffer
                        df_translated = translate_dataframe(df, translator)
                        trans_buffer = io.StringIO()
                        df_translated.to_csv(trans_buffer, index=False)
                        trans_buffer.seek(0)

                        # Upload translated CSV buffer to S3
                        s3_key_trans = f"{S3_PREFIX}{TABLES_TRANSLATED_DIR}/table_{idx}_{page_num}_1_translated.csv"
                        upload_file_to_s3_buffer(trans_buffer, S3_BUCKET, s3_key_trans)

    except Exception:
        record["pdf_text_en"] = "[PDF DOWNLOAD/READ ERROR]"
