"""
WSGI application that serves static file content for performance testing.
This simulates serving a static file through gunicorn for comparison.
"""

def application(environ, start_response):
    """WSGI application that returns static-like content"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample HTML for Testing</title>
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
        <h1>Sample HTML File</h1>
        <p>This is a sample HTML file for testing nginx static file serving.</p>
        <p>If you can see this page, nginx is correctly configured to serve static files.</p>
        <p>File location: static/sample.html</p>
        <p>Access URL: http://localhost/sample.html</p>
    </div>
</body>
</html>"""
    
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, response_headers)
    return [html.encode('utf-8')]
