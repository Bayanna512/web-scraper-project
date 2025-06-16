html_parser.py

import requests  # HTTP requests
from bs4 import BeautifulSoup  # HTML parsing
from urllib.parse import urljoin  # To build absolute URLs
from config import BASE_URL, PRESS_RELEASE_URL  # URLs config


def fetch_press_releases():
    r = requests.get(PRESS_RELEASE_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    r.raise_for_status()  # Check for request success
    r.encoding = 'utf-8'  # Ensure proper encoding for Japanese text

    soup = BeautifulSoup(r.text, "html.parser")
    dl = soup.find("dl")  # Locate the container holding releases
    if not dl:
        raise Exception("Could not find <dl> element on the page")

    dts = dl.find_all("dt")  # Dates
    dds = dl.find_all("dd")  # Corresponding release info

    press_list = []
    for dt, dd in zip(dts, dds):
        date = dt.get_text(strip=True)
        a = dd.find("a")
        if a:
            link = urljoin(BASE_URL, a['href'])  # Convert to full URL
            title = a.get_text(strip=True)
            press_list.append({"date": date, "title_jp": title, "pdf_link": link})

    return press_list


main.py 

import os
import io
import pandas as pd
import boto3
from src.html_scraper import fetch_press_releases
from src.pdf_parser import process_pdf
from src.translator import GoogleTranslator, translate_text
from config import CSV_OUTPUT_FILE, S3_BUCKET, S3_PREFIX

translator = GoogleTranslator(source='auto', target='en')
all_records = []

for idx, record in enumerate(fetch_press_releases(), 1):
    try:
        record["title_en"] = translate_text(record["title_jp"], translator)
    except Exception:
        record["title_en"] = "[TRANSLATION ERROR]"

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


pdf_parser.py 

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


---s3_utils.py ---

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def upload_file_to_s3(file_path, bucket, s3_key):
    """
    Upload a local file to AWS S3 bucket at the specified S3 key (path).

    Args:
        file_path (str): Local path of the file to upload.
        bucket (str): Name of the target S3 bucket.
        s3_key (str): Destination path/key inside the S3 bucket.
    """
    s3 = boto3.client('s3')

    try:
        s3.upload_file(file_path, bucket, s3_key)
        print(f"Uploaded local file to s3://{bucket}/{s3_key}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except NoCredentialsError:
        print("AWS credentials not available. Check your environment configuration.")
    except ClientError as e:
        print(f"Failed to upload file: {e}")

def upload_file_to_s3_buffer(buffer, bucket, s3_key):
    """
    Upload content from an in-memory buffer (e.g., io.StringIO) to AWS S3.

    Args:
        buffer (io.StringIO): In-memory text buffer containing the data.
        bucket (str): Name of the target S3 bucket.
        s3_key (str): Destination path/key inside the S3 bucket.
    """
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=bucket, Key=s3_key, Body=buffer.getvalue())
        print(f"Uploaded buffer content to s3://{bucket}/{s3_key}")
    except NoCredentialsError:
        print("AWS credentials not available. Check your environment configuration.")
    except ClientError as e:
        print(f"Failed to upload buffer content: {e}")


---translator.py ---

import time
from deep_translator import GoogleTranslator

def chunk_text(text, max_len=4000):
    """
    Splits text into chunks of max_len characters to avoid API limits.
    """
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]

def translate_text(text, translator):
    """
    Translates given text using the provided translator instance.
    Retries once after a short delay if translation fails.
    Returns a placeholder on failure.
    """
    if not text.strip():
        return ""
    try:
        return translator.translate(text)
    except Exception:
        time.sleep(5)  # Wait before retrying
        try:
            return translator.translate(text)
        except Exception:
            return "[TRANSLATION ERROR]"

def is_number(text):
    """
    Checks if text represents a number (int or float).
    """
    try:
        float(text.replace(',', ''))  # handle numbers with commas
        return True
    except ValueError:
        return False

def translate_dataframe(df, translator):
    """
    Translates DataFrame headers and cells (except numbers and empty strings).
    Returns a new DataFrame with translated content.
    """
    translated_df = df.copy()
    # Translate column headers
    translated_df.columns = [
        translate_text(col.strip(), translator) if col.strip() else col for col in df.columns
    ]
    # Translate each cell, skipping numbers or empty cells
    for col in translated_df.columns:
        translated_df[col] = [
            cell if not cell.strip() or is_number(cell.strip()) else translate_text(cell.strip(), translator)
            for cell in translated_df[col].astype(str)
        ]
    return translated_df

-----main.tf----

# Configure the AWS Provider
provider "aws" {
  region = "ap-southeast-1"  # Singapore region
}

# Create an S3 bucket for the web scraper project
resource "aws_s3_bucket" "webscraper_bucket" {
  bucket = "webscraper-20250614"  # Must be globally unique

  # Tags for visibility and cost tracking
  tags = {
    Name        = "webscraper-20250614"
    Environment = "Dev"
    Project     = "Web Scraper"
    Owner       = "Bayanna"
  }
}


-----------config.py ----

# Base URL for the TEPCO website
BASE_URL = "https://www.tepco.co.jp"

# URL to scrape press releases (Japanese index page)
PRESS_RELEASE_URL = "https://www.tepco.co.jp/press/release/index-j.html"

# Output CSV file path for the final translated press release data
CSV_OUTPUT_FILE = "output/tepco_translated_press_with_pdf.csv"

# Directory to store extracted PDF tables (original)
TABLES_DIR = "output/extracted_pdf_tables"

# Directory to store translated PDF tables
TABLES_TRANSLATED_DIR = "output/extracted_pdf_tables_translated"

# AWS S3 bucket name for uploads
S3_BUCKET = "webscraper-20250614"

# S3 key prefix for uploaded files
S3_PREFIX = "raw/tepco/"


Docker ---

# Use official Python 3.9 slim image as base
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy your entire project code into /app
COPY . .

# ✅ Let Python find your 'src' package
ENV PYTHONPATH="/app"

# Default command to run your scraper script
CMD ["python3", "src/main.py"]

----cd.yml----

name: CD Pipeline

on:
  workflow_run:
    workflows: ["CI Pipeline"]   
    types:
      - completed

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}  # only run if CI succeeded
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Install Terraform CLI
        uses: hashicorp/setup-terraform@v3

      - name: List Terraform files
        run: ls -R
        working-directory: Terraform

      - name: Terraform Init
        run: terraform init
        working-directory: Terraform

      - name: Terraform Validate
        run: terraform validate
        working-directory: Terraform

      # Uncomment to deploy
      # - name: Terraform Apply
      #   run: terraform apply -auto-approve
      #   working-directory: Terraform


----ci.yml----

name: CI Pipeline

on:
  push:
    branches:
      - main
      - bayanna
  pull_request:
    branches:
      - main
      - bayanna
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Terraform CLI
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init
        working-directory: Terraform

      - name: Terraform Validate
        run: terraform validate
        working-directory: Terraform

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build Docker image
        run: docker build -t web-scraper:latest .

      - name: Run scraper inside Docker
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ap-southeast-1
        run: |
          docker run --rm \
            -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
            -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
            -e AWS_REGION=$AWS_REGION \
            web-scraper:latest

