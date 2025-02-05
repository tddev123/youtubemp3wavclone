import os
import yt_dlp
import streamlit as st
import subprocess

# Define the download function
def download_video(url, format_choice):
    download_folder = 'downloads/'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)  # Create the folder if it doesn't exist

    if format_choice.lower() == 'mp4':
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download both video and audio
            'merge_output_format': 'mp4',  # Merge into mp4 format
            'ffmpeg_location': '/usr/bin/ffmpeg',  # Path to FFmpeg
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),  # Save to 'downloads' folder
        }
    elif format_choice.lower() == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),  # Save to 'downloads' folder
        }
    else:
        return "Invalid format choice. Please choose 'mp4' or 'mp3'."

    try:
        # Download video or audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            #st.write(f"File downloaded to: {filename}")
            return filename  # Return the saved filename
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit UI
st.set_page_config(page_title="YouTube Video & Audio Downloader", layout="centered")
st.image("https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png", width=100)
st.title("YouTube Video Downloader")

st.markdown("""
This application allows you to download videos from YouTube in various formats. 
Simply enter the URL of the video you want to download, select the desired format, 
and click the download button. Enjoy your favorite content offline!
""")

# Input and fetch video URL
video_url = st.text_input("Enter the YouTube video URL:")

format_choice = st.selectbox("Select the format:", ["mp4", "mp3"])


# Button for downloading and providing the download link
if st.button("Download Video"):
    if video_url:
        with st.spinner("Converting..."):
            result = download_video(video_url, format_choice)
            if result.startswith("An error occurred"):
                st.error(result)
            else:
                # Debug: Print the download location
                st.write(f"Download completed successfully: {result}")

                # Provide a download button for the user to download the file
                file_path = os.path.join('downloads', os.path.basename(result))

                # Check if the file exists and handle .webm to mp3 conversion if needed
                if os.path.exists(file_path):
                    # If the file is in webm format and the user selected mp3
                    if file_path.endswith(".webm") and format_choice == "mp3":
                        # Create the mp3 file path
                        mp3_file_path = file_path.replace(".webm", ".mp3")
                        # Convert .webm to .mp3
                        try:
                            subprocess.run(["/usr/bin/ffmpeg", "-i", file_path, mp3_file_path], check=True)
                            os.remove(file_path)  # Remove the original .webm file
                            file_path = mp3_file_path  # Update the path to the new .mp3 file
                        except subprocess.CalledProcessError as e:
                            st.error(f"Error during conversion: {e}")

                    # Provide the download button
                    with open(file_path, "rb") as file:
                        mime_type = "audio/mpeg" if format_choice == 'mp3' else "video/mp4"
                        st.download_button(
                            label="Click to Download Video",
                            data=file,
                            file_name=os.path.basename(file_path),
                            mime=mime_type
                        )
                else:
                    st.error(f"File not found at path: {file_path}")
    else:
        st.error("Please enter a valid YouTube URL.")

