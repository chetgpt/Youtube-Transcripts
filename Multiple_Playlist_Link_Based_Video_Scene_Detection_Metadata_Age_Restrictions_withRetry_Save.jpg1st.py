import cv2
import os
import numpy as np
from moviepy.editor import AudioFileClip
from pytube import Playlist, YouTube
from pytube.exceptions import AgeRestrictedError
import speech_recognition as sr
import time

def create_directory(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def stitch_images(images, rows, cols):
    """Stitch multiple images into a single image in a grid layout."""
    if not images:
        print("No images to stitch.")
        return None
    max_height = max(image.shape[0] for image in images)
    max_width = max(image.shape[1] for image in images)
    stitched_image = np.zeros((max_height * rows, max_width * cols, 3), dtype=np.uint8)
    for i, img in enumerate(images):
        if i >= rows * cols:
            break
        row = i // cols
        col = i % cols
        img = cv2.resize(img, (max_width, max_height))
        stitched_image[row * max_height: (row + 1) * max_height, col * max_width: (col + 1) * max_width, :] = img
    return stitched_image

def detect_cuts_and_create_storyboard(video_path, output_base_path, change_threshold=375000, frame_check_interval=30):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    video_base_name = os.path.splitext(os.path.basename(video_path))[0]
    scene_folder = os.path.join(output_base_path, video_base_name, "scenes")
    storyboard_folder = os.path.join(output_base_path, video_base_name, "storyboards")
    create_directory(scene_folder)
    create_directory(storyboard_folder)

    prev_frame = None
    scene_images = []
    scene_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % frame_check_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, gray)
                non_zero_count = np.count_nonzero(diff)
                if non_zero_count > change_threshold:
                    scene_img_path = save_frame(frame, scene_index, scene_folder)
                    if scene_img_path:
                        scene_images.append(cv2.imread(scene_img_path))  # Read the saved image for storyboard
                        scene_index += 1
            prev_frame = gray
    cap.release()

    if scene_images:
        storyboard_image = stitch_images(scene_images, 5, 4)  # Adjust rows and cols as needed
        if storyboard_image is not None:
            storyboard_path = os.path.join(storyboard_folder, "storyboard.jpg")
            if cv2.imwrite(storyboard_path, storyboard_image):
                print(f"Storyboard saved to '{storyboard_path}'")
            else:
                print("Failed to save storyboard image.")
        else:
            print("No valid scenes detected for storyboard.")
    else:
        print("No scenes detected for storyboard creation.")

def save_frame(frame, scene_index, scene_folder):
    """Save a frame to a specified folder."""
    filename = f"scene_{scene_index}.jpg"
    filepath = os.path.join(scene_folder, filename)
    success = cv2.imwrite(filepath, frame)
    if success:
        print(f"Saved scene {scene_index} in {scene_folder}")
        return filepath
    else:
        print(f"Failed to save scene {scene_index} at {filepath}")
        return None
    
def transcribe_audio(video_path, transcription_path, language="en-US", timeout=10):
    """Transcribe audio from a video file."""
    audio = AudioFileClip(video_path)
    audio_file_path = os.path.join(transcription_path, "temp_audio.wav")
    audio.write_audiofile(audio_file_path, verbose=False, logger=None)
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            transcription = recognizer.recognize_google(audio_data, language=language, timeout=timeout)
        except sr.UnknownValueError:
            transcription = "Unable to understand audio"
        except sr.RequestError as e:
            transcription = f"API request error: {e}"
        except Exception as e:
            transcription = f"An error occurred: {e}"
    transcription_file_path = os.path.join(transcription_path, "transcription.txt")
    with open(transcription_file_path, "w") as file:
        file.write(transcription)
    print(f"Transcription saved to '{transcription_file_path}'")

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
    print(f"Metadata saved to '{metadata_path}'")

def download_and_process_video(yt, download_path, output_base_path):
    """Download a video and then process it."""
    try:
        video = yt.streams.get_highest_resolution()
        video_path = video.download(download_path)
        print(f"Downloaded video {yt.title} to {video_path}")
        process_video(video_path, yt, output_base_path)
    except Exception as e:
        print(f"Failed to download video {yt.watch_url}: {e}")

def download_videos_from_playlist(playlist_url, download_path, output_base_path):
    """Download all videos from a YouTube playlist and process each immediately after downloading."""
    playlist = Playlist(playlist_url)
    create_directory(download_path)
    for url in playlist.video_urls:
        try:
            yt = YouTube(url)
            download_and_process_video(yt, download_path, output_base_path)
        except AgeRestrictedError as e:
            print(f"Video {url} is age restricted and cannot be downloaded. Skipping.")
        except Exception as e:
            print(f"Failed to download video {url}: {e}")

def process_video(video_path, yt, output_base_path):
    """Process a single video file including scene detection, transcription, creating a storyboard, and saving metadata."""
    print(f"Processing video: {video_path}")
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_path = os.path.join(output_base_path, video_base_name)
    create_directory(video_output_path)

    detect_cuts_and_create_storyboard(video_path, video_output_path)
    transcribe_audio(video_path, video_output_path)

    # Fetch and save metadata
    metadata = fetch_metadata(yt)
    save_metadata(metadata, video_output_path)

