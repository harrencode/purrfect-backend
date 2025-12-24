import boto3
from botocore.client import Config
import uuid
import os

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
    config=Config(signature_version="s3v4")
)

def upload_image_to_s3(file, folder="pets"):
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
