import os
from googleapiclient.discovery import build
from auth import get_credentials
import pandas as pd
from datetime import datetime, timedelta

# The user will need to provide their GA4 Property ID.
# This should be stored in an environment variable or a config file.
# For now, I'll add a placeholder and clear instructions.
GA4_PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "YOUR_GA4_PROPERTY_ID")

def get_ga4_data(credentials, property_id):
    """
    Fetches data from the Google Analytics 4 Data API.

    Args:
        credentials: The authenticated credentials object.
        property_id: The GA4 property ID (e.g., '123456789').

    Returns:
        A dictionary containing the fetched GA4 data.
    """
    if property_id == "YOUR_GA4_PROPERTY_ID":
        print("ERROR: GA4_PROPERTY_ID is not set.")
        print("Please set the GA4_PROPERTY_ID environment variable or replace the placeholder in ga4_data.py.")
        return None

    try:
        service = build('analyticsdata', 'v1beta', credentials=credentials)

        # Define the date range for the last week
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        date_range = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "name": "last_7_days"
        }

        # Run a batch report for all our requests
        response = service.properties().batchRunReports(
            property=f"properties/{property_id}",
            body={
                "requests": [
                    # Request 1: Total Users and New Users
                    {
                        "dateRanges": [date_range],
                        "metrics": [{"name": "totalUsers"}, {"name": "newUsers"}]
                    },
                    # Request 2: Top Traffic Channels by Sessions
                    {
                        "dateRanges": [date_range],
                        "dimensions": [{"name": "sessionDefaultChannelGroup"}],
                        "metrics": [{"name": "sessions"}],
                        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
                        "limit": 5
                    },
                    # Request 3: Top Pages by Views
                    {
                        "dateRanges": [date_range],
                        "dimensions": [{"name": "pageTitle"}],
                        "metrics": [{"name": "screenPageViews"}],
                        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
                        "limit": 5
                    }
                ]
            }
        ).execute()

        # Process the response
        ga4_data = {}

        # Process Report 1: User data
        report1 = response['reports'][0]
        ga4_data['total_users'] = report1.get('rows', [{}])[0].get('metricValues', [{}])[0].get('value', '0')
        ga4_data['new_users'] = report1.get('rows', [{}])[0].get('metricValues', [{}])[1].get('value', '0')

        # Process Report 2: Traffic sources
        report2 = response['reports'][1]
        headers = [header['name'] for header in report2.get('dimensionHeaders', []) + report2.get('metricHeaders', [])]
        rows = []
        for row in report2.get('rows', []):
            rows.append([dv['value'] for dv in row.get('dimensionValues', [])] + [mv['value'] for mv in row.get('metricValues', [])])
        ga4_data['traffic_sources'] = pd.DataFrame(rows, columns=headers) if rows else pd.DataFrame(columns=headers)

        # Process Report 3: Top pages
        report3 = response['reports'][2]
        headers = [header['name'] for header in report3.get('dimensionHeaders', []) + report3.get('metricHeaders', [])]
        rows = []
        for row in report3.get('rows', []):
            rows.append([dv['value'] for dv in row.get('dimensionValues', [])] + [mv['value'] for mv in row.get('metricValues', [])])
        ga4_data['top_pages'] = pd.DataFrame(rows, columns=headers) if rows else pd.DataFrame(columns=headers)

        return ga4_data

    except Exception as e:
        print(f"An error occurred while fetching GA4 data: {e}")
        return None

if __name__ == '__main__':
    print("Attempting to fetch GA4 data...")
    creds = get_credentials()
    if creds:
        # IMPORTANT: You must set your GA4 Property ID here for testing
        ga4_property_id = GA4_PROPERTY_ID

        if ga4_property_id == "YOUR_GA4_PROPERTY_ID":
            print("Please configure your GA4 Property ID in `ga4_data.py` before running this test.")
        else:
            data = get_ga4_data(creds, ga4_property_id)
            if data:
                print("\n--- GA4 Data ---")
                print(f"Total Users: {data['total_users']}")
                print(f"New Users: {data['new_users']}")
                print("\nTop Traffic Sources:")
                print(data['traffic_sources'].to_string(index=False))
                print("\nTop Pages:")
                print(data['top_pages'].to_string(index=False))
                print("\n------------------")
