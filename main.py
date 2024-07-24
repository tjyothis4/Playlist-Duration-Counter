from googleapiclient.discovery import build # to interact with YouTube API 
from datetime import timedelta
import os
import re

# For more information, check https://developers.google.com/youtube/v3/docs/ 

# TO-DO: check how to make it deployable, with environment variables
API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initializing the YouTube API Client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_playlist_duration(playlist_id):
    total_duration = timedelta()
    next_page_token = None # for pagination

    # The following code is mostly just using the API
    
    # Geting a page of playlist items. 
    while True:
        playlist_items = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        # Every YouTube video has a base 64 ID, here we collect all IDs
        video_ids = [item['contentDetails']['videoId'] for item in playlist_items['items']]

        # Getting details of each video, we will get duration from here. 
        video_response = youtube.videos().list(
            part='contentDetails',
            id=','.join(video_ids)
        ).execute()

        # Adding up all the durations
        for video in video_response['items']:
            duration = video['contentDetails']['duration']
            duration_timedelta = parse_duration(duration)
            total_duration += duration_timedelta

        # Getting the next page of videos
        next_page_token = playlist_items.get('nextPageToken')
        # Stopping While Loop if all pages have been processed
        if not next_page_token:
            break

    return total_duration

# Parsing the duration using regular expression
def parse_duration(duration):
    regex = re.compile(r'P(?:(?P<days>\d+)D)?T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    match = regex.match(duration)
    if not match:
        return timedelta()
    parts = {k: int(v) if v else 0 for k, v in match.groupdict().items()}
    return timedelta(**parts)

# Prompting input and calling necessary functions
playlist_id = input('Enter your playlist id ')
total_duration = get_playlist_duration(playlist_id)
print(f"Total duration of the playlist: {total_duration}")
