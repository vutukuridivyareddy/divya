"""Create an AWS S3 bucket and apply tags using boto3."""

import argparse
import logging
import sys

import boto3
from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def create_bucket(bucket_name: str, region: str = None) -> None:
    """Create an S3 bucket in a specified region."""
    try:
        if region is None or region == "us-east-1":
            s3_client = boto3.client("s3")
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client("s3", region_name=region)
            location = {"LocationConstraint": region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

        logger.info("Bucket '%s' created successfully.", bucket_name)
    except ClientError as error:
        logger.error("Could not create bucket '%s': %s", bucket_name, error)
        raise


def tag_bucket(bucket_name: str, tags: dict) -> None:
    """Add tags to an existing S3 bucket."""
    if not tags:
        logger.info("No tags provided, skipping tagging.")
        return

    tag_set = [{"Key": key, "Value": value} for key, value in tags.items()]
    s3_client = boto3.client("s3")
    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={"TagSet": tag_set},
        )
        logger.info("Tags applied to bucket '%s'.", bucket_name)
    except ClientError as error:
        logger.error("Could not tag bucket '%s': %s", bucket_name, error)
        raise


def parse_tags(tag_args):
    """Parse tags passed as Key=Value strings into a dict."""
    tags = {}
    for tag in tag_args or []:
        if "=" not in tag:
            raise ValueError("Tag must be in Key=Value format: %s" % tag)
        key, value = tag.split("=", 1)
        tags[key.strip()] = value.strip()
    return tags


def main():
    parser = argparse.ArgumentParser(description="Create an S3 bucket and add tags.")
    parser.add_argument("bucket_name", help="Name of the S3 bucket to create.")
    parser.add_argument("--region", default="us-east-1", help="AWS region for the S3 bucket.")
    parser.add_argument(
        "--tag",
        action="append",
        help="Tag in Key=Value format. Use multiple times for multiple tags.",
    )
    args = parser.parse_args()

    try:
        tags = parse_tags(args.tag)
    except ValueError as error:
        logger.error(error)
        sys.exit(1)

    try:
        create_bucket(args.bucket_name, args.region)
        tag_bucket(args.bucket_name, tags)
    except ClientError:
        sys.exit(1)


if __name__ == "__main__":
    main()
