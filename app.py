import os
from yt_dlp import YoutubeDL

def download_youtube_to_mp3(url, download_folder='downloads',ffmpeg_path=None):
    # Ensure the download folder exists
    os.makedirs(download_folder, exist_ok=True)

    print("Converting Mp3 Audio \U0001F422");
    
    # Options for downloading
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,  # Make it less verbose
        'noplaylist': True,  # Ensure we download a single video
    }

    # Add ffmpeg_path if provided
    if ffmpeg_path is not None:
        ydl_opts['ffmpeg_location'] = ffmpeg_path
    
    # Download the video as an mp3 file
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print("Download and conversion completed! \U0001F98B ")

def main():
    # Request user input for YouTube URL
    url = input("Please paste the YouTube link: ").strip()
    
    # Request user input for the download directory
    download_folder = input("Please paste the directory where you want to download the MP3 (default is 'downloads'): ").strip()
    
    # Use default directory if none provided
    if not download_folder:
        download_folder = 'downloads'
    
     # Define the ffmpeg path
    ffmpeg_path = 'F:\\ffmpeg'  # Replace with your actual path
    
    # Download and convert the file
    download_youtube_to_mp3(url, download_folder, ffmpeg_path)

if __name__ == "__main__":
    main()
