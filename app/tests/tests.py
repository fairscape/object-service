#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import unittest, sys, requests, json,io
sys.path.append(".")
from upload_class import *
from download_class import *
from utils import *
import main

# class test_Dist_class(unittest.TestCase):
#
#     def test_old_dist(self):
#
#         meta = {'@type':'DataDownload',
#         }
#
#         eg = up.build_evidence_graph(data)
#
#         with open('./Tests/result.json','r') as f:
#             should_be = json.load(f)
#
#         self.assertEqual(eg,should_be)


class test_app(unittest.TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()


    def test_upload_good(self):


        metadata = {
                    "@context":{
                        "@vocab":"http://schema.org/"
                    },
                    "@type":"Dataset",
                    "folder":"Test",
                    "name":"Test Dataset",
                    "description":"Spark Test Data Set",
                    "author":[
                        {
                            "name":"Justin Niestroy",
                            "@id": "https://orcid.org/0000-0002-1103-3882",
                            "affiliation":"University of Virginia"
                        }
                    ],
                }

        data = {}
        data['fil'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        data['metadata'] = (io.BytesIO(json.dumps(metadata).encode('utf-8')),'name')
        req = self.app.post('/data/ark:99999/123',data = data,content_type='multipart/form-data')

        self.assertEqual(req.status_code,400)

    def test_upload_missing_meta(self):


        metadata = {
                    "@context":{
                        "@vocab":"http://schema.org/"
                    },
                    "@type":"Dataset",
                    "folder":"Test",
                    "name":"Test Dataset",
                    "description":"Spark Test Data Set",
                    "author":[
                        {
                            "name":"Justin Niestroy",
                            "@id": "https://orcid.org/0000-0002-1103-3882",
                            "affiliation":"University of Virginia"
                        }
                    ],
                }

        data = {}
        data['files'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        #data['metadata'] = (io.BytesIO(json.dumps(metadata).encode('utf-8')),'name')
        req = self.app.post('/data/ark:99999/123',data = data,content_type='multipart/form-data')

        self.assertEqual(req.status_code,400)

    def test_upload_invalid_meta(self):


        metadata = {
                    "@context":{
                        "@vocab":"http://schema.org/"
                    },
                    "@type":"Dataset",
                    "folder":"Test",
                    "name":"Test Dataset",
                    "description":"Spark Test Data Set",
                    "author":[
                        {
                            "name":"Justin Niestroy",
                            "@id": "https://orcid.org/0000-0002-1103-3882",
                            "affiliation":"University of Virginia"
                        }
                    ],
                }

        data = {}
        data['files'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        data['metadata'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        req = self.app.post('/data/ark:99999/123',data = data,content_type='multipart/form-data')

        self.assertEqual(req.status_code,400)

    def test_upload_missing_files(self):


        metadata = {
                    "@context":{
                        "@vocab":"http://schema.org/"
                    },
                    "@type":"Dataset",
                    "folder":"Test",
                    "name":"Test Dataset",
                    "description":"Spark Test Data Set",
                    "author":[
                        {
                            "name":"Justin Niestroy",
                            "@id": "https://orcid.org/0000-0002-1103-3882",
                            "affiliation":"University of Virginia"
                        }
                    ],
                }

        data = {}
        #data['files'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        data['metadata'] = (io.BytesIO(json.dumps(metadata).encode('utf-8')),'name')
        req = self.app.post('/data/ark:99999/123',data = data,content_type='multipart/form-data')

        self.assertEqual(req.status_code,400)

    def test_upload_invalid_ark(self):


        metadata = {
                    "@context":{
                        "@vocab":"http://schema.org/"
                    },
                    "@type":"Dataset",
                    "folder":"Test",
                    "name":"Test Dataset",
                    "description":"Spark Test Data Set",
                    "author":[
                        {
                            "name":"Justin Niestroy",
                            "@id": "https://orcid.org/0000-0002-1103-3882",
                            "affiliation":"University of Virginia"
                        }
                    ],
                }

        data = {}
        #data['files'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        data['metadata'] = (io.BytesIO(json.dumps(metadata).encode('utf-8')),'name')
        req = self.app.post('/data/15dr',data = data,content_type='multipart/form-data')

        self.assertEqual(req.json['Error'],'Invalid ARK')



if __name__ == '__main__':
    unittest.main()
