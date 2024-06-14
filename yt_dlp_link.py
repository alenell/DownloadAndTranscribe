import yt_dlp

def download_subtitles(video_url, language='en', subtitle_format='srt'):
    ydl_opts = {
        'skip_download': False,
        'writesubtitles': True,
        'subtitleslangs': [language],
        'subtitlesformat': subtitle_format,
        'outtmpl': '%(title)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

# Example usage
video_url = ''
download_subtitles(video_url)