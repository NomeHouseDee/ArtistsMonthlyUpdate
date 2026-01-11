import pandas as pd
import smtplib
from email.mime.text import MIMEText

# --- CONFIGURATION ---
SENDER_EMAIL = "nomehousestudio@gmail.com"
# PASTE YOUR 16-DIGIT APP PASSWORD INSIDE THE QUOTES BELOW (Keep the spaces if you want, or remove them, it works either way)
SENDER_PASSWORD = "kojt audy sjra ecms"

# The "Threshold" - How much growth triggers an alert?
GENRE_BENCHMARKS = {
    # High Volatility: Viral-heavy genres need a higher bar to trigger an alert
    'Electronic': 0.25,  # 25% (includes Jungle, Hyperpop)
    'Indie-Pop': 0.15,  # 15% (Standard viral potential)

    # Medium Volatility
    'Post-Punk': 0.12,  # 12% (Niche, community-driven)
    'Alternative': 0.12,  # 12%
    'Indie': 0.15,  # 15% (General Indie)

    # Low Volatility: "Slow Burn" genres where small growth matters more
    'Singer-Songwriter': 0.08  # 8% (Harder to grow fast, so 8% is a big deal)
}
# --- THE ENGINE FUNCTIONS ---

def calculate_velocity(current, previous):
    """Calculates growth percentage."""
    if previous == 0: return 0
    return (current - previous) / previous


def send_real_email(artist_email, artist_name, growth_rate):
    """Sends email using Port 587 (STARTTLS) to avoid Mac network blocks."""
    subject = f"🚀 BREAKOUT ALERT: {artist_name} (+{growth_rate * 100:.1f}%)"
    body = f"""
    Hi {artist_name},

    FanEngine has detected a spike in your performance!

    📈 Growth Velocity: {growth_rate * 100:.1f}%

    This triggers a 'Breakout Moment' on our platform. 
    Would you like to schedule a strategy call to monetize this trend?

    Reply YES to this email.

    - The FanEngine Team
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = artist_email

    print(f"   ⏳ Connecting to Gmail for {artist_name}...")

    try:
        # TIMEOUT: We give it 10 seconds to connect, otherwise it errors out (no more hanging)
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
            server.ehlo()  # Say "Hello" to the server
            server.starttls()  # Encrypt the connection
            server.ehlo()  # Say "Hello" again (encrypted this time)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"   ✅ EMAIL SENT successfully!")

    except Exception as e:
        print(f"   ❌ EMAIL FAILED: {e}")
def check_breakout(row):
    """Analyzes a single artist for breakout signs."""
    genre = row['genre']
    ugc_growth = calculate_velocity(row['tiktok_ugc_current'], row['tiktok_ugc_previous'])
    required_growth = GENRE_BENCHMARKS.get(genre, 0.15)

    if ugc_growth > required_growth and row['sentiment_score'] > 0.5:
        return True, ugc_growth
    return False, ugc_growth


# --- MAIN EXECUTION ---
def run_engine():
    print("--- FanEngine 2026 Starting ---")

    try:
        df = pd.read_csv('artist_data.csv')
    except FileNotFoundError:
        print("❌ ERROR: Could not find 'artist_data.csv'.")
        return

    # Process each artist
    for index, row in df.iterrows():
        is_breakout, growth = check_breakout(row)

        if is_breakout:
            print(f"\n🚀 Breakout Detected: {row['artist_name']}")
            # FOR TESTING: We are sending the email to YOU (the studio) to verify it works.
            # In the future, we will change this to row['artist_email']
            send_real_email(SENDER_EMAIL, row['artist_name'], growth)
        else:
            print(f"🔹 {row['artist_name']} is stable.")

    print("\n--- Scan Complete ---")


if __name__ == "__main__":
    run_engine()