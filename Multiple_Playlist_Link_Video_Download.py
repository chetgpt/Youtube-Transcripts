import os
from pytube import Playlist, YouTube
from pytube.exceptions import AgeRestrictedError

def create_directory(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def download_video(yt, download_path):
    """Download a video."""
    try:
        video = yt.streams.get_highest_resolution()
        video.download(download_path)
        print(f"Downloaded video '{yt.title}' successfully.")
    except Exception as e:
        print(f"Failed to download video {yt.watch_url}: {e}")

def download_videos_from_playlist(playlist_url, download_path):
    """Download all videos from a YouTube playlist."""
    playlist = Playlist(playlist_url)
    create_directory(download_path)
    for url in playlist.video_urls:
        try:
            yt = YouTube(url)
            download_video(yt, download_path)
        except AgeRestrictedError:
            print(f"Video {url} is age restricted and cannot be downloaded. Skipping.")
        except Exception as e:
            print(f"Failed to download video {url}: {e}")

def main(playlist_urls, download_path):
    """Process videos from multiple playlist URLs."""
    for playlist_url in playlist_urls:
        print(f"Processing playlist: {playlist_url}")
        download_videos_from_playlist(playlist_url, download_path)

if __name__ == "__main__":
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
        # Add more playlist URLs as needed
    ]
    download_path = 'downloaded_videos'
    main(playlist_urls, download_path)
