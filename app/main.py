#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import flask, requests, time, json, os, warnings, re,logging
from datetime import datetime
from flask import request
from flask import send_file
from auth import *
from upload_class import *
from download_class import *
from minio_funcs import *
from metadata import *
from utils import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)

ORS_URL = os.environ.get("ORS_URL", "http://localhost:80/")
MINIO_URL = os.environ.get("MINIO_URL", "localhost:9000")
MINIO_SECRET = os.environ.get("MINIO_SECRET")
MINIO_KEY = os.environ.get("MINIO_KEY")
TESTING = os.environ.get("NO_AUTH",False)
EVI_PREFIX = 'evi:'

app.url_map.converters['everything'] = EverythingConverter

@app.route('/data/<everything:ark>',methods = ['POST','GET','DELETE','PUT'])
@user_level_permission
def all(ark):

    logger.info('Object Service handling request %s', request)

    if flask.request.method == 'POST':
        accept = request.headers.getlist('accept')

        if not valid_ark(ark):
            logger.info('Given bad ark: ' + str(ark))
            return flask.jsonify({'uploaded':False,"Error":'Invalid ARK'}),400

        error, valid_inputs = correct_inputs(request)
        if not valid_inputs:
            logger.info('Given bad Inputs')
            return flask.jsonify({'uploaded':False,"Error":error}),400

        #Create Main Upload Class From Request
        try:
            upload = Upload(request)
        except:
            logger.info('Metadata must be json.')
            return flask.jsonify({'uploaded':False,"Error":"Metadata must be json"}),400

        #Match sha256 here
        #upload.confirm_sha()

        logger.info('Minting Distribution ID for: %s', ark)
        success = upload.mint_distribution()
        if not success:
            return flask.jsonify({'uploaded':False,
                        'error':'Failed Minting Ids'}),503

        logger.info('Uploading file for: %s', ark)
        try:
            upload.upload(ark)
        except:
            logger.error('Failed to upload file for ark: %s',ark)
            return flask.jsonify({'uploaded':False,
                                        'error':error}),503



        return flask.jsonify({'uploaded':True,
                            'distribution_id':upload.dist_id})

    if flask.request.method == 'GET':

        if not valid_ark(ark):
            return flask.jsonify({"error":"Improperly formatted Identifier"}), 400

        token = request.headers.get("Authorization")
        metadata = retrieve_metadata(ark,token)

        if not valid_meta(metadata):
            return flask.jsonify({'error':'Given Ark missing distribution or is not a distribution.'}),400

        try:
            download = Download(metadata,token)
        except:
            return flask.jsonify({'error':"Given ark is not a download or is missing distribution"}),400
        if not download.valid:
            return flask.jsonify({'error':download.error})

        download_location = download.download()

        result = send_file(download_location)
        os.remove(download_location)

        return result

    if flask.request.method == 'DELETE':

        if not valid_ark(ark):
            return flask.jsonify({"error":"Improperly formatted Identifier"}), 400

        token = request.headers.get("Authorization")

        ark_meta = retrieve_metadata(ark,token)
        if ark_meta.get('@type') != 'Download':
            return flask.jsonify({'deleted':False,'error':'Must pass specific distribution to delete.'})

        minio_loc = ark_meta.get('name')
        bucket = minio_loc.split('/')[0]
        location = '/'.join(minio_loc.split('/')[1:])
        try:
            delete = delete_object(bucket,location)
            if not delete:
                return flask.jsonify({'deleted':False,'error':'Failed to delete.'}),500
        except:
            return flask.jsonify({'deleted':False,'error':'Failed to delete.'}),500
        try:
            delete_id = delete_identifer(ark,token)
        except:
            logger.error('Deleted file but failed to delete distribution id: %s', ark)
            return return flask.jsonify({'deleted':True,'error':'Failed to delete id.'}),200
        return  flask.jsonify('deleted':True)

    if flask.request.method == 'PUT':

        if not valid_ark(ark):
            return flask.jsonify({"error":"Improperly formatted Identifier"}), 400

        token = request.headers.get("Authorization")
        error, valid_inputs = correct_inputs(request)
        if not valid_inputs:
            return flask.jsonify({'uploaded':False,"Error":error}),400

        #Create Main Upload Class From Request
        upload = Upload(request)

        #Match sha256 here
        #upload.confirm_sha()

        logger.info('Minting Distribution ID for: %s', ark)
        success = upload.mint_distribution()
        if not success:
            return flask.jsonify({'uploaded':False,
                        'error':'Failed Minting Ids'}),503

        logger.info('Uploading file for: %s', ark)
        try:
            success, error = upload.upload(ark)
        except:
            logger.error('Failed to upload file for ark: %s',ark)
            return flask.jsonify({'uploaded':False,
                                        'error':error}),503

        success = upload.update_distribution()

        if success:
            return flask.jsonify({'uploaded':True,
                                    'distribution_id':upload.dist_id})
        else:
            logger.error('Failed update distribution for id: %s',upload.dist_id)
            # while True:
            #     success = upload.update_distribution()
            #     if success:
            #         break
            return flask.jsonify({'uploaded':True,
                                    'distribution_id':upload.dist_id})

if __name__ == "__main__":
    if TESTING:
        app.config['TESTING'] = True
    app.run(host='0.0.0.0',port=5005)
