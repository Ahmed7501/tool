#!/usr/bin/env python3
"""
Google Maps Email Scraper
Extracts emails from business websites found via Google Maps URLs.
"""

import asyncio
import pandas as pd
import re
import logging
import time
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urljoin
import os
from pathlib import Path
import docx
import io

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmaps_scraper.log'),
        logging.StreamHandler()
    ]
)

class GoogleMapsEmailScraper:
    def __init__(self, delay_between_requests=3, timeout=15, wait_after_load=3):
        self.delay_between_requests = delay_between_requests
        self.timeout = timeout * 1000  # Convert to milliseconds
        self.wait_after_load = wait_after_load
        # Robust email regex that supports all TLDs
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        self.playwright = None
        self.browser = None

    async def init_browser(self):
        """Initialize Playwright browser."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
            )

    async def close_browser(self):
        """Close Playwright browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            self.browser = None

    def extract_emails(self, text):
        """Extract emails from text using robust regex."""
        if not text:
            return []
        
        emails = re.findall(self.email_pattern, text, re.IGNORECASE)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_emails = []
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                unique_emails.append(email)
        
        return unique_emails

    def is_google_maps_url(self, url):
        """Check if URL is a Google Maps URL."""
        if not url or pd.isna(url):
            return False
        url_str = str(url).lower()
        return 'google.com/maps' in url_str or 'maps.google.com' in url_str

    def detect_url_column(self, df):
        """Automatically detect the column containing URLs."""
        url_indicators = ['href', 'link', 'website', 'url', 'maps', 'google']
        
        for col in df.columns:
            col_lower = col.lower()
            # Check if column name contains URL indicators
            if any(indicator in col_lower for indicator in url_indicators):
                # Check if column contains Google Maps URLs
                if df[col].apply(self.is_google_maps_url).any():
                    logging.info(f"Detected URL column: {col}")
                    return col
        
        # If no obvious column found, check all columns for Google Maps URLs
        for col in df.columns:
            if df[col].apply(self.is_google_maps_url).any():
                logging.info(f"Detected URL column: {col}")
                return col
        
        return None

    async def extract_website_from_gmaps(self, page, gmaps_url):
        """Extract the website link from Google Maps listing."""
        try:
            logging.info(f"Loading Google Maps page: {gmaps_url}")
            
            # Navigate to Google Maps page
            await page.goto(gmaps_url, timeout=self.timeout, wait_until='domcontentloaded')
            
            # Wait for page to load
            await asyncio.sleep(self.wait_after_load)
            
            # Try to wait for network idle
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logging.info("Network idle timeout, continuing...")
            
            # Look for website link in various possible locations
            website_selectors = [
                'a[data-item-id="authority"]',  # Common Google Maps website link
                'a[aria-label*="website"]',     # Website link with aria-label
                'a[href*="http"]:not([href*="google.com"])',  # Any external link
                '[data-value*="http"]',         # Data attributes containing URLs
                'a[target="_blank"]',           # External links
            ]
            
            website_url = None
            
            for selector in website_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        if href and not self.is_google_maps_url(href):
                            website_url = href
                            logging.info(f"Found website URL: {website_url}")
                            break
                    if website_url:
                        break
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            # If no website found via selectors, try to extract from page text
            if not website_url:
                page_text = await page.evaluate("() => document.body.innerText")
                # Look for URLs in text content
                url_pattern = r'https?://[^\s<>"]+'
                urls = re.findall(url_pattern, page_text)
                for url in urls:
                    if not self.is_google_maps_url(url):
                        website_url = url
                        logging.info(f"Found website URL in text: {website_url}")
                        break
            
            return website_url
            
        except Exception as e:
            logging.error(f"Error extracting website from Google Maps {gmaps_url}: {str(e)}")
            return None

    async def scrape_emails_from_site(self, page, website_url):
        """Scrape visible email addresses from the website."""
        try:
            logging.info(f"Scraping emails from website: {website_url}")
            
            # Navigate to the website
            await page.goto(website_url, timeout=self.timeout, wait_until='domcontentloaded')
            
            # Wait for page to load
            await asyncio.sleep(self.wait_after_load)
            
            # Try to wait for network idle
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logging.info("Network idle timeout, continuing...")
            
            # Extract text content from the page
            text_content = await page.evaluate("""
                () => {
                    // Get all text content from the page
                    const bodyText = document.body ? document.body.innerText : '';
                    const headText = document.head ? document.head.innerText : '';
                    return bodyText + ' ' + headText;
                }
            """)
            
            # Extract emails from the text content
            emails = self.extract_emails(text_content)
            
            if emails:
                logging.info(f"Found {len(emails)} emails on {website_url}")
            else:
                logging.info(f"No emails found on {website_url}")
            
            return emails
            
        except Exception as e:
            logging.error(f"Error scraping emails from {website_url}: {str(e)}")
            return []

    async def process_single_url(self, page, gmaps_url, original_row):
        """Process a single Google Maps URL and extract emails."""
        try:
            # Extract website from Google Maps
            website_url = await self.extract_website_from_gmaps(page, gmaps_url)
            
            if not website_url:
                logging.warning(f"No website found for Google Maps URL: {gmaps_url}")
                return {
                    **original_row,
                    'Original_URL': gmaps_url,
                    'Website_URL': '',
                    'Found_Emails': '',
                    'Status': 'No website found'
                }
            
            # Add delay between requests
            await asyncio.sleep(self.delay_between_requests)
            
            # Scrape emails from the website
            emails = await self.scrape_emails_from_site(page, website_url)
            
            return {
                **original_row,
                'Original_URL': gmaps_url,
                'Website_URL': website_url,
                'Found_Emails': ', '.join(emails),
                'Status': f"{len(emails)} emails found" if emails else "No emails found"
            }
            
        except Exception as e:
            logging.error(f"Error processing {gmaps_url}: {str(e)}")
            return {
                **original_row,
                'Original_URL': gmaps_url,
                'Website_URL': '',
                'Found_Emails': '',
                'Status': f'Error: {str(e)}'
            }

    async def process_urls_async(self, df, url_column):
        """Process all URLs concurrently."""
        await self.init_browser()
        
        # Filter rows with Google Maps URLs
        gmaps_df = df[df[url_column].apply(self.is_google_maps_url)].copy()
        
        if gmaps_df.empty:
            logging.warning("No Google Maps URLs found in the file")
            return []
        
        logging.info(f"Found {len(gmaps_df)} Google Maps URLs to process")
        
        results = []
        
        # Process URLs sequentially to avoid rate limiting
        for index, row in gmaps_df.iterrows():
            try:
                # Create a new page for each request
                if self.browser is None:
                    raise Exception("Browser not initialized")
                page = await self.browser.new_page()
                
                # Set user agent to avoid detection
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # Process the URL
                result = await self.process_single_url(page, row[url_column], row.to_dict())
                results.append(result)
                
                await page.close()
                
                # Add delay between requests
                await asyncio.sleep(self.delay_between_requests)
                
            except Exception as e:
                logging.error(f"Error processing row {index}: {str(e)}")
                results.append({
                    **row.to_dict(),
                    'Original_URL': row[url_column],
                    'Website_URL': '',
                    'Found_Emails': '',
                    'Status': f'Error: {str(e)}'
                })
        
        return results

