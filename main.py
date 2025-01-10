import requests
import time
from plyer import notification

# Twitch API credentials
CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'

# The name of the game you want to monitor
GAME_NAME = 'GAME_NAME'

# How often to check (in seconds)
CHECK_INTERVAL = 60

# Authenticate with Twitch API
def get_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']

# Get game ID from its name
def get_game_id(access_token, game_name):
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    params = {'name': game_name}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json().get('data', [])
    if data:
        return data[0]['id']
    else:
        raise ValueError(f"Game '{game_name}' not found on Twitch.")

# Check for live streams for a specific game
def check_streams(access_token, game_id):
    url = 'https://api.twitch.tv/helix/streams'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    params = {'game_id': game_id, 'first': 100}  # Adjust 'first' to get more results
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get('data', [])

# Send desktop notification
def send_notification(streamer_name, title):
    notification.notify(
        title=f"{streamer_name} is live!",
        message=title,
        timeout=10
    )

def main():
    try:
        access_token = get_access_token()
        game_id = get_game_id(access_token, GAME_NAME)
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return

    print(f"Monitoring streams for game: {GAME_NAME}...")
    already_alerted = set()

    while True:
        try:
            streams = check_streams(access_token, game_id)
            if not streams:
                print("No streams found.")
            for stream in streams:
                unique_id = f"{stream['user_name']}_{stream['id']}"
                if unique_id not in already_alerted:
                    streamer_name = stream['user_name']
                    title = stream['title']
                    alert_message = f"\n===============\nStreamer: {streamer_name}\nTitle: {title}\n==============="
                    print(alert_message)
                    send_notification(streamer_name, title)
                    already_alerted.add(unique_id)
        except Exception as e:
            print(f"Error during stream check: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
