from __future__ import print_function
import httplib
import json
import argparse

HOST = "127.0.0.1:5000"
# load the request body
with open('./request.json') as request_file:
    request = json.load(request_file)


with open('./header.json') as header_file:
    header = json.load(header_file)
    # header["Host"] = HOST
parser = argparse.ArgumentParser(description='Test a phrase with Alexa')
parser.add_argument('phrase', type=str, help="Whatever phrase you want to say to Alexa")
args = parser.parse_args()
request["request"]["intent"]["slots"]["All"]["value"] = args.phrase

conn = httplib.HTTPConnection(HOST)

conn.request('POST', "/", json.dumps(request), header)

response = conn.getresponse()
print(response.status, response.read())