def main(playlist_urls, download_path, output_base_path):
    """Process videos from multiple playlist URLs."""
    for playlist_url in playlist_urls:
        print(f"Processing playlist: {playlist_url}")
        download_videos_from_playlist(playlist_url, download_path, output_base_path)

if __name__ == "__main__":
    playlist_urls = ['https://www.youtube.com/watch?v=yrMU7-jBXFY&list=PLljiqTkDjp_FUM_jys4wpWwrYpeSBzIeo',
                     'https://www.youtube.com/watch?v=aMF9LtoGPkE&list=PLJIrOVqO5Wt60v55SRSHDOhVXlnefQSAu',
                     'https://www.youtube.com/watch?v=GbkTnv80W9g&list=PL3rbcosMQHB4_U8ftCiuZzIcvFoe-BsT3',
                     'https://www.youtube.com/watch?v=-hmceyP5skg&list=PLl9n0JUPTcFkOMJDZ0jVwZ6lC2yZ1JMIJ',
                     'https://www.youtube.com/watch?v=3hd39ktiEto&list=PLl9n0JUPTcFnsedkRqiWYDI5rXGdIci6i',
                     'https://www.youtube.com/watch?v=ceRozhN_-cw&list=PLjeMXrn7uT6aReobWlRF5SjROAz7LPAWp',
                     'https://www.youtube.com/watch?v=GM5ohGeSIk0&list=PLjeMXrn7uT6ZGNN6TbkVQKA_5hVcjZaw-',
                     'https://www.youtube.com/watch?v=2eUGGQUkLbQ&list=PLl9n0JUPTcFkpK-sDGGe6RQdjcKVFwfel',
                     'https://www.youtube.com/watch?v=qaAm84TMyBE&list=PLl9n0JUPTcFkwuT7waa7xmU9EzNSQl3Um',
                     'https://www.youtube.com/watch?v=0Rp_w2IPRaI&list=PLmOCail1XBUSjgW2Jn37C5opBTYe46Jae',
                     'https://www.youtube.com/watch?v=FF9l4uIGzu4&list=PLl9n0JUPTcFmlYA4LrYirWoV96CENMUtH',
                     'https://www.youtube.com/watch?v=qWg8CHhh6r8&list=PL2x_VKrjVD2GkupA87GfVIWBflcThT2CR',
                     'https://www.youtube.com/watch?v=TT8fQtgp4Ps&list=PLuZsv6Jyxgn1qtSIURq2l5AXujPeTvGbU',
                     'https://www.youtube.com/watch?v=vqQC7AtOEoA&list=PLLnTVkuYaCFi0im8sE85fl9Lb0eKMlC2c',
                     'https://www.youtube.com/watch?v=7zviestzCmg&list=PLn1k-Nt38W0ADIg4t8MoRnb_N55Unb7Kr',
                     'https://www.youtube.com/watch?v=DvHvOHynyZg&list=PLN1lZSRohwRZ-G6Raqyxwf1P65IWWQchw',
                     'https://www.youtube.com/watch?v=kwnb41HQopo&list=PL3rbcosMQHB7TmqtuGoJSD9Zdq15hp001',
                     'https://www.youtube.com/watch?v=WXiaFCNdFwM&list=PLl9n0JUPTcFl7uw62zZrgsUmglc8UVMkZ',
                     'https://www.youtube.com/watch?v=mVwfkBsN-Xg&list=PLl9n0JUPTcFlen_AMvLPhJbPXRYmLVcgH',
                     'https://www.youtube.com/watch?v=35B1MmX44o8&list=PL3rbcosMQHB76Uy8cV0VUQa3znQSZUB20',
                     'https://www.youtube.com/watch?v=4CTuDYxLwY0&list=PL99esZ5KArfjN0osi0CAUTbYhyKAZGCb5',
                     'https://www.youtube.com/watch?v=LlGO5zztBiA&list=PL3rbcosMQHB4nDUz5clUZv8upax2KwPrg',
                     'https://www.youtube.com/watch?v=iTt41yQn3t0&list=PLl9n0JUPTcFlCYmKF9M0rQ7O1EvcGODx0',
                     'https://www.youtube.com/watch?v=ptj3JPr3fwY&list=PLToalcF88BjXlrkOorfF-Vy6sF8xcPFob',
                     'https://www.youtube.com/watch?v=odMYkXeygJ4&list=PLCDHSh8UvqbOVN9wOu4c8yLesVFXef4vh',
                     'https://www.youtube.com/watch?v=jg4J-B0O6yU&list=PLe8L00sAPqRIJKeCgz9vnMPAOimqiMZuA',
                     'https://www.youtube.com/watch?v=S4TMRVju11o&list=PLl9n0JUPTcFkcw7AfDT_9gLlCZIHzvwx0',
                     'https://www.youtube.com/watch?v=mA8lrcDJPjM&list=PLpt2u02rNjDBRo9bRd57FdY-9VVENYemT',
                     'https://www.youtube.com/watch?v=a1ZikTy8H2Y&list=PLl9n0JUPTcFklDuIgGOINdG_XptNoGE5l'
    ]
    download_path = 'downloaded,_videos'
    output_base_path = 'processed_videos'
    main(playlist_urls, download_path, output_base_path)

