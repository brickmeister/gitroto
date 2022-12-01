from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import sys
import urllib3
from base64 import b64encode
import socket
import ssl
import logging

from key_manager_documentdb import GitCredentials

# setup an http pool
http = urllib3.PoolManager()

# setup the git credentials manager
git_credentials = GitCredentials()

class GithubProxyServer(BaseHTTPRequestHandler):
    """
    Class to proxy github requests
    """

    def add_authorization(self, username, token):
        """
        Add an authorization header
        """
        _bytes = bytes(f"{username}:{token}", "ascii")
        return f"Basic {b64encode(_bytes).decode('ascii')}"

    def parse_url(self):
        """
        Parse a url and dynamically change it
        """

        return f"https://github.com{self.path}"

    def proxy_response(self, response):
        """
        Function to proxy a request
        """

        # add a response header
        self.send_response(response.status)
        
        # setup responses
        for header in response.headers:
            if (header.lower() == "transfer-encoding"):
                self.send_header("transfer-encoding", "identity")
            elif (header.lower() == "connection"):
                self.send_header("connection", "close")
            else:
                self.send_header(header, response.headers[header])

        # finish send headers on response
        self.end_headers()

        # write response back to client
        for chunk in response.stream(32):
            self.wfile.write(chunk)

    def do_GET(self):
        """
        Get response
        """

        # set the url
        url = self.parse_url()

        # check if we have a heartbeat request
        if '/_health' in url:
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(b"Heartbeat ping received\n")
        else:
            # get the headers
            headers = self.do_HEAD()

            # get response
            response = http.request('GET', url, headers=headers, preload_content = False)

            # proxy response
            self.proxy_response(response)

            # release the connection
            response.release_conn()

    def do_POST(self):
        """
        Post Response
        """

        # set the url
        url = self.parse_url()

        # get the string length of the posted content
        content_len = int(self.headers.get('Content-Length', 0))

        # set the username and token
        headers = self.do_HEAD()

        # read the post content
        post_body = self.rfile.read(content_len)
        
        # modify the headers
        headers.update({
            "Cache-Control": self.headers.get('Cache-Control') or '*',
            "Connection": self.headers.get('Connection') or '*',
            "Content-Encoding": self.headers.get('Content-Encoding') or '*',
            "Content-Type": self.headers.get('Content-Type') or '*',
            "Pragma": self.headers.get('Pragma') or '*',
            "User-Agent": self.headers.get('User-Agent') or '*',
        })

        # create a response
        response = http.request('POST', url, body=post_body, headers=headers, preload_content = False)

        # proxy the response
        self.proxy_response(response)

        # release the connection
        response.release_conn()


    def do_HEAD(self):
        """
        Provide expected headers
        """

        # set the username and token
        try:
            username = self.headers.get('X-Git-User-Name') or "brickmeister"
            token = git_credentials.get_token(username) or self.headers.get('X-Git-User-Token')
            headers = {
                "Accept"          : self.headers.get('Accept'),
                "Authorization"   : self.add_authorization(username, token),
                "Accept-Encoding" : self.headers.get('Accept-Encoding') or "*"
            }
        except Exception as err:
            logging.warning(f"Failed to get token credentials, error : {err}")
            headers = {"Accept-Encoding" : self.headers.get('Accept-Encoding') or "*"}

        # return the headers
        return headers

if __name__ == '__main__':

    # setup a server address
    server_address = ('', int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
    print(server_address)
    # setup https server
    httpd = HTTPServer(server_address, GithubProxyServer)
    # setup a ssl socket
    # httpd.socket = ssl.wrap_socket(httpd.socket,
    #                                server_side = True,
    #                                ssl_version = ssl.PROTOCOL_TLS,
    #                                certfile = 'localhost.pem')

    # run http server as a daemon
    httpd.serve_forever()