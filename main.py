from datetime import datetime
import os
from auth import get_credentials
from ga4_data import get_ga4_data
from gsc_data import get_gsc_data
from gmb_data import get_gmb_data
from generate_pdf import create_report

# --- CONFIGURATION ---
# The script pulls configuration from environment variables. This is a best
# practice for keeping secrets and settings out of the code. The user will
# be instructed on how to set these in the README.md file.
GA4_PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID")
GSC_SITE_URL = os.environ.get("GSC_SITE_URL")
GMB_ACCOUNT_ID = os.environ.get("GMB_ACCOUNT_ID")
GMB_LOCATION_ID = os.environ.get("GMB_LOCATION_ID")

def main():
    """
    Main function to orchestrate the report generation process.
    """
    print("--- Starting Weekly Report Generation ---")

    # 1. Check for necessary configuration from environment variables
    if not all([GA4_PROPERTY_ID, GSC_SITE_URL, GMB_ACCOUNT_ID, GMB_LOCATION_ID]):
        print("\nERROR: Missing configuration.")
        print("Please ensure the following environment variables are set:")
        print("- GA4_PROPERTY_ID")
        print("- GSC_SITE_URL")
        print("- GMB_ACCOUNT_ID")
        print("- GMB_LOCATION_ID")
        print("\nRefer to the README.md file for instructions on how to set them.")
        return # Exit if configuration is incomplete

    # 2. Authenticate with Google APIs
    print("\nStep 1: Authenticating with Google...")
    creds = get_credentials()
    if not creds:
        print("Authentication failed. Please run `python auth.py` first or check your `credentials.json` file.")
        return
    print("Authentication successful.")

    # 3. Fetch data from all Google services
    print("\nStep 2: Fetching data from Google services...")

    print("  - Fetching Google Analytics 4 data...")
    ga4_data = get_ga4_data(creds, GA4_PROPERTY_ID)
    if ga4_data:
        print("    ...GA4 data fetched successfully.")
    else:
        print("    ...Warning: Failed to fetch GA4 data. Section will be empty.")

    print("  - Fetching Google Search Console data...")
    gsc_data = get_gsc_data(creds, GSC_SITE_URL)
    if gsc_data:
        print("    ...GSC data fetched successfully.")
    else:
        print("    ...Warning: Failed to fetch GSC data. Section will be empty.")

    print("  - Fetching Google Business Profile data...")
    gmb_data = get_gmb_data(creds, GMB_ACCOUNT_ID, GMB_LOCATION_ID)
    if gmb_data:
        print("    ...GMB data fetched successfully.")
    else:
        print("    ...Warning: Failed to fetch GMB data. Section will be empty.")

    # 4. Generate the final PDF report
    print("\nStep 3: Generating the PDF report...")
    try:
        # Define the output filename
        output_filename = f"Weekly_Report_{GA4_PROPERTY_ID}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        create_report(ga4_data, gsc_data, gmb_data, filename=output_filename)
    except Exception as e:
        print(f"An error occurred during PDF generation: {e}")
        return

    print("\n--- Weekly Report Generation Complete ---")


if __name__ == '__main__':
    main()
