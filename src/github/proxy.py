from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import urllib3
from base64 import b64encode
import socket

from key_manager import GitCredentials

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
        return f"Basic {b64encode(b'{username}:{token}').decode('ascii')}"


    deef 

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
        self.wfile.write(response.data)

    def do_GET(self):
        """
        Get response
        """

        # set the url
        url = f"{self.path}"
        print(url)

        # get the headers
        headers = self.do_HEAD()

        # get response
        response = http.request('GET', url, headers=headers)

        # proxy response
        self.proxy_response(response)

    def do_POST(self):
        """
        Post Response
        """

        # set the url
        url = f"{self.path}"

        # get the string length of the posted content
        content_len = int(self.headers.get('Content-Length', 0))

        # set the username and token
        username = self.headers.get('X-Git-User-Name')
        token = self.headers.get('X-Git-User-Token')

        # read the post content
        post_body = self.rfile.read(content_len)
        
        # modify the headers
        ## CHANGE AUTHORIZATION TO USE DIFFERENT USERNAME/PASSWORD
        ## THAT IS PULLED FROM OBJECT
        headers = {
            "Accept": self.headers.get('Accept'),
            "Accept-Encoding": self.headers.get('Accept-Encoding'),
            "Authorization": self.add_authorization(username, token),
            "Cache-Control": self.headers.get('Cache-Control'),
            "Connection": self.headers.get('Connection'),
            "Content-Encoding": self.headers.get('Content-Encoding'),
            "Content-Type": self.headers.get('Content-Type'),
            "Pragma": self.headers.get('Pragma'),
            "User-Agent": self.headers.get('User-Agent'),
        }

        # create a response
        response = http.request('POST', url, body=post_body, headers=headers)

        # proxy the response
        self.proxy_response(response)

    def do_HEAD(self):
        """
        Provide expected headers
        """

        # set the username and token
        ## WE WANT TO RETRIEVE THIS FROM OUR LIST
        ## CURRENTLY WON'T WORK WITH SSH DEPLOY KEYS
        username = self.headers.get('X-Git-User-Name')
        token = self.headers.get('X-Git-User-Token')

        # setup some headers
        headers = {
            "Accept"          : self.headers.get('Accept'),
            "Authorization"   : self.add_authorization(username, token),
            "Accept-Encoding" : self.headers.get('Accept-Encoding') 
        }
        
        # setup encoding
        headers["Accept-Encoding"] = self.headers.get('Accept-Encoding')

        # return the headers
        return headers

    def do_CONNECT(self):
        """
        Setup connect method
        """

        (ip, _) = self.client_address
        target_ip = self.path.split(":")[0]

        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.wfile.write(f"{self.protocol_version} 200 Connection established\r\n".encode("utf-8"))
            self.wfile.write(f"Proxy-agent: Gitroto Proxy\r\n".encode("utf-8"))
            self.wfile.write("\r\n".encode("utf-8"))
            # try:
                # self._read_write(target, 300)
            # except Exception as err:
                # print(f"Encountered error in writing to socket, error : {err}")
        
        except Exception as err:
            print(f"Failed to setup socket connection, error : {err}")


        finally:
            target.close()
            self.connection.close()

if __name__ == '__main__':

    # setup a server address
    server_address = ('', int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
    print(server_address)
    # setup https server
    httpd = HTTPServer(server_address, GithubProxyServer)
    # run http server as a daemon
    httpd.serve_forever()