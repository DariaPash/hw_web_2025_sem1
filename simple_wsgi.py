from urllib.parse import parse_qs
import json


def application(environ, start_response):
    
    get_params = {}
    if environ.get('QUERY_STRING'):
        query_string = environ['QUERY_STRING']
        get_params = parse_qs(query_string)
        get_params = {k: v[0] if len(v) == 1 else v for k, v in get_params.items()}
    
    post_params = {}
    if environ.get('REQUEST_METHOD') == 'POST':
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            if content_length > 0:
                post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
                post_params = parse_qs(post_data)
                post_params = {k: v[0] if len(v) == 1 else v for k, v in post_params.items()}
        except (ValueError, KeyError):
            pass
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WSGI Parameters</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .params {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #4CAF50;
            margin: 10px 0;
        }}
        .param-item {{
            margin: 8px 0;
            padding: 5px;
        }}
        .param-key {{
            font-weight: bold;
            color: #2196F3;
        }}
        .param-value {{
            color: #666;
            margin-left: 10px;
        }}
        .empty {{
            color: #999;
            font-style: italic;
        }}
        pre {{
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>WSGI Parameters Display</h1>
        
        <h2>GET Parameters</h2>
        <div class="params">
            {format_params(get_params) if get_params else '<div class="empty">No GET parameters</div>'}
        </div>
        
        <h2>POST Parameters</h2>
        <div class="params">
            {format_params(post_params) if post_params else '<div class="empty">No POST parameters</div>'}
        </div>
        
        <h2>Request Information</h2>
        <div class="params">
            <div class="param-item">
                <span class="param-key">Method:</span>
                <span class="param-value">{environ.get('REQUEST_METHOD', 'N/A')}</span>
            </div>
            <div class="param-item">
                <span class="param-key">Path:</span>
                <span class="param-value">{environ.get('PATH_INFO', 'N/A')}</span>
            </div>
            <div class="param-item">
                <span class="param-key">Query String:</span>
                <span class="param-value">{environ.get('QUERY_STRING', 'N/A')}</span>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, response_headers)
    return [html.encode('utf-8')]


def format_params(params):
    """Format parameters dictionary as HTML"""
    if not params:
        return '<div class="empty">No parameters</div>'
    
    html_parts = []
    for key, value in params.items():
        if isinstance(value, list):
            value_str = ', '.join(str(v) for v in value)
        else:
            value_str = str(value)
        html_parts.append(
            f'<div class="param-item">'
            f'<span class="param-key">{key}:</span>'
            f'<span class="param-value">{value_str}</span>'
            f'</div>'
        )
    return ''.join(html_parts)
