import cv2
import os
import numpy as np
from moviepy.editor import *
import tkinter as tk
from tkinter import filedialog

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

def save_frame(frame, scene_index):
    scene_folder = "detected_scenes"
    create_directory(scene_folder)
    cv2.imwrite(os.path.join(scene_folder, f"scene_{scene_index}.jpg"), frame)
    print(f"Saved scene {scene_index}")

def detect_cuts_and_create_storyboard(video_path, change_threshold=750000, frame_check_interval=30):
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

def process_video(video_path):
    print(f"Processing video: {video_path}")
    scene_images = detect_cuts_and_create_storyboard(video_path)
    if scene_images:
        rows, cols = 5, 4  # Adjust grid size as needed
        storyboard = stitch_images(scene_images, rows, cols)
        if storyboard is not None:
            cv2.imwrite(f"storyboard_{os.path.basename(video_path)}.jpg", storyboard)
            print(f"Storyboard saved for '{os.path.basename(video_path)}'")
        else:
            print("No valid scenes detected for storyboard.")
    else:
        print("No scenes detected.")

def main():
    root = tk.Tk()
    root.withdraw()
    video_paths = filedialog.askopenfilenames()

    if video_paths:
        for video_path in video_paths:
            process_video(video_path)
    else:
        print("No video file selected.")

if __name__ == "__main__":
    main()
