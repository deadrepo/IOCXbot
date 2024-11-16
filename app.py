import time
import requests
import tweepy
import os
from datetime import datetime
import urllib3

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Twitter API credentials
api_key = "v3eBMl6Jf6OYXsn9RqwS0zvrT"
api_secret = "CBObgJalMyopVjwt9p4JYwm1Fbg4vxwEABha3zfJqXyBBfhcEs"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAGiLwwEAAAAAsV8z5QreyqnmJJCzsykS0akTu5U%3DJbLWVY9QZ4pDnzOgPyJv10x0MXLQjh7XLTWzBeDI22N6rsVhEQ"
access_token = "1855504506454491136-DRgM24DGusF0qBAK95B6hDevi7CDWp"
access_token_secret = "WQJJCSqGuxUD7IJwmUqf3t1Z6GjA4wG1Jjr523fz8eQKU"

# Authenticate with Twitter
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Function to get the latest IOCs from the API
def get_latest_ioc():
    url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
    headers = {
        'X-OTX-API-KEY': '3e8d87461d891ed5defdb37347af501379c56b2701dfe4ff6466d91607f48604'
    }
    try:
        response = requests.get(url, headers=headers, verify=False)  # Disable SSL verification
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                first_result = data['results'][1]
                ioc_name = first_result.get('name', 'No Name Available').split('.')[0] + "."
                adversary = first_result.get('adversary', '')
                first_indicator = first_result['indicators'][0]['indicator'].replace('.com', '[dot]com')
                tweet_content = f"New IOC Alert →\n\n{ioc_name}\n\n"
                if adversary:
                    tweet_content += f"Adversary: {adversary}\n\n"
                tweet_content += f"Indicator: {first_indicator}"
                return tweet_content, ioc_name
            else:
                print("No results found.")
                return None, None
        else:
            print(f"Error fetching IOCs: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Error during API request: {e}")
        return None, None

# Function to read previously stored IOCs
def read_stored_iocs(filename="stored_iocs.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return [ioc.strip() for ioc in file.readlines()]
    return []

# Function to store new IOC
def store_ioc(ioc_name, filename="stored_iocs.txt"):
    with open(filename, "a") as file:
        file.write(ioc_name + "\n")

# Main function to run the bot
def run_bot():
    while True:
        try:
            tweet_content, ioc_name = get_latest_ioc()
            if tweet_content:
                stored_iocs = read_stored_iocs()
                if ioc_name not in stored_iocs:
                    try:
                        client.create_tweet(text=tweet_content)
                        print(f"Tweeted: {tweet_content}")
                        store_ioc(ioc_name)
                    except Exception as e:
                        print(f"Error while tweeting: {e}")
                else:
                    print("This IOC has already been tweeted.")
            else:
                print("No new IOCs found.")
        except Exception as e:
            print(f"Error in run_bot loop: {e}")
        time.sleep(300)  # Wait 5 minutes before next iteration

if __name__ == "__main__":
    run_bot()
