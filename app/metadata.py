#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import os, requests, json
ORS_URL = os.environ.get("ORS_URL", "http://localhost:80/")

def mint_identifier(meta,ARK_NS,qualifier = False,token=None):

    if qualifier:
        url = ORS_URL + 'ark:' + ARK_NS + '/' + qualifier + '/' + random_alphanumeric_string(30)
    else:
        url = ORS_URL + 'shoulder/ark:' + ARK_NS

    #Create Identifier for each file uploaded
    r = requests.post(
            url,
            data=json.dumps(meta),
            headers={"Authorization": token}
            )

    if 'created' in r.json().keys():
        id = r.json()['created']
        return id

    else:
        print(r.json())
        return 'error'

def retrieve_metadata(ark,token):

    r = requests.get(
        ORS_URL + ark,
        headers={"Authorization": token}
        )

    return r.json()
def delete_identifier(ark,token = None):

    url = ORS_URL + ark
    r = requests.delete(url,headers={"Authorization": token})

    return

def get_minio_location(meta,token):

    if '@type' not in meta.keys():
        return '',''

    if meta.get('@type') == 'DataDownload':

        if 'contentUrl' in meta.keys():
            bucket = meta['contentUrl'].split('/')[0]
            location = '/'.join(meta['contentUrl'][1:])

        else:
            bucket = ''
            location = ''

    elif meta.get('@type') == 'Download':

        if 'name' in meta.keys():
            bucket = meta['url'].split('/')[0]
            location = '/'.join(meta['url'][1:])


        else:
            bucket = ''
            location = ''

    else:

        if 'distribution' in meta.keys():

            if isinstance(meta['distribution'],dict):

                if 'contentUrl' in meta['distribution'].keys():
                    bucket = meta['distribution']['contentUrl'].split('/')[0]
                    location = '/'.join(meta['distribution']['contentUrl'][1:])

                else:
                    if '@id' in meta['distribution'].keys():
                        dist_meta = retrieve_metadata(meta['distribution']['@id'],token)
                        bucket, location = get_minio_location(dist_meta)
                    else:
                        bucket = ''
                        location = ''
        else:
            bucket = ''
            location = ''

    return bucket, location
