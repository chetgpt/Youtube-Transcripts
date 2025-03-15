# CHETGPT: It's a compilation of codes that can perform the tasks described below.

# BY CHATGPT:

## 📌 Overview
This repository contains **Python scripts for video processing, scene detection, transcription, and YouTube playlist downloading**. These tools leverage **OpenCV, MoviePy, SpeechRecognition, and Pytube** for video analysis and metadata extraction.

## 🚀 Features
- **🎞️ Scene Detection & Storyboard Generation**
  - Detects **scene changes** in videos using **frame difference analysis**.
  - Generates **storyboard images** summarizing key frames.
- **📜 Speech-to-Text Transcription**
  - Extracts **audio from videos** and converts it into text using **Google Speech Recognition**.
- **📥 YouTube Playlist Downloading**
  - Downloads full YouTube playlists while **handling age restrictions**.
  - Supports **HD video downloads** and metadata extraction.
- **📊 Video Metadata Extraction**
  - Fetches video **title, author, publish date, views, length, and description**.

## 📦 Dependencies
Install required libraries using:
```bash
pip install opencv-python moviepy speechrecognition pytube numpy tkinter
```

## 🛠 How to Use
### 🎬 **Process Local Videos**
1. Run the scene detection and transcription script:
   ```bash
   python Bulk_FIle_Based_Video_Scene_Detection.py
   ```
2. Select **video files** for processing.
3. Outputs:
   - **Detected scenes** stored in `/detected_scenes/`.
   - **Storyboards** saved as `.jpg`.
   - **Transcriptions** saved as `.txt`.

### 📥 **Download & Process YouTube Playlists**
1. Run the YouTube downloader & scene detection script:
   ```bash
   python Multiple_Playlist_Link_Based_Video_Scene_Detection.py
   ```
2. The script will:
   - Download videos from **predefined playlist links**.
   - Process **scene detection & audio transcription**.
3. Outputs stored in **organized folders** per video.

## 📁 File Outputs
- **`/downloaded_videos/`** → Raw downloaded YouTube videos.
- **`/processed_videos/`** → Organized folders per processed video.
- **`/storyboards/`** → Scene summaries.
- **`/transcriptions/`** → Audio-to-text transcriptions.
- **`/metadata.txt`** → Video metadata information.

## 📌 Next Steps
- Improve **scene detection accuracy** using machine learning.
- Add **multi-language transcription support**.
- Enhance **playlist management & error handling**.

## 🤝 Contributing
Feel free to **submit issues or pull requests** for improvements!

---
🎬 *Automating video processing, one scene at a time!*
