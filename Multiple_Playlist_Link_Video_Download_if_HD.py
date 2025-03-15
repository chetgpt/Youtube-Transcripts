from pytube import Playlist, YouTube
import os

def create_directory(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def download_video_in_hd(youtube, download_path):
    """Download a video in HD quality if available."""
    try:
        # Try to download in 1080p resolution first, then 720p, and fallback to the highest resolution.
        video = youtube.streams.filter(res="1080p", file_extension="mp4").first() or \
                youtube.streams.filter(res="720p", file_extension="mp4").first() or \
                youtube.streams.get_highest_resolution()
        
        if video:
            video_path = video.download(download_path)
            print(f"Downloaded video '{youtube.title}' to '{video_path}'")
        else:
            print(f"No suitable HD stream found for '{youtube.title}'.")
    except Exception as e:
        print(f"Failed to download video '{youtube.watch_url}': {e}")

def download_videos_from_playlist(playlist_url, download_path):
    """Download all videos from a YouTube playlist in HD quality."""
    playlist = Playlist(playlist_url)
    create_directory(download_path)
    print(f"Downloading videos from playlist: {playlist.title}")

    for video_url in playlist.video_urls:
        try:
            youtube = YouTube(video_url)
            download_video_in_hd(youtube, download_path)
        except Exception as e:
            print(f"Failed to download video {video_url}: {e}")

def main():
    playlist_urls = ['https://www.youtube.com/watch?v=-hmceyP5skg&list=PLl9n0JUPTcFkOMJDZ0jVwZ6lC2yZ1JMIJ&pp=iAQB',
        'https://www.youtube.com/watch?v=3hd39ktiEto&list=PLl9n0JUPTcFnsedkRqiWYDI5rXGdIci6i&pp=iAQB',
        'https://www.youtube.com/watch?v=2eUGGQUkLbQ&list=PLl9n0JUPTcFkpK-sDGGe6RQdjcKVFwfel&pp=iAQB',
        'https://www.youtube.com/watch?v=FF9l4uIGzu4&list=PLl9n0JUPTcFmlYA4LrYirWoV96CENMUtH&pp=iAQB',
        'https://www.youtube.com/watch?v=WXiaFCNdFwM&list=PLl9n0JUPTcFl7uw62zZrgsUmglc8UVMkZ&pp=iAQB',
        'https://www.youtube.com/watch?v=mVwfkBsN-Xg&list=PLl9n0JUPTcFlen_AMvLPhJbPXRYmLVcgH&pp=iAQB',
        'https://www.youtube.com/watch?v=iTt41yQn3t0&list=PLl9n0JUPTcFlCYmKF9M0rQ7O1EvcGODx0&pp=iAQB',
        'https://www.youtube.com/watch?v=S4TMRVju11o&list=PLl9n0JUPTcFkcw7AfDT_9gLlCZIHzvwx0&pp=iAQB',
        'https://www.youtube.com/watch?v=a1ZikTy8H2Y&list=PLl9n0JUPTcFklDuIgGOINdG_XptNoGE5l&pp=iAQB',
        'https://www.youtube.com/watch?v=7K3SKEF8YGU&list=PLl9n0JUPTcFkJnzxMqMBwkMZ3hUSur0ab&pp=iAQB',
        'https://www.youtube.com/watch?v=7K3SKEF8YGU&list=PLl9n0JUPTcFlM1doEopKnKU0wywuWkvJi&pp=iAQB',
        'https://www.youtube.com/watch?v=AswXUyNoc8s&list=PLl9n0JUPTcFlyOuA8Jck_aQd_EltiQPie&pp=iAQB'
    ]
    download_path = 'downloaded_videos'

    for playlist_url in playlist_urls:
        download_videos_from_playlist(playlist_url, download_path)

if __name__ == "__main__":
    main()
