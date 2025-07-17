# 🏏 ESPN Cricinfo CLI Live Commentary Tracker
# This script provides real-time commentary updates (overs, runs, and commentary) for ongoing live cricket matches.

import requests
import time

# Base URL to fetch current live matches from ESPN Cricinfo
MATCHES_URL = "https://hs-consumer-api.espncricinfo.com/v1/pages/matches/current?lang=en&latest=true"

# Fetch the list of current matches
response = requests.get(MATCHES_URL)
match_data = response.json()

# Extract only live matches using list comprehension
# Each item = [scribeId, seriesId, series name, team1, team2]
live_matches = [
    [
        match['scribeId'],
        match['series']['objectId'],
        match['series']['longName'],
        match['teams'][0]['team']['longName'],
        match['teams'][1]['team']['longName']
    ]
    for match in match_data['matches'] if match['status'] == "Live"
]

# If no live matches, notify the user
if not live_matches:
    print("NO LIVE MATCHES")
else:
    # Display the list of live matches to the user
    print("Available Live Matches:\n")
    for i, live_match in enumerate(live_matches):
        print(f"Live {i + 1} ->> {live_match[2]}")

    # User selects a live match
    selected_match = input("\nSelect Your Live Match (e.g., Live 1): ").lower()
    
    # Strip prefix like "live", "live ", etc., and convert to integer index
    user_input = selected_match.strip("live ") or selected_match.strip("live") or selected_match
    user_input = int(user_input)

    # Fetch metadata of selected match
    match_name = live_matches[user_input - 1][2]
    team_vs = f"{live_matches[user_input - 1][3]} VS {live_matches[user_input - 1][4]}"
    print(f"\n{match_name}\n{team_vs}\n")

    # Store previously seen overs to avoid duplication
    seen_overs = set()
    last_commentary = ""

    # Main loop: Poll the API continuously for the latest ball updates
    while True:
        current_match = live_matches[user_input - 1]

        # Match details endpoint (dynamic based on match and series IDs)
        DETAIL_URL = (
            f"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?"
            f"&seriesId={current_match[1]}&matchId={current_match[0]}&latest=true"
        )

        # Fetch detailed data for selected match
        match_details = requests.get(DETAIL_URL).json()
        recent_ball = match_details['recentBallCommentary']['ballComments'][0]

        # Extract ball information
        over = recent_ball['oversActual']
        title = recent_ball['title']
        runs = recent_ball['totalRuns']
        commentary_items = recent_ball.get('commentTextItems')

        # Check and skip duplicate overs (based on over number)
        seen_overs.add(over)

        # Build message text
        if commentary_items:
            commentary_text = commentary_items[0]['html']
            output = (
                f"Over : {over}\n"
                f"Title : {title}\n"
                f"Runs : {runs}\n"
                f"Commentary: {commentary_text}\n"
            )
        else:
            output = (
                f"Over : {over}\n"
                f"Title : {title}\n"
                f"Runs : {runs}\n"
                "----------No Commentary Available----------\n"
            )

        # Avoid printing duplicate commentary
        if output != last_commentary:
            print(output)
            last_commentary = output
        else:
            # If same as previous, just wait
            time.sleep(15)

        # Sleep to prevent over-polling the API
        time.sleep(15)
