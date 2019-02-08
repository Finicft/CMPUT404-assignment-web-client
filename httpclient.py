#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust and Fangting Chen
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port_path(self,url):
        #code from https://pymotw.com/3/urllib.parse/
        componments = urllib.parse.urlparse(url)
        host = componments.hostname
        port = componments.port
        path = componments.path 
        scheme = componments.scheme
        if port == None:
            if scheme == "http":
                port = 80 
            else: 
                port = 443 
        if path == "":
            path = "/"
        return host,port,path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        headers = self.get_headers(data)
        code = int(headers.split(" ")[1])
        return code

    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]
        headers.split("\r\n")
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        #connect socket
        HOST, PORT, PATH = self.get_host_port_path(url)
        self.connect(HOST, PORT)
        #send request and receive response 
        payload = "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Close\r\n\r\n".format(PATH, HOST)
        self.sendall(payload)
        data = self.recvall()
        #get code and body 
        code = self.get_code(data)
        body = self.get_body(data)
         #close connection
        self.close()
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
         HOST, PORT, PATH = self.get_host_port_path(url)
         self.connect(HOST, PORT)
         content_type = "Content-Type: application/x-www-form-urlencoded"
         content_length = "Content-Length: "
        
         if args == None:
             content_length += str(0) 
         else:
             #encode args
             #code from https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python
             encoded = urllib.parse.urlencode(args)
             content_length += str(len(encoded)) + "\r\n\r\n" + encoded
         close_connection = "Connection: Close"
         payload = "POST {} HTTP/1.1\r\nHost: {}\r\n{}\r\n{}\r\n{}\r\n\r\n".format(PATH, HOST, content_type, content_length, close_connection)
         self.sendall(payload)
         data = self.recvall()
         code = self.get_code(data)
         body = self.get_body(data)
         self.close()
         print(body)
         return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
