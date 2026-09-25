import os
import requests
from apify_client import ApifyClient

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

client = ApifyClient(APIFY_TOKEN)

# Service business categories in Las Vegas, Henderson, and Summerlin
SEARCH_TERMS = [
    "plumber Las Vegas NV",
    "salon Las Vegas NV",
    "barbershop Las Vegas NV",
    "hvac repair Las Vegas NV",
    "electrician Las Vegas NV",
    "locksmith Las Vegas NV",
    "towing service Las Vegas NV"
]

def run_apify_lead_pipeline():
    print("Starting Apify Google Maps Scraper Actor...")

    run_input = {
        "searchStringsArray": SEARCH_TERMS,
        "maxCrawledPlacesPerSearch": 100,  # Increased from 50 to pull deeper results
        "language": "en",
        "allPlacesNoSubcategories": True,
    }

    # Execute Actor
    run = client.actor("compass/google-maps-extractor").call(run_input=run_input)

    lead_count = 0
    print("Scrape complete. Processing and filtering datasets...")

    dataset_items = client.dataset(run["defaultDatasetId"]).iterate_items()

    for item in dataset_items:
        rating = item.get("totalScore")
        phone = item.get("phone") or item.get("phoneUnformatted")
        company_name = item.get("title")
        category = item.get("categoryName") or "Local Service"

        # UPDATED FILTER: Must have phone AND rating strictly under 4.0 (Captures vulnerable businesses)
        if phone and rating is not None and rating < 4.0:
            payload = {
                "company_name": company_name,
                "phone": phone,
                "rating": rating,
                "reviews_count": item.get("reviewsCount", 0),
                "category": category,
                "website": item.get("website", ""),
                "address": item.get("address", ""),
                "vulnerability_tag": "High Call-Loss Risk (Sub-4.0 Rating)"
            }

            print(f"MATCH: {company_name} | Rating: {rating} | Phone: {phone} | Cat: {category}")

            if ZAPIER_WEBHOOK_URL:
                res = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
                if res.status_code == 200:
                    lead_count += 1

    print(f"Finished pipeline. Pushed {lead_count} low-rated leads to HubSpot.")

if __name__ == "__main__":
    run_apify_lead_pipeline()
