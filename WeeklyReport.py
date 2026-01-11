import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
import json
import time
import random
import io

# Import your trends code (Ensure trends_engine.py is in the same folder)
from trends_engine import get_artist_trends
load_dotenv()


# --- 1. DATA VISUALIZATION ENGINE ---
def generate_charts(profile):
    artist_name = profile['name']
    # 1. Get the filename from your JSON data_sources
    csv_file = profile.get('data_sources', {}).get('manual_csv')

    plt.figure(figsize=(8, 4))
    sns.set_style("darkgrid")

    # 2. Check if the CSV file actually exists in your folder
    if csv_file and os.path.exists(csv_file):
        try:
            df_stats = pd.read_csv(csv_file)

            # THE SAFETY FIX: Standardize column names
            # This makes "City " (with a space) or "city" (lowercase) all match your code
            df_stats.columns = [str(col).strip().title() for col in df_stats.columns]

            # Use the cleaned names
            # Spotify "Listeners" might be "Listeners (Last 28 Days)",
            # so we look for any column containing the word "Listeners"
            city_col = 'City'
            listener_col = [col for col in df_stats.columns if 'Listener' in col][0]

            df_sorted = df_stats.sort_values(by=listener_col, ascending=False).head(5)
            cities = df_sorted[city_col].tolist()
            interactions = df_sorted[listener_col].tolist()

        except Exception as e:

            print(f"❌ Error reading CSV for {artist_name}: {e}")
            # Fallback to an "Empty State" if the CSV is corrupted
            cities = ["Data Pending"]
            interactions = [0]
    else:
        # 3. Dynamic Fallback: If no file, show a "Pending" message instead of random cities
        print(f"⚠️ No CSV found for {artist_name}. Showing pending state.")
        cities = ["Upload Data", "To See", "Top", "Fan", "Cities"]
        interactions = [0, 0, 0, 0, 0]

    # 4. Generate the Chart
    sns.barplot(x=cities, y=interactions, hue=cities, palette="viridis", legend=False)
    plt.title(f"Top Listening Hubs: {artist_name}")
    plt.ylabel("Monthly Listeners")

    image_path = f"{artist_name}_chart.png"
    plt.savefig(image_path)
    plt.close()
    return image_path

# --- 2. SYNC SCORE LOGIC ---
def calculate_sync_score(checklist):
    score = sum(checklist.values())
    if score >= 10: return score, "Ready Today", "#2e7d32"
    if score >= 7: return score, "Fix Today️", "#fbc02d"
    return score, "Needs Work ", "#d32f2f"


# --- 3. HTML TEMPLATE ---
HTML_TEMPLATE = """
<html>
<body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
    <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; background-color: #ffffff; border-radius: 10px;">

        <h2 style="color: #2e7d32; border-bottom: 2px solid #eee; padding-bottom: 10px;">
             Weekly Intelligence: {{ artist_name }}
        </h2>

        <p style="font-size: 14px; color: #555;">
            <strong>Genre Profile:</strong> {{ primary_genre }} | {{ target_market }}
        </p>

        <div style="background-color: #f4f4f4; padding: 15px; border-left: 5px solid #2e7d32; margin: 20px 0;">
    <h4 style="margin-top: 0; color: #2e7d32;"> Your Custom Focus Area:</h4>
    <p style="font-style: italic; margin-bottom: 0;">"{{ focus_message }}"</p>
    
    {% if focus_link %}
    <div style="margin-top: 15px;">
        <a href="{{ focus_link }}" style="background-color: #2e7d32; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; font-size: 12px; display: inline-block;">
            View Resource / Video
        </a>
    </div>
    {% endif %}
</div>

        <h3 style="color: #444;"> Top Fan Locations</h3>
        <p style="font-size: 13px; color: #777;">Based on your recent listener data:</p>
        <img src="cid:chart_image" style="width: 100%; border-radius: 8px; margin-bottom: 20px;">

        <h3 style="color: #444;">️ Trending Metadata Tags</h3>
        <p style="font-size: 13px; color: #777;">Current high-volume search terms for your niche:</p>
        <img src="cid:cloud_image" style="width: 100%; border-radius: 8px; margin-bottom: 10px;">

        <p style="font-size: 12px; color: #888;">
            <i>Check the attached CSV for a full list of these keywords.</i>
        </p>

        <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0 10px 0;">
        <p style="font-size: 11px; color: #aaa; text-align: center;">Sent via Nome House Studios 2026</p>
    </div>
</body>
</html>
"""

# --- 4. THE SENDER ---
def send_complete_report(profile, chart_path, cloud_path, trending_keywords):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    if not sender_email or not sender_password:
        print(" Error: Email credentials not found in .env file.")
        return

    msg = MIMEMultipart("related")
    msg['Subject'] = f"Weekly Artist Report: {profile['name']}"
    msg['From'] = sender_email
    msg['To'] = profile['email']

    # Calculate Sync Score
    score, status, color = calculate_sync_score(profile.get('sync_checklist', {}))

    # Fill Template
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        artist_name=profile['name'],
        primary_genre=profile.get('primary_genre', 'N/A'),
        target_market=profile.get('target_market_genre', 'N/A'),
        focus_message=profile.get('focus_area_message', 'Keep pushing your sound!'),
        focus_link=profile.get('focus_area_link'),  # <--- ADD THIS LINE
        score=score,
        status=status,
        score_color=color,
        growth="28"
    )
    msg.attach(MIMEText(html_content, "html"))

    # Attach Chart Image
    with open(chart_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<chart_image>')
        msg.attach(img)

    # Attach Word Cloud Image
    with open(cloud_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<cloud_image>')
        msg.attach(img)

    # Create & Attach CSV (In-Memory)
    csv_buffer = io.StringIO()
    csv_buffer.write("Trending Keyword,Source\n")
    for kw in trending_keywords:
        csv_buffer.write(f"{kw},Google Trends\n")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(csv_buffer.getvalue())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{profile["name"]}_Metadata_Tags.csv"')
    msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Success: {profile['name']}")
    except Exception as e:
        print(f"Error for {profile['name']}: {e}")


# --- 5. THE MASTER LOOP ---
# --- 5. THE MASTER LOOP ---
if __name__ == "__main__":
    profiles_dir = "profiles/"

    for filename in os.listdir(profiles_dir):
        if filename.endswith(".json"):
            path = os.path.join(profiles_dir, filename)

            with open(path, 'r') as f:
                artist_profile = json.load(f)

            print(f"\n--- Processing: {artist_profile['name']} ---")

            # 1. Run Chart Engine (Passing the profile dictionary)
            c_path = generate_charts(artist_profile)

            # 2. Run Trends Engine (Now returns TWO items)
            w_path, real_keywords = get_artist_trends(path)

            # 3. Send Email (Passing the new keywords)
            send_complete_report(artist_profile, c_path, w_path, real_keywords)

            # 4. Cleanup
            if os.path.exists(c_path): os.remove(c_path)
            if os.path.exists(w_path): os.remove(w_path)

            # 5. Anti-Ban Delay
            wait_time = random.randint(15, 30)
            time.sleep(wait_time)