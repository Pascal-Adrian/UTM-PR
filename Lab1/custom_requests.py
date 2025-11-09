import socket
import ssl
import re


class HTTPResponse:
    def __init__(self, headers, body):
        self.status_code = int(headers.split(" ")[1])
        self.headers = headers
        self.body = body
        self.text = self.body

    def __str__(self):
        return f"{self.headers}\r\n\r\n{self.body}"


def http_get(url, max_redirects=5):
    redirect_count = 0
    while redirect_count < max_redirects:
        # Determine if the URL uses HTTP or HTTPS
        if url.startswith("https://"):
            protocol = "https"
            default_port = 443
            url = url[len("https://"):]
        elif url.startswith("http://"):
            protocol = "http"
            default_port = 80
            url = url[len("http://"):]
        else:
            raise ValueError("Only 'http' and 'https' protocols are supported.")

        # Separate the host and path
        if "/" in url:
            host, path = url.split("/", 1)
            path = "/" + path
        else:
            host = url
            path = "/"

        # Prepare the request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # For HTTPS, wrap the socket with SSL
            if protocol == "https":
                context = ssl.create_default_context()
                context.check_hostname = False  # For hostname validation
                context.verify_mode = ssl.CERT_NONE
                with context.wrap_socket(s, server_hostname=host) as ssl_socket:
                    # Connect to the server on port 443 (HTTPS)
                    ssl_socket.connect((host, default_port))

                    # Send the HTTP request
                    ssl_socket.sendall(request.encode('utf-8'))

                    # Receive the response data
                    response = b""
                    while True:
                        chunk = ssl_socket.recv(4096)
                        if not chunk:
                            break
                        response += chunk
            else:
                # For HTTP, connect to the server on port 80
                s.connect((host, default_port))

                # Send the HTTP request
                s.sendall(request.encode('utf-8'))

                # Receive the response data
                response = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk

        # Decode the response from bytes to a string
        response = response.decode('utf-8')

        # Separate the headers from the body
        headers, body = response.split("\r\n\r\n", 1)
        status_line = headers.split("\r\n")[0]
        status_code = int(status_line.split(" ")[1])

        # Check if we received a redirect response (status code 3xx)
        if 300 <= status_code < 400:
            # Find the "Location" header
            location_match = re.search(r"Location: (.+)\r\n", headers)
            if location_match:
                new_url = location_match.group(1).strip()
                print(f"[redirect] Redirecting to: {protocol}://{host}{new_url}")
                # Handle relative redirects
                if new_url.startswith("/"):
                    new_url = f"{protocol}://{host}{new_url}"
                elif not new_url.startswith("http"):
                    new_url = f"{protocol}://{host}/{new_url}"
                url = new_url
                redirect_count += 1
                continue  # Follow the redirect
            else:
                print(f"[request error] Redirect status code received but no 'Location' header found.")
                raise RuntimeError("Redirect status code received but no 'Location' header found.")
        else:
            # No redirect, return the headers and body
            return HTTPResponse(headers, body)

    raise RuntimeError("Max redirects exceeded.")