def read_input_file(filepath):
    """Detect file type and return a DataFrame."""
    filepath = Path(filepath)
    file_extension = filepath.suffix.lower()
    
    try:
        if file_extension in ['.xlsx', '.xls']:
            logging.info(f"Reading Excel file: {filepath}")
            return pd.read_excel(filepath)
        elif file_extension == '.csv':
            logging.info(f"Reading CSV file: {filepath}")
            return pd.read_csv(filepath)
        elif file_extension == '.docx':
            logging.info(f"Reading Word file: {filepath}")
            # Read Word document and extract text
            doc = docx.Document(str(filepath))
            text_content = []
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            
            # Create DataFrame with text content
            df = pd.DataFrame({'Content': text_content})
            
            # Extract URLs from text content
            url_pattern = r'https?://[^\s]+'
            urls = []
            for text in text_content:
                found_urls = re.findall(url_pattern, text)
                urls.extend(found_urls)
            
            # Create DataFrame with URLs
            if urls:
                df = pd.DataFrame({'URL': urls})
            else:
                df = pd.DataFrame({'Content': text_content})
            
            return df
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {str(e)}")
        raise

async def main():
    """Main function to run the Google Maps email scraper."""
    print("🚀 Google Maps Email Scraper")
    print("=" * 50)
    
    # Get input file path
    filepath = input("Enter the path to your input file (.xlsx, .csv, .docx): ").strip()
    
    if not filepath:
        print("No file path provided. Exiting.")
        return
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    try:
        # Read input file
        df = read_input_file(filepath)
        print(f"✅ Successfully loaded file with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        # Initialize scraper
        scraper = GoogleMapsEmailScraper()
        
        # Detect URL column
        url_column = scraper.detect_url_column(df)
        
        if not url_column:
            print("❌ No Google Maps URLs found in the file.")
            print("Please ensure your file contains a column with Google Maps URLs.")
            return
        
        print(f"🔍 Processing URLs from column: {url_column}")
        
        # Process URLs
        results = await scraper.process_urls_async(df, url_column)
        
        if not results:
            print("❌ No results to save.")
            return
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results
        results_df.to_excel('results.xlsx', index=False)
        results_df.to_csv('results.csv', index=False)
        
        print(f"✅ Results saved to:")
        print(f"   - results.xlsx ({len(results_df)} rows)")
        print(f"   - results.csv ({len(results_df)} rows)")
        
        # Show summary
        total_emails = sum(len(emails.split(',')) if emails else 0 for emails in results_df['Found_Emails'])
        websites_found = len(results_df[results_df['Website_URL'] != ''])
        
        print(f"\n📊 Summary:")
        print(f"   - URLs processed: {len(results_df)}")
        print(f"   - Websites found: {websites_found}")
        print(f"   - Total emails found: {total_emails}")
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        logging.error(f"Main error: {str(e)}")
    finally:
        await scraper.close_browser()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 