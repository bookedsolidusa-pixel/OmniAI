import os
import requests
from outscraper import OutscraperClient

API_KEY = os.getenv("OUTSCRAPER_API_KEY")
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

client = OutscraperClient(api_key=API_KEY)

QUERIES = [
    "plumbers in Las Vegas NV",
    "salons in Las Vegas NV",
    "barbershops in Las Vegas NV",
    "hvac repair in Las Vegas NV",
    "electricians in Las Vegas NV",
    "towing service in Las Vegas NV"
]

def run_daily_pipeline():
    print("Running daily extraction pipeline...")
    results = client.google_maps_search(QUERIES, limit=50, language="en", region="us")

    lead_count = 0
    for query_results in results:
        for place in query_results:
            rating = place.get("rating")
            phone = place.get("phone")

            # Filter for active phone numbers and rating < 3.0
            if phone and rating is not None and rating < 3.0:
                payload = {
                    "company_name": place.get("name"),
                    "phone": phone,
                    "rating": rating,
                    "reviews_count": place.get("reviews"),
                    "category": place.get("category") or "General Service",
                    "website": place.get("site"),
                    "address": place.get("full_address"),
                    "lead_status": "Uncontacted - Low Rating",
                    "source": "Daily Automated Scraper"
                }

                # Post lead directly to Zapier -> HubSpot
                if ZAPIER_WEBHOOK_URL:
                    response = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
                    if response.status_code == 200:
                        lead_count += 1

    print(f"Pipeline finished successfully. Sent {lead_count} low-rated leads to HubSpot.")

if __name__ == "__main__":
    run_daily_pipeline()
