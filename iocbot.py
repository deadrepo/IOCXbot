import time
import requests
import tweepy
import os
from datetime import datetime

# Twitter API credentials
api_key = ""
api_secret = ""
bearer_token = ""
access_token = ""
access_token_secret = ""

# Authenticate with Twitter
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Function to get the latest IOCs from the API
def get_latest_ioc():
    url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
    headers = {
        'X-OTX-API-KEY': ''
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Check if there are any results and return the first one
        if data.get('results'):
            first_result = data['results'][0]
            ioc_name = first_result.get('name', 'No Name Available')

            # Trim the name until the first dot (before 'public services')
            trimmed_ioc_name = ioc_name.split('.')[0] + "."

            # Get adversary and first indicator
            adversary = first_result.get('adversary', 'Unknown')
            first_indicator = first_result['indicators'][0]['indicator']

            # Replace .com with [dot]com
            first_indicator = first_indicator.replace('.com', '[dot]com')

            # Construct the IOC content with timestamp for uniqueness
            tweet_content = f"New IOC Alert →\n\n" \
                             f"{trimmed_ioc_name}\n\n" \
                             f"Adversary: {adversary}\n\n" \
                             f"Indicator: {first_indicator}"

            return tweet_content, trimmed_ioc_name
        else:
            print("No results found.")
            return None, None
    else:
        print(f"Error fetching IOCs from OTX: {response.status_code}")
        return None, None

# Function to read previously stored IOCs from a text file
def read_stored_iocs(filename="stored_iocs.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            stored_iocs = file.readlines()
        return [ioc.strip() for ioc in stored_iocs]
    else:
        return []

# Function to store the new IOC in the text file
def store_ioc(ioc_name, filename="stored_iocs.txt"):
    with open(filename, "a") as file:
        file.write(ioc_name + "\n")

# Main function to run the bot continuously
def run_bot():
    while True:
        # Get the latest IOC content and the IOC name
        tweet_content, ioc_name = get_latest_ioc()

        # If a new IOC is found
        if tweet_content:
            # Read stored IOCs
            stored_iocs = read_stored_iocs()

            # Check if the IOC has already been stored or tweeted
            if ioc_name not in stored_iocs:
                # Send the tweet
                try:
                    client.create_tweet(text=tweet_content)
                    print(f"Tweeted: {tweet_content}")
                    # Store the new IOC in the file
                    store_ioc(ioc_name)
                except Exception as e:
                    print(f"Error while tweeting: {e}")
            else:
                print("This IOC has already been stored or tweeted.")

        else:
            print("No new IOCs found or there was an issue fetching them.")

        # Wait for a while before checking again (e.g., every 5 minutes)
        time.sleep(60)

if __name__ == "__main__":
    run_bot()
