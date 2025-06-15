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
