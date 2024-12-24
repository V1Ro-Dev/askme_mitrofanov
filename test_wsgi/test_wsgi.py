from cgi import parse

HELLO_WORLD = b"Hello world!\n"


def simple_app(environ, start_response):

    method = environ['REQUEST_METHOD']
    print(environ)

    params = environ['QUERY_STRING']
    body = {}
    if method == "POST":
        body = environ['wsgi.input'].read(int(environ.get("CONTENT_LENGTH", 0)))
        body = body.decode()

    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    response = f"Method: {method}, params: {params}, body: {body}".encode("utf-8")
    return [response]


application = simple_app