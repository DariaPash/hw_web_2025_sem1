"""
Simple dynamic WSGI application for performance testing.
Returns a response similar in size to static files for fair comparison.
"""

def application(environ, start_response):
    """Dynamic WSGI application that returns HTML content"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dynamic Content</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Dynamic Content</h1>
        <p>This is a dynamically generated response from a WSGI application.</p>
        <p>This content is generated on each request, unlike static files.</p>
        <p>Timestamp: """ + str(environ.get('REQUEST_TIME', '')) + """</p>
        <p>Path: """ + environ.get('PATH_INFO', '/') + """</p>
    </div>
</body>
</html>"""
    
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, response_headers)
    return [html.encode('utf-8')]
