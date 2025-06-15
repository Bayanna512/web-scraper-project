# web-scraper-project
A scalable and modular Python web scraping project for extracting, processing, and exporting data from multiple websites efficiently to S3.

# TEPCO Press Release Web Scraper & PDF Extractor

---

## Overview

This project is a scalable Python-based web scraper designed to extract press release data from the [Tokyo Electric Power Company (TEPCO)](https://www.tepco.co.jp) website. It scrapes Japanese press release titles and PDF links, translates the content to English, extracts tables from PDFs, translates tables, and uploads all results to AWS S3 for further processing or analytics.

---

## Features

- Scrapes press release metadata (date, title, PDF link) from TEPCO's press release webpage.
- Downloads and parses PDF documents linked on the page.
- Extracts full text and tabular data from PDFs using `pdfplumber`.
- Translates Japanese text and table contents into English using Google Translate API (`deep_translator`).
- Saves original and translated content seamlessly to an AWS S3 bucket for further analysis, processing.
- Modular code structure supporting easy enhancements.
- Ready for containerization and CI/CD pipeline integration.

---

## Project Structure

web-scraper-project/
│
├── src/
│   ├── html_scraper.py         # Scrapes HTML pages for press release metadata
│   ├── pdf_parser.py           # Downloads PDFs, extracts text and tables, and translates content
│   ├── translator.py           # Utilities for translating text and DataFrames using Google Translate
│   ├── s3_utils.py             # Handles file uploads to AWS S3
│   └── main.py                 # Entry point: orchestrates scraping, translation, and S3 upload
│
├── config.py                  # Centralized configuration (URLs, AWS bucket, output paths)
├── requirements.txt           # Python package dependencies
├── README.md                  # Project overview and usage instructions



---

## Key Technologies & Libraries

| Technology         | Purpose                                               |
|--------------------|-----------------------------------------------------|
| `requests`          | HTTP requests for HTML and PDF download              |
| `beautifulsoup4`    | Parsing HTML content                                 |
| `pdfplumber`        | PDF text and table extraction                         |
| `deep_translator`   | Translate Japanese to English text                    |
| `pandas`            | Data manipulation and CSV output                      |
| `boto3`             | AWS S3 file upload                                    |

---


