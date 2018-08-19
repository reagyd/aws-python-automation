#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Webotron: Deploy websites with AWS

Webotron automates the process of deploying static websites using AWS
- Configure AWS S3 buckets.
	- Create them
	- Set them up for static website hosting
	- Deploy local files to them
- Configure DNS with route 53
- Configure A content delivery network and SSL with AWS cloudfront.
"""
from pathlib import Path
import mimetypes
import boto3
from botocore.exceptions import ClientError
import click


session = boto3.Session(profile_name='PythonAutomation')
s3 = session.resource('s3')


@click.group()
def cli():
    """webotron deploy websites to AWS."""
    pass


@click.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an s3 bucket."""
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)
	# pass   -- pass is used to have a function do nothing


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure s3."""
    s3_bucket = None

    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={'LocationConstraint': session.region_name}
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise error

    policy = """{
    "Version":"2012-10-17",
    "Statement":[{
    "Sid":"PublicReadGetObject",
    "Effect":"Allow",
    "Principal": "*",
    "Action":["s3:GetObject"],
    "Resource":["arn:aws:s3:::%s/*"
      ]
     }
    ]}
    """ % s3_bucket.name
    policy = policy.strip()
    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    s3_bucket.Website().put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })

    #return


def upload_file(s3_bucket, path, key):
    """Upload path to s3_bucket at key."""
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(

        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        })


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync content of pathname to bucket."""
    s3_bucket = s3.Bucket(bucket)

    root = Path(pathname).expanduser().resolve()
    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir():
                handle_directory(p)
            if p.is_file():
                upload_file(s3_bucket, str(p), str(p.relative_to(root)))


    handle_directory(root)


if __name__ == '__main__':
    cli()
	#list_buckets()
