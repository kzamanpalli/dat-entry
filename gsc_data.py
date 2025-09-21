import os
from googleapiclient.discovery import build
from auth import get_credentials
import pandas as pd
from datetime import datetime, timedelta

# The user will need to provide their GSC Site URL.
# This should be the full URL of the property as it appears in Google Search Console.
GSC_SITE_URL = os.environ.get("GSC_SITE_URL", "YOUR_GSC_SITE_URL")

def get_gsc_data(credentials, site_url):
    """
    Fetches data from the Google Search Console API.

    Args:
        credentials: The authenticated credentials object.
        site_url: The full URL of the GSC property (e.g., 'https://www.example.com/').

    Returns:
        A dictionary containing the fetched GSC data.
    """
    if site_url == "YOUR_GSC_SITE_URL":
        print("ERROR: GSC_SITE_URL is not set.")
        print("Please set the GSC_SITE_URL environment variable or replace the placeholder in gsc_data.py.")
        return None

    try:
        service = build('webmasters', 'v3', credentials=credentials)

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        # 1. Get total clicks, impressions, ctr for the site
        request_totals = {
            'startDate': start_date.strftime("%Y-%m-%d"),
            'endDate': end_date.strftime("%Y-%m-%d"),
        }
        response_totals = service.searchanalytics().query(siteUrl=site_url, body=request_totals).execute()

        gsc_data = {
            'clicks': 0,
            'impressions': 0,
            'ctr': 0,
            'top_queries': pd.DataFrame()
        }

        if 'rows' in response_totals and response_totals['rows']:
            totals = response_totals['rows'][0]
            gsc_data['clicks'] = totals['clicks']
            gsc_data['impressions'] = totals['impressions']
            gsc_data['ctr'] = totals['ctr']

        # 2. Get top 5 queries by clicks
        request_queries = {
            'startDate': start_date.strftime("%Y-%m-%d"),
            'endDate': end_date.strftime("%Y-%m-%d"),
            'dimensions': ['query'],
            'rowLimit': 5,
            'startRow': 0
        }
        response_queries = service.searchanalytics().query(siteUrl=site_url, body=request_queries).execute()

        if 'rows' in response_queries and response_queries['rows']:
            rows = []
            for row in response_queries['rows']:
                rows.append({
                    'Query': row['keys'][0],
                    'Clicks': row['clicks'],
                    'Impressions': row['impressions']
                })
            gsc_data['top_queries'] = pd.DataFrame(rows)

        return gsc_data

    except Exception as e:
        print(f"An error occurred while fetching GSC data: {e}")
        return None

if __name__ == '__main__':
    print("Attempting to fetch GSC data...")
    creds = get_credentials()
    if creds:
        site_url = GSC_SITE_URL
        if site_url == "YOUR_GSC_SITE_URL":
            print("Please configure your GSC Site URL in `gsc_data.py` before running this test.")
        else:
            data = get_gsc_data(creds, site_url)
            if data:
                print("\n--- GSC Data ---")
                print(f"Total Clicks: {data['clicks']:.0f}")
                print(f"Total Impressions: {data['impressions']:.0f}")
                print(f"Average CTR: {data['ctr'] * 100:.2f}%")
                print("\nTop Queries:")
                if not data['top_queries'].empty:
                    print(data['top_queries'].to_string(index=False))
                else:
                    print("No query data available.")
                print("\n------------------")
