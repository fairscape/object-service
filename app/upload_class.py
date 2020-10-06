#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from metadata import *
import boto3,json,os,hashlib
from botocore.client import Config
from upload_class import *
from download_class import *
from minio_funcs import *
from metadata import *
from utils import *


MINIO_URL = os.environ.get("MINIO_URL", "minionas.uvadcos.io")
MINIO_SECRET = os.environ.get("MINIO_SECRET")
MINIO_KEY = os.environ.get("MINIO_KEY")
OS_URL = os.environ.get("OS_URL")

class Upload:

    def __init__(self, request):
        '''
        Upload Class has file and metadata about where file
        will be stored.
        '''


        meta = json.loads(request.files['metadata'].read())

        self.file_location = meta['file_location']
        self.bucket = meta['bucket']
        self.file_name = meta['file_name']
        self.given_sha256 = meta['sha256']
        if 'version' in meta.keys():
            self.version = meta['version']
        else:
            self.version = 1

        self.file_data = request.files.getlist('files')[0]
        self.sha256 = get_file_hash(self.file_data)

        self.token = request.headers.get("Authorization")

        self.ns = meta['namespace']

    def mint_distribution(self):


        self.file_data.seek(0, os.SEEK_END)
        size = self.file_data.tell()
        self.file_data.seek(0)
        dist_meta = {
                    "@type":"Download",
                    "contentSize":size,
                    "name":self.bucket + '/' + self.file_location,
                    "fileFormat":self.file_name.split('.')[-1],
                    "hash-sha256":self.sha256,
                    'version':self.version
                }
        print(dist_meta)
        #self.dist_id = 'ark:99999/8553abdb-53e7-4925-962e-0e2c0bdfa269'
        self.dist_id = mint_identifier(dist_meta,self.ns,token = self.token)

        return True

    def upload(self,ark):

        minioClient = boto3.client('s3',
                            endpoint_url=MINIO_URL,
                            aws_access_key_id=MINIO_KEY,
                            aws_secret_access_key=MINIO_SECRET,
                            region_name='us-east-1')

        #If someone else has a file that matches given name and location
        #add ark as front folder
        print(self.file_location)
        if file_location_taken(self.bucket,self.file_location):
            self.file_location = ark.split('/')[-1] + '/' + self.file_location

        minioClient.upload_fileobj(self.file_data,
                            self.bucket, self.file_location)
        return True

    def update_distribution(self):

        new_meta = {
            'contentUrl':OS_URL + self.dist_id,
        }

        url = ORS_URL + self.dist_job
        r = requests.put(url,data = json.dumps(new_meta),
                    headers={"Authorization": self.token})

        if 'updated' in r.json():
            return True

        return False

def get_file_hash(f):

    f.seek(0)

    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: f.read(4096),b""):
        sha256_hash.update(byte_block)
    hash = sha256_hash.hexdigest()

    f.seek(0)

    return hash
