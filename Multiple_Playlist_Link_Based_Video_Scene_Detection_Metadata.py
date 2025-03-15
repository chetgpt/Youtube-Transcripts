import cv2
import os
import numpy as np
from moviepy.editor import AudioFileClip
from pytube import Playlist, YouTube
import speech_recognition as sr

def create_directory(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def stitch_images(images, rows, cols):
    """Stitch multiple images into a single image in a grid layout."""
    images = [img for img in images if img is not None and img.size > 0]
    if not images:
        return None
    max_height = max(image.shape[0] for image in images)
    max_width = max(image.shape[1] for image in images)
    stitched_image = np.zeros((max_height * rows, max_width * cols, 3), dtype=np.uint8)
    for i, img in enumerate(images):
        if i >= rows * cols:
            break
        row = i // cols
        col = i % cols
        resized_image = cv2.resize(img, (max_width, max_height))
        stitched_image[row * max_height: (row + 1) * max_height, col * max_width: (col + 1) * max_width, :] = resized_image
    return stitched_image

def save_frame(frame, scene_index, scene_folder):
    """Save a frame to a specified folder."""
    create_directory(scene_folder)
    cv2.imwrite(os.path.join(scene_folder, f"scene_{scene_index}.jpg"), frame)
    print(f"Saved scene {scene_index} in {scene_folder}")

def transcribe_audio(video_path, transcription_path, language="id-ID", timeout=10):
    """Transcribe audio from a video file with increased timeout and error handling."""
    create_directory(transcription_path)
    audio = AudioFileClip(video_path)
    audio_file_path = os.path.join(transcription_path, "temp_audio.wav")
    audio.write_audiofile(audio_file_path)
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            # Increase timeout value from default
            transcription = recognizer.recognize_google(audio_data, language=language, timeout=timeout)
        except sr.UnknownValueError:
            transcription = "Unable to understand audio"
        except sr.RequestError as e:
            transcription = f"Error: {e}"
        except Exception as e:  # Catch any other exceptions, including TimeoutError
            transcription = f"An error occurred: {e}"
    transcription_file_path = os.path.join(transcription_path, "transcription.txt")
    with open(transcription_file_path, "w") as file:
        file.write(transcription)
    print(f"Transcription saved to '{transcription_file_path}'")

def detect_cuts_and_create_storyboard(video_path, change_threshold=375000, frame_check_interval=30):
    """Detect scene cuts and create a storyboard from a video file."""
    cap = cv2.VideoCapture(video_path)
    prev_frame = None
    scene_images = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if cap.get(cv2.CAP_PROP_POS_FRAMES) % frame_check_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, gray)
                non_zero_count = cv2.countNonZero(diff)
                if non_zero_count > change_threshold:
                    scene_images.append(frame)
            prev_frame = gray
    cap.release()
    return scene_images

def fetch_metadata(youtube_video):
    """Fetch metadata from a YouTube video object."""
    metadata = {
        'Title': youtube_video.title,
        'Author': youtube_video.author,
        'Publish Date': str(youtube_video.publish_date),
        'Views': youtube_video.views,
        'Length': youtube_video.length,
        'Description': youtube_video.description,
    }
    return metadata

def save_metadata(metadata, path):
    """Save metadata to a file."""
    metadata_path = os.path.join(path, 'metadata.txt')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")

def download_videos_from_playlist(playlist_url, download_path):
    """Download all videos from a YouTube playlist and return video paths along with YouTube objects."""
    playlist = Playlist(playlist_url)
    create_directory(download_path)
    downloaded_videos = []
    for url in playlist.video_urls:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        video_path = video.download(download_path)
        downloaded_videos.append((video_path, yt))
    return downloaded_videos

def process_video(video_path, yt, output_base_path):
    """Process a single video file including scene detection, transcription, creating a storyboard, and saving metadata."""
    print(f"Processing video: {video_path}")
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_path = os.path.join(output_base_path, video_base_name)
    create_directory(video_output_path)

    # Organize outputs in separate folders
    scene_folder = os.path.join(video_output_path, "scenes")
    storyboard_path = os.path.join(video_output_path, "storyboards")
    transcription_path = os.path.join(video_output_path, "transcriptions")
    create_directory(scene_folder)
    create_directory(storyboard_path)
    create_directory(transcription_path)

    scene_images = detect_cuts_and_create_storyboard(video_path)
    for index, scene in enumerate(scene_images):
        save_frame(scene, index, scene_folder)
    if scene_images:
        rows, cols = 5, 4
        storyboard_image = stitch_images(scene_images, rows, cols)
        if storyboard_image is not None:
            storyboard_image_path = os.path.join(storyboard_path, "storyboard.jpg")
            cv2.imwrite(storyboard_image_path, storyboard_image)
            print(f"Storyboard saved to '{os.path.join(storyboard_path, 'storyboard.jpg')}'")
        else:
            print("No valid scenes detected for storyboard.")
    else:
        print("No scenes detected.")
    transcribe_audio(video_path, transcription_path)

    # Fetch and save metadata
    metadata = fetch_metadata(yt)
    save_metadata(metadata, video_output_path)

def main(playlist_urls, download_path):
    """Process videos from multiple playlist URLs."""
    for playlist_url in playlist_urls:
        print(f"Processing playlist: {playlist_url}")
        videos = download_videos_from_playlist(playlist_url, download_path)
        for video_path, yt in videos:
            process_video(video_path, yt, download_path)

if __name__ == "__main__":
    playlist_urls = [
        'https://www.youtube.com/watch?v=-hmceyP5skg&list=PLl9n0JUPTcFkOMJDZ0jVwZ6lC2yZ1JMIJ&pp=iAQB'
        # Add more playlist URLs as needed
    ]
    download_path = 'downloaded_videos'
    main(playlist_urls, download_path)