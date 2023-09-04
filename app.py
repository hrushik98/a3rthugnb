import streamlit as st
import os
import shutil
import re
from pytube import YouTube, Search
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import zipfile

# Function to reset the "music" folder
def reset():
    if os.path.exists("music"):

        shutil.rmtree("music")
    # Create a directory named "music"
        os.makedirs("music")
    else:
        os.makedirs("music")

def mp3_downloader(link):
    text = f"{link}"

    # Use regex to find the first match in the text
    match = re.search(r'https://(?:www\.)?youtube\.com/watch\?v=([\w-]+)', text)

    # Check if a match was found
    if match:
        # Extract the YouTube video ID from the match
        youtube_video_id = match.group(1)

        # Construct the full YouTube URL using the extracted video ID
        youtube_full_url = f'https://youtube.com/watch?v={youtube_video_id}'
    else:
        st.error("No YouTube URL found in the text.")

    # url input from user
    yt = YouTube(str(youtube_full_url))

    # extract only audio
    video = yt.streams.filter(only_audio=True).first()

    # check for destination to save file
    destination = "music"

    # download the file
    out_file = video.download(output_path=destination)

    # save the file
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)

    # result of success
    st.success(yt.title + " has been successfully downloaded.")

def download(spotify_link):
    url = f"{spotify_link}"
    match = re.search(r'playlist\/([^?]+)', url)
    match = match.group(1)

    # Replace with your client ID and client secret
    client_id = '8f0fc1b5b42146ecab4ac461a515ff74'
    client_secret = '111b3ef11abd4859a5989e44ce2e0fd3'

    # Initialize the Spotify client credentials manager
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    # Create a Spotify client
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Replace 'spotify:playlist:78uOvPEsvzhWbhuTtxLmDB' with the URI of your playlist
    playlist_uri = f'spotify:playlist:{match}'

    # Fetch the playlist data
    playlist = sp.playlist_tracks(playlist_uri)

    # Initialize an empty array to store song titles and artist names
    music = []

    # Extract and append song titles and artist names to the 'music' array
    for track in playlist['items']:
        track_name = track['track']['name']
        artist_names = [artist['name'] for artist in track['track']['artists']]
        artist_name = ', '.join(artist_names)
        music.append(f"{track_name} - {artist_name}")

    music_links = []
    for item in music:
        s = Search(f'{item}')
        for v in s.results:
            music_links.append(f"{v.title}: {v.watch_url}")
            break

    failed = []
    for link in music_links:
        try:
            mp3_downloader(link)
        except:
            failed.append(link)
            continue

    if os.path.exists("music"):
        # Define the directory to zip
        directory_to_zip = "music"

        # Define the name of the zip file
        zip_file_name = "music.zip"

        # Create a zip file
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_to_zip):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, directory_to_zip)
                    zipf.write(file_path, arcname=arcname)

        st.success(f"🎉 Successful! Created {playlist_name}_playlist")
        if failed:
            st.warning("We couldn't download these files:")
            st.write(failed)

        # Add a "Download Zip" button to download the zip file
        with open("music.zip", "rb") as fp:
            btn = st.download_button(
                label="Download ZIP",
                data=fp,
                file_name=f"{playlist_name}.zip"
            )

st.title("Spotify Pirate 🏴‍☠️")

# Create a hyperlink to your GitHub profile
github_url = "https://github.com/hrushik98"
github_text = "created by @hrushik98"

# Display the hyperlink
st.markdown(f"**[ {github_text} ]({github_url})**")

playlist_name = st.text_input("Enter your playlist name")
playlist_link = st.text_input("Enter your playlist link")

if st.button("Download"):
    reset()
    download(f"{playlist_link}")
