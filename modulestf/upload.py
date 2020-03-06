import os
import uuid
from hashlib import md5

import boto3

from .const import S3_BUCKET, S3_BUCKET_REGION
from .logger import setup_logging

logger = setup_logging()


def upload_file_to_s3(filename):
    s3_bucket = os.environ.get("S3_BUCKET", S3_BUCKET)
    s3_dir = os.environ.get("S3_DIR", "local")

    zip_filename = md5(bytes(uuid.uuid4().hex, "ascii")).hexdigest() + ".zip"

    s3 = boto3.client("s3", region_name=S3_BUCKET_REGION)
    s3_key = s3_dir + "/" + zip_filename

    s3.upload_file(filename, s3_bucket, s3_key, ExtraArgs=dict(
        ACL="public-read",
        ContentType="application/zip",
        StorageClass="ONEZONE_IA"
    ))

    # Perfect: With Cloudfront https is available
    # link = "https://" + s3_bucket + "/" + s3_key

    # Long URL because there is no Cloudfront distribution (yet)
    link = "https://s3-" + S3_BUCKET_REGION + ".amazonaws.com/" + s3_bucket + "/" + s3_key

    logger.info("LINK=" + link)

    return link
