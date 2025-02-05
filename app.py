from flask import Flask, render_template, request, jsonify, send_file
from views import views
from yt_dlp import YoutubeDL
import os

app = Flask(__name__, template_folder='templates')
app.register_blueprint(views, url_prefix="/")


# Path to the Downloads folder
downloads_path = r'C:/Users/lilbubba/Downloads'

def get_ydl_opts(format):
    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),  # Save to Downloads with video title and correct extension
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '320'
        }],
    }

def download_from_url(url, format):
    ydl_opts = get_ydl_opts(format)
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info_dict)
        base, ext = os.path.splitext(file_path)
        file_path = base + f'.{format}'
        title = info_dict.get('title', 'output')
        size = os.path.getsize(file_path)  # Get file size
        file_type = format.upper()
        return file_path, title, size, file_type

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format = data.get('format')
    if not url or not format:
        return jsonify({'error': 'No URL or format provided'}), 400

    try:
        file_path, title, size, file_type = download_from_url(url, format)
        size_mb = size / (1024 * 1024)  # Convert size to megabytes
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
    



if __name__ == '__main__':
    app.run(debug=True)
    
