#  coding: utf-8 
import socketserver
import os

# Copyright 2023 Charith Pathirathna
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
        # Get the request data
        self.data = self.request.recv(1024).strip()
        self.received_request = self.data.decode('utf-8')
        self.response = ""
        self.content_type = ""
        self.protocol = "HTTP/1.1"
        self.handle_request()
        self.request.sendall(bytearray(self.response, 'utf-8'))
        
    def handle_request(self):
        # If the request is POST/PUT/DELETE or anything other than GET
        if("GET" not in self.received_request):
            self.response += f'{self.protocol} 405 Method Not Allowed\r\n'

        # If the request is GET
        else:
            # Gets the path from the GET request by taking everything from index[4] to
            # index[("HTTP/1.1") -1]
            get_index = self.received_request.index("HTTP/1.1") -1
            path = self.received_request[4:get_index]

            # Test if folder exists
            isExist = os.path.exists("./www/")
            if not (isExist):
                print("Can only serve files in ./www and deeper\n")
                self.handle_not_found()
                return False

            file_path = ("www") + path

            # Test if path exists
            if os.path.exists(file_path):
                # Exceptional case when filename already ends with '/'
                if file_path[-1] == "/" and len(file_path) > 4:
                    file_path[:-1]
                    # Removes trailing '/' and rechecks if path exists
                    if os.path.exists(file_path):
                        self.response += f'{self.protocol} 200 OK\r\n'

                # Path with ./www exists
                else:
                    # Splits the path to get the subdirectories and filename
                    subs = os.path.split(file_path)
                    fname = subs[1]

                    # If at root
                    if fname == "":
                        file_path +=  "index.html"
                        # Test if file exists
                        try:
                            file = open(file_path, 'r')
                        except:
                            # Else, handle not found error
                            self.handle_not_found()
                            return
                        page_body = file.read()
                        self.response += f'{self.protocol} 200 OK\r\n'
                        self.response += f'Content-Type: text/html\r\n\r\n'
                        self.response += f'{page_body}\r\n'
                        
                    else:
                        # Adds trailing '/' to filename
                        fname += "/"
                        # Check if filename contains .html/ at the end
                        if fname[-6:] == ".html/":
                            self.content_type = "text/html"
                        # Else, check if filename contains .css/ at the end
                        elif fname[-5:] == ".css/":
                            self.content_type = "text/css"
                        # Handle moved permanently case
                        else:
                            print("File_path: " + file_path)
                            replaced_path = path[1:]
                            self.response += f'{self.protocol} 301 Moved Permanently\r\n'
                            self.response += f'Location: http://localhost:8080/{replaced_path}/\r\n\r\n'
                            return False

                        # Test if file exists
                        try:
                            file = open(file_path, 'r')
                        except:
                            # Else, handle not found error
                            self.handle_not_found()
                            return False

                        page_body = file.read()
                        self.response += f'{self.protocol} 200 OK\r\n'
                        self.response += f'Content-Type: {self.content_type}\r\n\r\n'
                        self.response += f'{page_body}\r\n'

            # Else, handle not found error
            else: 
                self.handle_not_found()

    # Send the 404 Not Found Response
    def handle_not_found(self):
        self.response += f'{self.protocol} 404 Not Found\r\n'

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()