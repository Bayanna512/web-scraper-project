TEPCO Energy Website Data Scraper & Translator

--------------------
Overview
--------------------

This project automates data scraping from the TEPCO website, extracting structured and unstructured data such as HTML content, PDFs, and tables. The extracted content is translated from Japanese to English using Google Translate APIs and uploaded directly to AWS S3 for further analysis.

--------------------
Key Features
--------------------

- Scrapes press releases and data from the TEPCO website  
- Extracts and translates PDF text and tables into English  
- Handles complex data types: HTML, PDF text, CSV tables  
- Uploads output CSV files and translated tables to AWS S3  
- Fully containerized with Docker for easy deployment  
- Infrastructure provisioning using Terraform  
- CI/CD pipelines configured using GitHub Actions workflows  

--------------------
Directory Structure
--------------------

project-root/  
│  
├── Dockerfile  
├── Terraform/  
│   └── main.tf  
├── .github/  
│   └── workflows/  
│       ├── ci.yml  
│       └── cd.yml  
├── config.py            # Config variables like S3 bucket, prefixes, output paths  
├── main.py              # Entry point to run scraping, translation, and upload  
├── README.md  
├── requirements.txt  
├── src/  
│   ├── html_scraper.py  # Logic to scrape press releases from TEPCO website  
│   ├── pdf_parser.py    # Handles downloading, parsing, and translating PDFs  
│   ├── s3_utils.py      # AWS S3 helpers for uploading files/buffers  
│   ├── translator.py    # Translation utilities with chunking support  

--------------------
Workflow Summary
--------------------

1. Scrape TEPCO website for press releases metadata  
2. Translate titles from Japanese to English  
3. Download PDFs and extract all text and tables  
4. Translate PDF content fully into English  
5. Upload results to AWS S3 for downstream use  

--------------------
Project Modules & Purpose
--------------------

| Module           | Purpose                                           |
|------------------|-------------------------------------------------|
| main.py          | Coordinates entire ETL pipeline                   |
| html_scraper.py  | Scrapes press release metadata                    |
| pdf_parser.py    | Downloads PDFs, extracts and translates content  |
| translator.py    | Handles text translation with chunking support   |
| s3_utils.py      | Upload utilities for AWS S3                        |
| config.py        | Configuration parameters (bucket names, paths)   |

--------------------
Libraries & Dependencies
--------------------

- **requests**  
  Used to send HTTP requests for scraping HTML pages and downloading PDF files.

- **pdfplumber**  
  Parses PDF files to extract textual content and tables for further processing.

- **pandas**  
  Data manipulation and conversion of extracted tables into CSV format.

- **boto3**  
  AWS SDK for Python to interact with AWS S3 for uploading output files.

- **googletrans (or custom GoogleTranslator wrapper)**  
  Provides translation services from Japanese to English using Google Translate APIs.

- **io**  
  Handles in-memory file operations (StringIO, BytesIO) for efficient data streaming.

- **os**  
  File path and environment variable management.

- **logging** (optional but recommended)  
  To log application flow, errors, and debugging information.

