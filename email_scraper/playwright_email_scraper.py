#!/usr/bin/env python3
"""
Playwright-based Email Scraper
Handles JavaScript-rendered content and extracts emails with robust regex.
"""

import asyncio
import re
import logging
from playwright.async_api import async_playwright
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PlaywrightEmailScraper:
    def __init__(self, timeout=15, wait_after_load=3):
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
                args=['--no-sandbox', '--disable-dev-shm-usage']
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

    async def extract_emails_from_url(self, url):
        """Extract emails from a URL using Playwright."""
        try:
            await self.init_browser()
            
            # Create a new page
            page = await self.browser.new_page()
            
            # Set user agent to avoid detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            logging.info(f"Loading page: {url}")
            
            # Navigate to the page with timeout
            try:
                await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')
            except Exception as e:
                logging.error(f"Failed to load {url}: {str(e)}")
                await page.close()
                return []
            
            # Wait for additional time to allow JavaScript to populate content
            logging.info(f"Waiting {self.wait_after_load} seconds for JS content...")
            await asyncio.sleep(self.wait_after_load)
            
            # Try to wait for page to be fully loaded
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logging.info(f"Network idle timeout for {url}, continuing...")
            
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
            
            # Log results
            if emails:
                logging.info(f"Found {len(emails)} emails on {url}")
            else:
                logging.info(f"No emails found on {url}")
            
            await page.close()
            return emails
                    
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return []

async def main():
    """Main function to run the email scraper."""
    scraper = PlaywrightEmailScraper()
    
    try:
        # Get URL from user input
        url = input("Enter the URL: ").strip()
        
        if not url:
            print("No URL provided. Exiting.")
            return
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        print(f"Scraping emails from: {url}")
        print("Loading page and waiting for JavaScript content...")
        
        # Extract emails
        emails = await scraper.extract_emails_from_url(url)
        
        # Display results
        if emails:
            print(f"\n✅ Found {len(emails)} unique email(s):")
            for i, email in enumerate(emails, 1):
                print(f"  {i}. {email}")
        else:
            print("\n❌ No emails found on this page.")
            print("This could be because:")
            print("  - The page doesn't contain any email addresses")
            print("  - Emails are loaded dynamically and not visible")
            print("  - The page has anti-scraping protection")
            print("  - The page failed to load properly")
    
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
    finally:
        await scraper.close_browser()

if __name__ == "__main__":
    print("🚀 Playwright Email Scraper")
    print("=" * 40)
    print("This scraper can handle JavaScript-rendered content!")
    print("=" * 40)
    
    # Run the async main function
    asyncio.run(main()) 