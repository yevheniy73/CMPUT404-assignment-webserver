#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2023 Yevhen Kaznovskyi
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        # Parse the incoming HTTP request
        incoming_request = self.data.decode('utf-8').split('\r\n')[0]
        type_of_request = incoming_request.split()[0]
        og_path_request = incoming_request.split()[1]

        # Construct the full path with the root
        path_request = f"./www{og_path_request}"
        mimetype = "text/css" if ".css" in path_request else "text/html"

        # Check for '..' in the path to prevent a directory attack, include small explanation
        if ".." in path_request:
            content = "<h1>404 Not Found</h1><p>The page you are trying to access is not allowed.</p>"
            message = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{content}"
            self.request.sendall(bytearray(message,'utf-8'))
            return

        # Handle redirects
        if (og_path_request.endswith("/") == False) and ("." not in og_path_request[1:]) and (og_path_request != "/"):
            message = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {og_path_request}/\r\nConnection: close\r\n\r\n"
            self.request.sendall(bytearray(message,'utf-8'))
            return
        
        if type_of_request == "GET":
            
            if og_path_request.endswith("/"):
                path_request += "index.html"

            # Check if request is valid and exists
            if os.path.exists(path_request):
                
                # Get the html content
                with open(path_request, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Send a 200 OK with the page content
                message = f"HTTP/1.1 200 OK\r\nContent-Type: {mimetype}\r\nConnection: close\r\n\r\n{content}"
                self.request.sendall(bytearray(message,'utf-8'))
            else:
                # Handle 404 Not Found if request not valid, include small explanation
                content = "<h1>404 Not Found</h1><p>The page you are trying to access does not exist.</p>"
                message = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{content}"
                self.request.sendall(bytearray(message,'utf-8'))
        else:
            # Handle 405 Method Not Allowed if the method is not GET, include small explanation
            content = "<h1>405 Method Not Allowed</h1><p>The method you are attemping to use is not allowed.</p>"
            message = f"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{content}"
            self.request.sendall(bytearray(message,'utf-8'))

        return

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
