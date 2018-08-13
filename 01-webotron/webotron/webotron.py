import boto3
import click

@click.group()
def cli():
	"webotron deploy websites to AWS"
	pass

@click.command('list-buckets')
def list_buckets():
	"List all s3 buckets"
	for bucket in s3.buckets.all():
		print(bucket)


@cli.command('list-buckets')
def list_buckets():
	"List all s3 buckets"
	for bucket in s3.buckets.all():
		print(bucket)

@cli.command('list-bucket-objects')
@click.argument("bucket")
def list_bucket_objects(bucket):
	"List objects in an s3 bucket"
	for obj in s3.Bucket(bucket).objects.all():
		print(obj)
	#pass   -- pass is used to have a function do nothing

session = boto3.Session(profile_name='PythonAutomation')
s3 = session.resource('s3')


if __name__ == '__main__':
	cli()
	#list_buckets()
