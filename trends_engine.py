import pandas as pd
from pytrends.request import TrendReq
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import os


def get_artist_trends(artist_json_path):
    with open(artist_json_path, 'r') as f:
        profile = json.load(f)

    artist_name = profile['name']
    keywords = profile.get('search_keyword', [profile.get('primary_genre', 'Music')])
    if isinstance(keywords, str):
        keywords = [keywords]
    main_keyword = keywords[0]
    all_query_words = []

    print(f"🔍 Fetching LIVE trends for {artist_name} using: '{main_keyword}'...")

    pytrends = TrendReq(
        hl='en-US',
        tz=0,
        retries=3,
        backoff_factor=0.5,
        requests_args={
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
        }
    )
    try:
        pytrends.build_payload([main_keyword], cat=35, timeframe='now 7-d')  # cat=35 is the "Music" category
        related_queries = pytrends.related_queries()
        if main_keyword in related_queries and related_queries[main_keyword]['rising'] is not None:
            rising_df = related_queries[main_keyword]['rising']
            all_query_words = rising_df['query'].tolist()
        if all_query_words:
            word_string = " ".join(all_query_words)
        else:
            # Fallback if the keyword is too niche for Google.
            word_string = " ".join(keywords) + f" {profile.get('primary_genre', 'Music')} New-Music"

    except Exception as e:
        print(f"⚠️ Google Trends Error: {e}. Using fallback words.")
        word_string = " ".join(keywords) + " Trending Music Production"
    print(f"☁️ Generating Word Cloud for {artist_name}...")
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='magma'
    ).generate(word_string)
    cloud_path = f"{artist_name}_wordcloud.png"
    wordcloud.to_file(cloud_path)

    # Send the keywords back to WeeklyReport.py for the CSV attachment
    result_keywords = all_query_words if all_query_words else keywords

    return cloud_path, result_keywords


if __name__ == "__main__":
    test_path = 'profiles/artist_01.json'
    if os.path.exists(test_path):
        path = get_artist_trends(test_path)
        print(f"✅ Created: {path}")
    else:
        print(f"❌ Could not find {test_path} to test.")
