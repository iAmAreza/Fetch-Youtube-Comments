from googleapiclient.discovery import build
import json
import re
import os

# Your YouTube API key
api_key = 'Replace this with your YouTube API key'  

# YouTube API client setup
youtube = build('youtube', 'v3', developerKey=api_key)

def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    video_id = None
    patterns = [
        r"youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)([a-zA-Z0-9_-]{11})",  # Full URL
        r"youtu\.be\/([a-zA-Z0-9_-]{11})"  # Shortened URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break

    return video_id

def get_video_comments(video_url):
    # Extract video ID from URL
    video_id = extract_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL")
        return []

    comments = []
    
    # Fetch only top-level comments (ignore replies)
    comment_response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
    ).execute()

    # Extract only comment text
    while comment_response:
        for item in comment_response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            # Remove '\n\n' and '\n' and replace with a space
            comment = comment.replace('\n\n', ' ').replace('\n', ' ')
            comments.append(comment)

        # Check for the next page of comments
        if 'nextPageToken' in comment_response:
            comment_response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=comment_response['nextPageToken'],
                textFormat='plainText'
            ).execute()
        else:
            break

    return comments

# Replace with the actual YouTube video URL
video_url = ''  # e.g. 'https://www.youtube.com/watch?v=VIDEO_ID'
comments = get_video_comments(video_url)

# Save comments to a JSON file with UTF-8 encoding
if comments:
    with open('comments.json', 'w', encoding='utf-8') as json_file:
        json.dump(comments, json_file, indent=4, ensure_ascii=False)
    print("Comments saved to comments.json")
else:
    print("No comments fetched.")
