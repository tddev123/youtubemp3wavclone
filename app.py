import os
import random
import sys
import browser_cookie3
from flask import Flask, render_template, request, jsonify, send_file
from views import views
from yt_dlp import YoutubeDL
import tempfile
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')
app.register_blueprint(views, url_prefix="/")

# Path to the Downloads folder
downloads_path = r'C:/Users/lilbubba/Downloads'

def extract_youtube_cookies():
    """
    Extract YouTube cookies from available browsers
    
    Attempts to extract cookies from multiple browsers in this order:
    1. Chrome
    2. Firefox
    3. Edge
    4. Safari (on macOS)
    
    :return: List of YouTube-related cookies
    """
    browsers = [
        browser_cookie3.chrome,
        browser_cookie3.firefox,
        browser_cookie3.edge
    ]
    
    # Attempt to extract cookies from different browsers
    for browser_func in browsers:
        try:
            # Extract all cookies from YouTube domain
            cookies = browser_func(domain_name='youtube.com')
            
            # Convert to list of dictionaries
            cookie_list = []
            for cookie in cookies:
                cookie_dict = {
                    'domain': cookie.domain,
                    'name': cookie.name,
                    'value': cookie.value,
                    'path': cookie.path,
                    'expires': int(cookie.expires.timestamp()) if cookie.expires else None,
                    'secure': cookie.secure
                }
                cookie_list.append(cookie_dict)
            
            # If we found cookies, return them
            if cookie_list:
                print(f"Extracted {len(cookie_list)} cookies from {browser_func.__name__}")
                return cookie_list
        
        except Exception as e:
            print(f"Error extracting cookies from {browser_func.__name__}: {e}")
    
    # If no cookies found
    print("No YouTube cookies found in any browser")
    return []

def create_netscape_cookie_file(cookies):
    """
    Create a Netscape-formatted cookie file
    
    :param cookies: List of dictionaries with cookie information
    :return: Path to the temporary cookie file
    """
    try:
        # Netscape cookie file header
        cookie_content = "# Netscape HTTP Cookie File\n"
        
        # Current timestamp as default expiration if not provided
        default_expiration = int((datetime.now() + timedelta(days=30)).timestamp())
        
        for cookie in cookies:
            # Netscape format: 
            # domain \t FLAG \t path \t secure \t expires \t name \t value
            domain = cookie.get('domain', '.youtube.com')
            path = cookie.get('path', '/')
            secure = str(cookie.get('secure', 'FALSE')).upper()
            expires = cookie.get('expires', default_expiration)
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            
            # Ensure no tabs in name or value
            name = name.replace('\t', '_')
            value = value.replace('\t', '_')
            
            cookie_line = f"{domain}\tTRUE\t{path}\t{secure}\t{expires}\t{name}\t{value}\n"
            cookie_content += cookie_line
        
        # Create temporary file
        fd, path = tempfile.mkstemp(suffix='.txt')
        with open(path, 'w') as temp_file:
            temp_file.write(cookie_content)
        
        return path
    except Exception as e:
        print(f"Error creating cookie file: {e}")
        return None

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0'
    ]
    return random.choice(user_agents)

def get_ydl_opts(format, cookie_path=None):
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
        'verbose': True
    }
    
    # Add cookie file if a path was provided
    if cookie_path:
        opts['cookiefile'] = cookie_path
    
    return opts

def download_from_url(url, format, cookies=None):
    # If no cookies provided, try to extract from browsers
    if not cookies:
        cookies = extract_youtube_cookies()
    
    # Create cookie file if cookies are available
    cookie_path = create_netscape_cookie_file(cookies) if cookies else None
    
    # Get YoutubeDL options
    ydl_opts = get_ydl_opts(format, cookie_path)
    
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
    format = data.get('format', 'mp3')
    cookies = data.get('cookies')  # Optional: allow manual cookie passing
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        file_path, title, size, file_type = download_from_url(url, format, cookies)
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
