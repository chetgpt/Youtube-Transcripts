import cv2
import os
import numpy as np
import speech_recognition as sr
from moviepy.editor import AudioFileClip
from pytube import Playlist, YouTube

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def stitch_images(images, rows, cols):
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

def save_frame(frame, scene_index, base_path):
    scene_folder = os.path.join(base_path, "detected_scenes")
    create_directory(scene_folder)
    cv2.imwrite(os.path.join(scene_folder, f"scene_{scene_index}.jpg"), frame)
    print(f"Saved scene {scene_index} in {scene_folder}")

def transcribe_audio(video_path, base_path):
    create_directory(base_path)
    audio = AudioFileClip(video_path)
    audio_file_path = os.path.join(base_path, "temp_audio.wav")
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
    transcription_file_path = os.path.join(base_path, "transcription.txt")
    with open(transcription_file_path, "w") as file:
        file.write(transcription)
    print(f"Transcription saved to '{transcription_file_path}'")

def detect_cuts_and_create_storyboard(video_path, change_threshold=375000, frame_check_interval=30):
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

def process_video(video_path):
    print(f"Processing video: {video_path}")
    base_path = os.path.splitext(os.path.basename(video_path))[0]
    create_directory(base_path)
    scene_images = detect_cuts_and_create_storyboard(video_path)
    for index, scene in enumerate(scene_images):
        save_frame(scene, index, base_path)
    if scene_images:
        rows, cols = 5, 4
        storyboard = stitch_images(scene_images, rows, cols)
        if storyboard is not None:
            storyboard_path = os.path.join(base_path, "storyboard.jpg")
            cv2.imwrite(storyboard_path, storyboard)
            print(f"Storyboard saved to '{storyboard_path}'")
        else:
            print("No valid scenes detected for storyboard.")
    else:
        print("No scenes detected.")
    transcribe_audio(video_path, base_path)

def main():
    playlist_url = 'https://youtube.com/playlist?list=PLljiqTkDjp_G5nGHxAPRttwBZ7BhELVa7&si=gsQl_Q5_QRjB8lyh'  # Change this to your playlist URL
    download_path = 'downloaded_videos'
    video_paths = download_videos_from_playlist(playlist_url, download_path)
    for video_path in video_paths:
        process_video(video_path)
    # Optionally, clean up downloaded files after processing
    # for video_path in video_paths:
    #     os.remove(video_path)

if __name__ == "__main__":
    main()
