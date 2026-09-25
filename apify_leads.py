import os
import requests
from apify_client import ApifyClient

# Get secrets from environment variables
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

# Initialize Apify Client
client = ApifyClient(APIFY_TOKEN)

# Define search terms targeting phone-dependent service businesses
SEARCH_TERMS = [
    "plumber Las Vegas NV",
    "salon Las Vegas NV",
    "barbershop Las Vegas NV",
    "hvac repair Las Vegas NV",
    "electrician Las Vegas NV",
    "locksmith Las Vegas NV"
]

def run_apify_lead_pipeline():
    print("Starting Apify Google Maps Scraper Actor...")

    # Configure input parameters for the compass/google-maps-extractor Actor
    run_input = {
        "searchStringsArray": SEARCH_TERMS,
        "maxCrawledPlacesPerSearch": 50,
        "language": "en",
        "allPlacesNoSubcategories": True,
    }

    # Run the Apify Google Maps Scraper Actor and wait for it to finish
    # Uses the official Google Maps Scraper Actor: compass/google-maps-extractor
    run = client.actor("compass/google-maps-extractor").call(run_input=run_input)

    lead_count = 0
    print("Scrape complete. Processing and filtering datasets...")

    # Fetch results from Apify's dataset storage
    dataset_items = client.dataset(run["defaultDatasetId"]).iterate_items()

    for item in dataset_items:
        rating = item.get("totalScore")
        phone = item.get("phone")
        company_name = item.get("title")
        category = item.get("categoryName") or "Local Service"

        # FILTER: Must have a phone number AND rating strictly under 3.0
        if phone and rating is not None and rating < 3.0:
            payload = {
                "company_name": company_name,
                "phone": phone,
                "rating": rating,
                "reviews_count": item.get("reviewsCount", 0),
                "category": category,
                "website": item.get("website"),
                "address": item.get("address"),
                "vulnerability_tag": "High Risk - Missing Inbound Calls"
            }

            print(f"MATCH: {company_name} | Rating: {rating} | Phone: {phone} | Cat: {category}")

            # Send payload directly to Zapier Catch Webhook -> HubSpot
            if ZAPIER_WEBHOOK_URL:
                res = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
                if res.status_code == 200:
                    lead_count += 1

    print(f"Finished pipeline. Pushed {lead_count} low-rated leads to HubSpot.")

if __name__ == "__main__":
    run_apify_lead_pipeline()
