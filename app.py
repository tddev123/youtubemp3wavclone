import os
import random
from flask import Flask, render_template, request, jsonify, send_file
from views import views
from yt_dlp import YoutubeDL
import tempfile

app = Flask(__name__, template_folder='templates')
app.register_blueprint(views, url_prefix="/")

# Path to the Downloads folder
downloads_path = r'C:/Users/lilbubba/Downloads'

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0'
    ]
    return random.choice(user_agents)

def create_temporary_cookie_file(cookie_content=None):
    """
    Create a temporary cookie file that will be automatically deleted after use.
    
    :param cookie_content: Optional string content for the cookie file
    :return: Path to the temporary cookie file
    """
    try:
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix='.txt')
        
        # If cookie content is provided, write it to the file
        if cookie_content:
            with open(path, 'w') as temp_file:
                temp_file.write(cookie_content)
        
        return path
    except Exception as e:
        print(f"Error creating temporary cookie file: {e}")
        return None

def get_ydl_opts(format, cookie_content=None):
    # Create a temporary cookie file if content is provided
    cookie_path = create_temporary_cookie_file(cookie_content)
    
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '320'
        }],
        'http_headers': {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
        },
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': True,
        'quiet': False,
        'no_warnings': False,
        'verbose': True  # Add verbose output for debugging
    }
    
    # Add cookie file if a path was successfully created
    if cookie_path:
        opts['cookiefile'] = cookie_path
    
    return opts

def download_from_url(url, format, cookie_content=None):
    ydl_opts = get_ydl_opts(format, cookie_content)
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            base, ext = os.path.splitext(file_path)
            file_path = base + f'.{format}'
            title = info_dict.get('title', 'output')
            size = os.path.getsize(file_path)
            file_type = format.upper()
            return file_path, title, size, file_type
        except Exception as e:
            print(f"Download error: {str(e)}")
            raise

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format = data.get('format')
    cookie_content = data.get('cookie_content')  # Optional cookie content
    
    if not url or not format:
        return jsonify({'error': 'No URL or format provided'}), 400
    
    try:
        file_path, title, size, file_type = download_from_url(url, format, cookie_content)
        size_mb = size / (1024 * 1024)
        return jsonify({'file_path': file_path, 'title': title, 'size': size_mb, 'type': file_type}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-file', methods=['GET'])
def download_file():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
