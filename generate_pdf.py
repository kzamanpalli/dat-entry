from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime, timedelta
import pandas as pd

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 18)
        self.cell(0, 10, "Weekly Performance Report", border=0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        date_range_str = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"

        self.set_font("helvetica", "", 11)
        self.cell(0, 10, date_range_str, border=0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("helvetica", "B", 14)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 10, f" {title}", align="L", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def sub_section_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, title, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def key_value(self, key, value):
        self.set_font("helvetica", "B", 11)
        self.cell(60, 8, f"{key}:")
        self.set_font("helvetica", "", 11)
        self.cell(0, 8, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def dataframe_to_table(self, df):
        if not isinstance(df, pd.DataFrame) or df.empty:
            self.set_font("helvetica", "I", 10)
            self.cell(0, 10, "No data available.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return

        self.set_font("helvetica", "B", 9)
        self.set_fill_color(240, 240, 240)

        col_widths = []
        for col in df.columns:
            col_widths.append(self.get_string_width(col) + 6)

        total_width = sum(col_widths)
        available_width = self.w - self.l_margin - self.r_margin
        scaling_factor = available_width / total_width if total_width > 0 else 1
        final_widths = [w * scaling_factor for w in col_widths]

        for i, col in enumerate(df.columns):
            self.cell(final_widths[i], 8, col, border=1, fill=True, align="C")
        self.ln()

        self.set_font("helvetica", "", 8)
        for _, row in df.iterrows():
            for i, item in enumerate(row):
                self.cell(final_widths[i], 7, str(item), border=1)
            self.ln()
        self.ln(5)

    def add_ga4_section(self, data):
        self.add_page()
        self.section_title("Website Performance (Google Analytics 4)")
        if not data:
            self.cell(0, 10, "Could not retrieve GA4 data.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return

        self.key_value("Total Website Visitors", data.get('total_users', 'N/A'))
        self.key_value("New Visitors", data.get('new_users', 'N/A'))
        self.ln(5)

        self.sub_section_title("Top Traffic Sources")
        self.dataframe_to_table(data.get('traffic_sources', pd.DataFrame()))

        self.sub_section_title("Most Popular Pages")
        self.dataframe_to_table(data.get('top_pages', pd.DataFrame()))

    def add_gsc_section(self, data):
        self.add_page()
        self.section_title("Google Search Visibility (Search Console)")
        if not data:
            self.cell(0, 10, "Could not retrieve GSC data.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return

        self.key_value("Clicks from Google Search", f"{data.get('clicks', 0):.0f}")
        self.key_value("Impressions in Search", f"{data.get('impressions', 0):.0f}")
        self.key_value("Average Click-Through Rate", f"{data.get('ctr', 0) * 100:.2f}%")
        self.ln(5)

        self.sub_section_title("Top Search Terms")
        self.dataframe_to_table(data.get('top_queries', pd.DataFrame()))

    def add_gmb_section(self, data):
        self.add_page()
        self.section_title("Local Business Presence (Google Business Profile)")
        if not data:
            self.cell(0, 10, "Could not retrieve GMB data.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return

        self.key_value("Views on Google Search", data.get('search_views', 'N/A'))
        self.key_value("Views on Google Maps", data.get('maps_views', 'N/A'))
        self.key_value("Website Visits from Profile", data.get('website_visits', 'N/A'))
        self.key_value("Phone Calls", data.get('phone_calls', 'N/A'))
        self.key_value("Direction Requests", data.get('direction_requests', 'N/A'))
        self.key_value("Avg. Rating (from recent reviews)", data.get('average_rating', 'N/A'))
        self.ln(5)

        self.sub_section_title("Latest Reviews")
        self.dataframe_to_table(data.get('latest_reviews', pd.DataFrame()))

def create_report(ga4_data, gsc_data, gmb_data, filename="weekly_report.pdf"):
    pdf = PDF()
    pdf.add_ga4_section(ga4_data)
    pdf.add_gsc_section(gsc_data)
    pdf.add_gmb_section(gmb_data)
    pdf.output(filename)
    print(f"Report successfully generated: {filename}")

if __name__ == '__main__':
    print("Generating a sample PDF report...")
    dummy_ga4 = {
        'total_users': 1500, 'new_users': 1200,
        'traffic_sources': pd.DataFrame({'Channel': ['Organic', 'Direct', 'Referral'], 'Sessions': [800, 400, 300]}),
        'top_pages': pd.DataFrame({'Page': ['Home', 'About', 'Contact'], 'Views': [1000, 300, 200]})
    }
    dummy_gsc = {
        'clicks': 500, 'impressions': 10000, 'ctr': 0.05,
        'top_queries': pd.DataFrame({'Query': ['widgets', 'buy widgets', 'local widgets'], 'Clicks': [150, 100, 50]})
    }
    dummy_gmb = {
        'search_views': 2000, 'maps_views': 1500, 'website_visits': 150, 'phone_calls': 50,
        'direction_requests': 75, 'average_rating': '4.5',
        'latest_reviews': pd.DataFrame({'Rating': ['5', '4'], 'Reviewer': ['John D.', 'Jane S.'], 'Comment': ['Great!', 'Helpful.']})
    }
    create_report(dummy_ga4, dummy_gsc, dummy_gmb, "sample_report.pdf")
