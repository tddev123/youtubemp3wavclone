from flask import Flask, render_template, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import tempfile

app = Flask(__name__)

# Use a temporary directory for downloads (works on serverless platforms)
downloads_path = tempfile.gettempdir()

def get_ydl_opts(format):
    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '320'
        }],
        # Bypass bot detection with browser-like headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        # Additional options to avoid issues
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
    }

def download_from_url(url, format):
    ydl_opts = get_ydl_opts(format)
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info_dict)
        base, ext = os.path.splitext(file_path)
        file_path = base + f'.{format}'
        title = info_dict.get('title', 'output')
        size = os.path.getsize(file_path)
        file_type = format.upper()
        return file_path, title, size, file_type

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format = data.get('format')
    
    if not url or not format:
        return jsonify({'error': 'Missing URL or format'}), 400

    try:
        file_path, title, size, file_type = download_from_url(url, format)
        size_mb = size / (1024 * 1024)
        return jsonify({
            'file_path': file_path,
            'title': title,
            'size': size_mb,
            'type': file_type
        }), 200
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
