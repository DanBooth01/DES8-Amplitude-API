import boto3
import os
import logging

logger = logging.getLogger(__name__)


def load_to_S3(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME):


    s3_client = boto3.client(
        's3',
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    )


    #List all items in S3 bucket
    objects = s3_client.list_objects_v2(Bucket= AWS_BUCKET_NAME)

    files_in_bucket= []

    for obj in objects['Contents']:
        files_in_bucket.append(obj['Key'])


    #Upload files that aren't in s3 bucket:
    files_to_upload = os.listdir('data')

    for file in files_to_upload:
        file_to_upload = f'data/{file}'
        filename_s3 = file
        if file not in objects['Contents']:
            try:
                s3_client.upload_file(file_to_upload, AWS_BUCKET_NAME, filename_s3)
                print(f'{file} uploaded successfully')
                logger.info(f'{file} uploaded successfully')
                os.remove(file_to_upload)
            except Exception as e:
                print(f'An error has occured: {e}')
                logger.error(f'An error has occured: {e}')
        else:
            print(f"{file} has already been uploaded")
            logger.info(f"{file} has already been uploaded")
