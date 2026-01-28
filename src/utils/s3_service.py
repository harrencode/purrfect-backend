import boto3
from botocore.client import Config
import uuid
import os

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

client_kwargs = {
    "region_name": AWS_REGION,
    "config": Config(signature_version="s3v4"),
}

# If credentials are not explicitly provided, boto3 will use the default credential chain
# (ideal for AWS Elastic Beanstalk via instance profile / IAM role).
if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    client_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY
    client_kwargs["aws_secret_access_key"] = AWS_SECRET_KEY

s3 = boto3.client("s3", **client_kwargs)

def upload_image_to_s3(file, folder="pets"):
    if not BUCKET_NAME:
        raise RuntimeError("AWS_S3_BUCKET_NAME is not set")

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

    s3.upload_fileobj(
        file.file,
        BUCKET_NAME,
        unique_filename,
        ExtraArgs={
            "ContentType": file.content_type,
            # "ACL": "public-read"
        }
    )

    return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
