import requests
import csv
import time
from datetime import datetime, timezone
import subprocess

graphql_endpoint = "https://api-gateway.skymavis.com/graphql/marketplace"
api_key = "rXbMQ0vDzJieYwyJWdFJdLjtq1TSvZCG"

def fetch_graphql(query):
    try:
        response = requests.post(graphql_endpoint, json={'query': query}, headers={
            'Content-Type': 'application/json',
            'X-Api-Key': api_key
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def update_csv():
    query1 = """
    query MyQuery {
        erc1155Tokens {
            results {
                name
                minPrice
                tokenType
            }
        }
    }"""

    query2 = """
    query MyQuery {
        exchangeRate {
            eth {
                usd
            }
        }
    }"""

    data1 = fetch_graphql(query1)
    data2 = fetch_graphql(query2)

    if data1 and data2:
        exchange_rate = data2['data']['exchangeRate']['eth']['usd']
        tokens = data1['data']['erc1155Tokens']['results']

        # Prepare CSV content
        csv_content = [["Token Name", "Price (USD)", "Currency"]]
        for token in tokens:
            eth_price = float(token['minPrice']) / 1e18
            usd_price = round(eth_price * exchange_rate, 4)
            csv_content.append([token['name'], usd_price, "USD"])

        # Add last updated timestamp
        last_updated = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        csv_content.append([last_updated])

        # Write to CSV file
        with open('prices.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_content)

        print(f"CSV updated at {last_updated}")

        # Run Git commands
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Update prices.csv at {last_updated}"])
        subprocess.run(["git", "push"])

if __name__ == "__main__":
    while True:
        update_csv()
        time.sleep(300)  # Wait for 5 minutes (300 seconds)