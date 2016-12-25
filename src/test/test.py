from __future__ import print_function
import httplib
import json

HOST = "127.0.0.1:5000"
# load the request body
with open('./request.json') as request_file:
    request = json.load(request_file)
    request = json.dumps(request)

with open('./header.json') as header_file:
    header = json.load(header_file)
    # header["Host"] = HOST

conn = httplib.HTTPConnection(HOST)

conn.request('POST', "/", request, header)

response = conn.getresponse()
print(response.status, response.read())
