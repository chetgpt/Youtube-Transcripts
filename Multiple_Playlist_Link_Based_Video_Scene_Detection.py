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

def transcribe_audio(video_path, transcription_path):
    """Transcribe audio from a video file."""
    create_directory(transcription_path)
    audio = AudioFileClip(video_path)
    audio_file_path = os.path.join(transcription_path, "temp_audio.wav")
    audio.write_audiofile(audio_file_path)
    recognizer = sr.Recognizer()
    transcription = ""
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            transcription = recognizer.recognize_google(audio_data, language="id-ID")
        except sr.UnknownValueError:
            transcription = "Unable to understand audio"
        except sr.RequestError as e:
            transcription = f"Error: {e}"
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

def download_videos_from_playlist(playlist_url, download_path):
    """Download all videos from a YouTube playlist."""
    playlist = Playlist(playlist_url)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    downloaded_videos = []
    for url in playlist.video_urls:
        print(f"Downloading video from {url}")
        video = YouTube(url)
        stream = video.streams.get_highest_resolution()
        downloaded_video = stream.download(download_path)
        downloaded_videos.append(downloaded_video)
        print(f"Downloaded {downloaded_video}")
    return downloaded_videos

def process_video(video_path, output_base_path):
    """Process a single video file for scene detection, transcription, and creating a storyboard."""
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

def main(playlist_urls, download_path):
    """Process videos from multiple playlist URLs."""
    for playlist_url in playlist_urls:
        print(f"Processing playlist: {playlist_url}")
        video_paths = download_videos_from_playlist(playlist_url, download_path)
        for video_path in video_paths:
            process_video(video_path, download_path)

if __name__ == "__main__":
    playlist_urls = [
        'https://www.youtube.com/watch?v=3hd39ktiEto&list=PLl9n0JUPTcFnsedkRqiWYDI5rXGdIci6i&pp=iAQB',
        # Add more playlist URLs as needed
    ]
    download_path = 'downloaded_videos'
    main(playlist_urls, download_path)