from googleapiclient.discovery import build
from datetime import timedelta
import os
import re

# You need to set up a Google Cloud project and enable the YouTube Data API
# Then, create an API key and set it as an environment variable
API_KEY = os.environ.get('YOUTUBE_API_KEY')

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_playlist_duration(playlist_id):
    total_duration = timedelta()
    next_page_token = None

    while True:
        playlist_items = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids = [item['contentDetails']['videoId'] for item in playlist_items['items']]

        video_response = youtube.videos().list(
            part='contentDetails',
            id=','.join(video_ids)
        ).execute()

        for video in video_response['items']:
            duration = video['contentDetails']['duration']
            duration_timedelta = parse_duration(duration)
            total_duration += duration_timedelta

        next_page_token = playlist_items.get('nextPageToken')
        if not next_page_token:
            break

    return total_duration

def parse_duration(duration):
    regex = re.compile(r'P(?:(?P<days>\d+)D)?T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    match = regex.match(duration)
    if not match:
        return timedelta()
    parts = {k: int(v) if v else 0 for k, v in match.groupdict().items()}
    return timedelta(**parts)

playlist_id = input('Enter your playlist id ')
total_duration = get_playlist_duration(playlist_id)
print(f"Total duration of the playlist: {total_duration}")