provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_s3_bucket" "webscraper_bucket" {
  bucket = "webscraper-20250614"

}
resource "aws_s3_bucket_acl" "bucket_acl" {

  bucket = aws_s3_bucket.webscraper_bucket.id
  acl    = "private"
}

