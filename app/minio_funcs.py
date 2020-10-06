#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, requests, hashlib, boto3
from botocore.client import Config

MINIO_URL = os.environ.get("MINIO_URL", "minionas.uvadcos.io")
MINIO_SECRET = os.environ.get("MINIO_SECRET",'test')
MINIO_KEY = os.environ.get("MINIO_KEY",'test')




def download_file(bucket,location):
    file_name = location.split('/')[-1]
    minioClient = boto3.client('s3',
                        endpoint_url=MINIO_URL,
                        aws_access_key_id=MINIO_KEY,
                        aws_secret_access_key=MINIO_SECRET,
                        region_name='us-east-1')
    minioClient.download_file(bucket, location, '/' + file_name)
    return '/' + file_name

def file_location_taken(bucket,location):
    """return the False if no file exsists else True"""
    minioClient = boto3.client('s3',
                        endpoint_url=MINIO_URL,
                        aws_access_key_id=MINIO_KEY,
                        aws_secret_access_key=MINIO_SECRET,
                        region_name='us-east-1')
    response = minioClient.list_objects_v2(
        Bucket=bucket,
        Prefix=location,
    )
    for obj in response.get('Contents', []):
        if obj['Key'] == location:
            return True
    return False

def upload(f,name,bucket,folder = ''):
    #filename = get_filename(file)
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size == 0:
        return {'upload':False,'error':"Empty File"}
    # try:
    minioClient = boto3.client('s3',
                        endpoint_url=MINIO_URL,
                        aws_access_key_id=MINIO_KEY,
                        aws_secret_access_key=MINIO_SECRET,
                        region_name='us-east-1')
    minioClient.upload_fileobj(f,bucket,location)
    # except ResponseError as err:
    #
    #     return {'upload':False}
    #f.save(secure_filename(f.filename))
    return {'upload':True,'location':bucket + location}
