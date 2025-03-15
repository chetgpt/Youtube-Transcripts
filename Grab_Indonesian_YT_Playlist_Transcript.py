import os
from pytube import Playlist
from youtube_transcript_api import YouTubeTranscriptApi

def get_playlist_video_ids(playlist_url):
    playlist = Playlist(playlist_url)
    return [video.video_id for video in playlist.videos]

def get_transcript(video_id, language_code='en'):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        return transcript
    except Exception as e:
        print(f"An error occurred for video {video_id}: {e}")
        return None

def save_transcript(video_id, transcript, folder_path):
    file_path = os.path.join(folder_path, f"{video_id}.txt")
    with open(file_path, 'w', encoding='utf-8') as file:
        for entry in transcript:
            file.write(entry['text'] + '\n')

# Replace with your playlist URL
playlist_url = 'https://www.youtube.com/watch?v=r0yUhbUc1d0&list=PL3DDSWxr6dSfYpYty0jcxRGfPHfdNJBs_'


# Create a directory for the playlist
playlist_directory = 'Playlist_Transcripts'
if not os.path.exists(playlist_directory):
    os.makedirs(playlist_directory)

# Extract video IDs from the playlist
video_ids = get_playlist_video_ids(playlist_url)

# Fetch transcripts for each video and save to files
for video_id in video_ids:
    transcript = get_transcript(video_id, 'id')
    if transcript:
        save_transcript(video_id, transcript, playlist_directory)
        print(f"Transcript for video {video_id} saved.")
