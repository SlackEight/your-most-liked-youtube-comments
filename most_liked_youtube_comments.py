# Standard library imports
import json
import os

# Third-party imports
from googleapiclient.discovery import build
from tqdm import tqdm

youtube_v3_api_key = "YOUR_API_KEY"

print("Welcome to the YouTube Comment Fetcher! \\o/ - Written by @slackeight")

print("Step 1 is getting all the comments from the Google Takeout files... ", end="")

def fix_weird_text_stuff(text):
    weird_text_stuff = {
        "&quot;": "\"",
        "&#39;": "'",
        "&#x27;": "'",
        "&#x2F;": "/",
        "&amp;": "&",
        "<br>": "\n",
        "\u2014": "-"
    }
    for key, value in weird_text_stuff.items():
        text = text.replace(key, value)
    return text

possible_paths = [
    'Takeout/YouTube and YouTube Music/comments',
    'YouTube and YouTube Music/comments',
    'comments',
    '.'
]
for path in possible_paths:
    if os.path.exists(path) and "comments.csv" in os.listdir(path):
        comments_files = [path+"/"+f for f in os.listdir(path) if f.endswith('.csv')]
        break

if not comments_files:
    error_message = """ERROR! Couldn't find the Google Takout comments file.
    
    1. If you haven't downloaded your YouTube data from Google Takeout, you can do that here: https://takeout.google.com/settings/takeout
    - Click deselect all on the top right, and then only select YouTube and YouTube Music. Then request your data. They take a while to process, but will send you a download link when they're done.
    
    2. If you've already downloaded your Takeout files, make sure you've extracted them, and placed this python script (top_comments.py) inside the Takeout folder. It should work anywhere in the root of the Takeout folder."""
    raise FileNotFoundError(error_message)

comment_ids = []
for file in comments_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            comment_ids.extend([line.split(',')[0] for line in f if line.strip()])
    except Exception as e:
        print(f"Warning: Error reading file {file}: {e}")
        continue

print("Done! Successfully loaded in the comments.\n")

print("Step 2 is building a YouTube API client. We need this to see how many likes each comment got... ", end="")

try:
    youtube = build('youtube', 'v3', developerKey = youtube_v3_api_key if youtube_v3_api_key != "YOUR_API_KEY" else os.getenv("YOUTUBE_V3_API_KEY"))
except Exception as e:
    error_message = """ERROR! Couldn't build the YouTube API client. In order to use this script, you'll need to create a YouTube API key (this is free, if you exceed the 10k daily limit, the script will just stop working so don't worry).
    
    To get an API key, go to the Google Cloud Console (https://console.cloud.google.com/) and follow these steps:
       - Sign in with your Google account
       - Click the "Select a project" dropdown in the top left
       - Click "Create project"
       - Go to the https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com
       - Click on "Enable"
       - Click on the Credentials tab
       - Click on "Create credentials"
       - Select "API key"
       - Copy the API key and paste it into the youtube_v3_api_key variable in the script
    """
    raise Exception(error_message)

comment_data = {}

print("Done! Built the YouTube API client. Now we're going to get the comment data...\n\n")

print(f"To avoid needing to re-run this script from scratch if something goes wrong, we'll temporarily save everything to comments_cache.json (in case you were wondering what that file is)")

cache_separator = "!SEPERATOR!"
try:
    with open('comments_cache.csv', 'r', encoding='utf-8') as f:
        try:
            comment_data = {
                line.split(cache_separator)[0]: {
                    'comment': fix_weird_text_stuff(line.split(cache_separator)[1].strip()),
                    'like_count': line.split(cache_separator)[2].strip()
                } for line in f if line.strip()
            }
        except Exception as e:
            print(f"Something went wrong while loading the cache file: {e}\n\nStarting from scratch instead")
            comment_data = {}
except FileNotFoundError:
    print("No cache file found, starting from scratch.")
    comment_data = {}

with open('comments_cache.csv', 'a', encoding='utf-8') as cache_file:
    progress_bar = tqdm(total=len(comment_ids), desc="Processing comments", miniters=2)

    unprocessed_comment_ids = [i for i in comment_ids if i not in comment_data]
    progress_bar.update(len(comment_ids) - len(unprocessed_comment_ids))

    for comment_id in unprocessed_comment_ids:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                id=comment_id
            ).execute()
            
            if response['items']:
                content = response['items'][0]['snippet']['topLevelComment']['snippet']['textDisplay'].strip().replace("\n", " ")
                like_count = response['items'][0]['snippet']['topLevelComment']['snippet']['likeCount']
                comment_data[comment_id] = {
                    'comment': content,
                    'like_count': like_count
                }
                cache_file.write(f"{comment_id}{cache_separator}{content}{cache_separator}{like_count}\n")
                cache_file.flush()  # Ensure data is written immediately
            else:
                comment_data[comment_id] = {
                    'comment': 'not found',
                    'like_count': 0
                }
                cache_file.write(f"{comment_id}{cache_separator}not found{cache_separator}0\n")
                cache_file.flush()
        except Exception as e:
            print(f"\nWarning: Error processing comment {comment_id}: {e}")
            continue
        finally:
            progress_bar.update(1)

    progress_bar.close()

print("Done!")

# our data looks like 
'''
{
    "comment_id": {
        "comment": "comment content",
        "like_count": "number of likes"
    }
}

we want to save the JSON but write it so that the most liked comments are at the top
'''

# Convert and sort the data
sorted_comments = sorted(
    [{"id": k, "comment": v['comment'], "like_count": int(v['like_count'])} 
     for k, v in comment_data.items()],
    key=lambda x: x['like_count'],
    reverse=True
)

# Write the final JSON output
with open('most_liked_comments.json', 'w', encoding='utf-8') as f:
    json_entries = [
        json.dumps({item['id']: {'comment': item['comment'], 'like_count': item['like_count']}}, 
                  indent=4)[1:-2]
        for item in sorted_comments
    ]
    f.write('{\n    ' + ',\n    '.join(json_entries) + '\n}')
