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
