import os
import subprocess

def main():
    print("🚀 STARTING WEEKLY INTELLIGENCE PIPELINE...")

    # 1. Update JSONs from the CSV you downloaded
    print("\n--- Phase 1: Updating Profiles ---")
    # This runs your Code 1 script
    subprocess.run(["python", "update_profiles.py"])

    # 2. Pause for you to do manual research
    input("\n📝 STOP: Have you finished manual research in the JSON files? (Press Enter to continue to Emails)")

    # 3. Run the Email/Trend Engine
    print("\n--- Phase 2: Generating Visuals & Sending Emails ---")
    # This runs your Code 3 script (which calls Code 2 internally)
    subprocess.run(["python", "WeeklyReport.py"])

    print("\n✅ PIPELINE COMPLETE. All artists notified.")

if __name__ == "__main__":
    main()