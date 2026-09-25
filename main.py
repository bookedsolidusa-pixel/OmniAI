import os
import requests
from outscraper import OutscraperClient

API_KEY = os.getenv("OUTSCRAPER_API_KEY")
WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

client = OutscraperClient(api_key=API_KEY)

# Define target queries
QUERIES = [
    "plumbers in Las Vegas NV",
    "salons in Las Vegas NV",
    "barbershops in Las Vegas NV",
    "hvac repair in Las Vegas NV",
    "electricians in Las Vegas NV",
    "locksmiths in Las Vegas NV"
]

def run_daily_extraction():
    print("Fetching listings...")
    # Pull Google Maps results
    results = client.google_maps_search(QUERIES, limit=50, language="en", region="us")

    count = 0
    for query_group in results:
        for place in query_group:
            rating = place.get("rating")
            phone = place.get("phone")

            # FILTER: Must have a phone number AND rating strictly less than 3.0
            if phone and rating is not None and rating < 3.0:
                payload = {
                    "company_name": place.get("name"),
                    "phone": phone,
                    "rating": rating,
                    "reviews_count": place.get("reviews"),
                    "category": place.get("category") or "Local Service",
                    "website": place.get("site"),
                    "address": place.get("full_address"),
                    "vulnerability_tag": "High Risk - Missing Inbound Calls"
                }

                # Push to Zapier -> HubSpot
                if WEBHOOK_URL:
                    res = requests.post(WEBHOOK_URL, json=payload)
                    if res.status_code == 200:
                        count += 1

    print(f"Extraction complete. Sent {count} leads to HubSpot.")

if __name__ == "__main__":
    run_daily_extraction()
