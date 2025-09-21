import os
from googleapiclient.discovery import build
from auth import get_credentials
import pandas as pd
from datetime import datetime, timedelta

# The user will need to provide their GMB Account and Location ID.
# Instructions on how to find these will be in the README.md.
GMB_ACCOUNT_ID = os.environ.get("GMB_ACCOUNT_ID", "YOUR_GMB_ACCOUNT_ID")
GMB_LOCATION_ID = os.environ.get("GMB_LOCATION_ID", "YOUR_GMB_LOCATION_ID")

def get_gmb_data(credentials, account_id, location_id):
    """
    Fetches data from the Google Business Profile APIs.

    Args:
        credentials: The authenticated credentials object.
        account_id: The GMB Account ID.
        location_id: The GMB Location ID for the specific business.

    Returns:
        A dictionary containing the fetched GMB data.
    """
    if account_id == "YOUR_GMB_ACCOUNT_ID" or location_id == "YOUR_GMB_LOCATION_ID":
        print("ERROR: GMB_ACCOUNT_ID or GMB_LOCATION_ID is not set.")
        print("Please set these as environment variables or replace the placeholders in gmb_data.py.")
        return None

    gmb_data = {
        'search_views': 0,
        'maps_views': 0,
        'website_visits': 0,
        'phone_calls': 0,
        'direction_requests': 0,
        'average_rating': 'N/A',
        'latest_reviews': pd.DataFrame()
    }

    parent_path = f"accounts/{account_id}/locations/{location_id}"
    location_path = f"locations/{location_id}"

    try:
        # --- 1. Fetch Performance Metrics ---
        performance_service = build('businessprofileperformance', 'v1', credentials=credentials)

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        daily_metrics = [
            "BUSINESS_IMPRESSIONS_DESKTOP_MAPS", "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH",
            "BUSINESS_IMPRESSIONS_MOBILE_MAPS", "BUSINESS_IMPRESSIONS_MOBILE_SEARCH",
            "WEBSITE_CLICKS", "CALL_CLICKS", "DRIVING_DIRECTIONS_REQUESTS"
        ]

        total_metrics = {}
        for metric in daily_metrics:
            # Note: The Python client library may not have keyword args for all URL params.
            # This is a robust way to make the call.
            request = performance_service.locations().getDailyMetricsTimeSeries(
                name=location_path,
                dailyMetric=metric,
                **{
                    'dailyRange.startDate.year': start_date.year,
                    'dailyRange.startDate.month': start_date.month,
                    'dailyRange.startDate.day': start_date.day,
                    'dailyRange.endDate.year': end_date.year,
                    'dailyRange.endDate.month': end_date.month,
                    'dailyRange.endDate.day': end_date.day
                }
            )
            response = request.execute()

            total_value = 0
            if 'timeSeries' in response and 'datedValues' in response['timeSeries']:
                total_value = sum(int(dp.get('value', 0)) for dp in response['timeSeries']['datedValues'])
            total_metrics[metric] = total_value

        gmb_data['search_views'] = total_metrics.get("BUSINESS_IMPRESSIONS_DESKTOP_SEARCH", 0) + total_metrics.get("BUSINESS_IMPRESSIONS_MOBILE_SEARCH", 0)
        gmb_data['maps_views'] = total_metrics.get("BUSINESS_IMPRESSIONS_DESKTOP_MAPS", 0) + total_metrics.get("BUSINESS_IMPRESSIONS_MOBILE_MAPS", 0)
        gmb_data['website_visits'] = total_metrics.get("WEBSITE_CLICKS", 0)
        gmb_data['phone_calls'] = total_metrics.get("CALL_CLICKS", 0)
        gmb_data['direction_requests'] = total_metrics.get("DRIVING_DIRECTIONS_REQUESTS", 0)

        # --- 2. Fetch Reviews ---
        reviews_service = build('mybusinessreviews', 'v1', credentials=credentials)
        response_reviews = reviews_service.accounts().locations().reviews().list(
            parent=parent_path,
            pageSize=5, # Get the 5 most recent reviews
            orderBy='updateTime desc'
        ).execute()

        if 'reviews' in response_reviews and response_reviews['reviews']:
            reviews = response_reviews['reviews']
            # Filter out reviews without a star rating before calculating average
            rated_reviews = [r for r in reviews if 'starRating' in r]
            if rated_reviews:
                total_rating = sum(int(r['starRating'].replace('STAR_', '')) for r in rated_reviews)
                gmb_data['average_rating'] = f"{total_rating / len(rated_reviews):.1f}"

            review_list = []
            for review in reviews:
                comment = (review.get('comment', 'No comment') or 'No comment')
                review_list.append({
                    'Rating': review.get('starRating', 'N/A').replace('STAR_', ''),
                    'Reviewer': review.get('reviewer', {}).get('displayName', 'Anonymous'),
                    'Comment': (comment[:97] + '...') if len(comment) > 100 else comment
                })
            gmb_data['latest_reviews'] = pd.DataFrame(review_list)

    except Exception as e:
        print(f"An error occurred while fetching GMB data: {e}")
        return None

    return gmb_data

if __name__ == '__main__':
    print("Attempting to fetch GMB/Business Profile data...")
    creds = get_credentials()
    if creds:
        account_id = GMB_ACCOUNT_ID
        location_id = GMB_LOCATION_ID
        if account_id == "YOUR_GMB_ACCOUNT_ID" or location_id == "YOUR_GMB_LOCATION_ID":
            print("Please configure your GMB Account and Location IDs in `gmb_data.py` before running this test.")
        else:
            data = get_gmb_data(creds, account_id, location_id)
            if data:
                print("\n--- GMB Data ---")
                print(f"Search Views: {data['search_views']}")
                print(f"Map Views: {data['maps_views']}")
                print(f"Website Visits: {data['website_visits']}")
                print(f"Phone Calls: {data['phone_calls']}")
                print(f"Direction Requests: {data['direction_requests']}")
                print(f"Average Rating from last 5 reviews: {data['average_rating']}")
                print("\nLatest Reviews:")
                if not data['latest_reviews'].empty:
                    print(data['latest_reviews'].to_string(index=False))
                else:
                    print("No recent reviews found.")
                print("\n------------------")
