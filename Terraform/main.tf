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
