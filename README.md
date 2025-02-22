# YouTube Comment Fetcher

This script helps you find your most-liked YouTube comments by analyzing your YouTube comment history from Google Takeout and using the YouTube API to fetch like counts. 

## Setup Instructions

YouTube Guide on running this:
https://www.youtube.com/watch?v=gqMg1ld-Vu0&t=332s

### 1. Download Your YouTube Data
1. Go to [Google Takeout](https://takeout.google.com/settings/takeout)
2. Click "Deselect all" and then only select "YouTube and YouTube Music"
3. Request your data and wait for Google to prepare it
4. Download and extract the Takeout archive
5. You might need to combine all the outputs into the same folder. We're only interested in the stuff stored at "Takeout/YouTube and YouTube Music/comments/"

### 2. Get a YouTube API Key
1. Make a [Google Cloud Console project](https://console.cloud.google.com/projectcreate)
2. Enable the [YouTube Data API v3](https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com)
3. Create credentials (API key)
4. Copy your API key
5. Edit the `most_liked_youtube_comments.py` script and replace the bit that says `"YOUR_API_KEY"` with the text you just copied.

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

## Usage
1. Place the script (`most_liked_youtube_comments.py`) in the same directory as your extracted Takeout files
2. Run the script:
```bash
python most_liked_youtube_comments.py
```

2. The script will:
   - Find your comments from the Takeout files
   - Fetch like counts for each comment using the YouTube API
   - Create a cache file (`comments_cache.csv`) to save progress, in case the script gets interrupted half-way
   - Generate an output JSON file (`most_liked_comments.json`) with your comments sorted by likes.

## Output

The script generates two files:
- `comments_cache.csv`: A cache file to avoid re-fetching data if the script is interrupted
- `most_liked_comments.json`: The final output with all your comments sorted by like count

## Notes

- The script uses API quota points. There's a daily limit of 10,000 comments with the API. If you hit the limit the script will stop working, but progress will be saved so you can just run the script again the next day and it'll keep going from where it left off.
- Comments that don't exist anymore will be marked as "not found" in the output JSON file.

## Troubleshooting

If you encounter any issues:

1. **Can't find comments file**: Make sure the script is in the correct directory with your Takeout files
2. **API Key errors**: Make sure you've followed step 2, and that you've replaced the `"YOUR_API_KEY"` text in the .py file with your actual API key.
3. **Quota limits**: The script will stop if you hit the API quota limit. Wait 24 hours and try again

## Contributing

Feel free to submit issues and enhancement requests!
