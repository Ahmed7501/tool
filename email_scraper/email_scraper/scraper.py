import asyncio
import pandas as pd
import re
import time
from tqdm import tqdm
import os
from urllib.parse import urlparse
import logging
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class EmailScraper:
    def __init__(self, delay=0.5, max_concurrent=10, timeout=15, wait_after_load=3):
        self.delay = delay
        self.max_concurrent = max_concurrent
        self.timeout = timeout * 1000  # Convert to milliseconds for Playwright
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

    def get_domain_name(self, url):
        """Extract domain name from URL."""
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except:
            return url

    async def scrape_url(self, url):
        """Scrape emails from a single URL using Playwright."""
        try:
            await self.init_browser()
            
            if not self.browser:
                raise Exception("Failed to initialize browser")
            
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
                logging.warning(f"Failed to load {url}: {str(e)}")
                await page.close()
                return {
                    'url': url,
                    'business': self.get_domain_name(url),
                    'emails': '',
                    'domain': self.get_domain_name(url),
                    'error': f'Page load failed: {str(e)}'
                }
            
            # Wait for additional time to allow JavaScript to populate content
            logging.info(f"Waiting {self.wait_after_load} seconds for JS content...")
            await asyncio.sleep(self.wait_after_load)
            
            # Try to wait for page to be fully loaded
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logging.info(f"Network idle timeout for {url}, continuing...")
            
            # Get page title for business name
            title = await page.title()
            
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
            
            # Get domain name
            domain = self.get_domain_name(url)
            
            # Log results
            if emails:
                logging.info(f"Found {len(emails)} emails on {url}")
            else:
                logging.info(f"No emails found on {url}")
            
            await page.close()
            
            return {
                'url': url,
                'business': title.strip() if title else domain,
                'emails': ', '.join(emails),
                'domain': domain,
                'error': ''
            }
                    
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'business': self.get_domain_name(url),
                'emails': '',
                'domain': self.get_domain_name(url),
                'error': f'Scraping error: {str(e)}'
            }

    async def process_urls_async(self, urls):
        """Process URLs concurrently using asyncio with semaphore for concurrency control."""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                result = await self.scrape_url(url)
                await asyncio.sleep(self.delay)  # Rate limiting
                return result
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Exception processing {urls[i]}: {str(result)}")
                processed_results.append({
                    'url': urls[i],
                    'business': self.get_domain_name(urls[i]),
                    'emails': '',
                    'domain': self.get_domain_name(urls[i]),
                    'error': f'Exception: {str(result)}'
                })
            else:
                processed_results.append(result)
        
        return processed_results

    def process_urls(self, input_file, output_file):
        """Process URLs from input file and save results to CSV."""
        try:
            # Read URLs from file
            with open(input_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]

            logging.info(f"Starting to process {len(urls)} URLs...")

            # Create event loop and run async processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(self.process_urls_async(urls))
            finally:
                loop.run_until_complete(self.close_browser())
                loop.close()

            # Create DataFrame and save to CSV
            df = pd.DataFrame(results)
            
            # Ensure all required columns exist
            required_columns = ['url', 'business', 'emails', 'domain', 'error']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Ensure emails column is string type
            df['emails'] = df['emails'].fillna('').astype(str)
            
            df.to_csv(output_file, index=False)
            logging.info(f"Results saved to {output_file}")
            
            # Log summary
            successful_scrapes = len(df[df['error'] == ''])
            total_emails = sum(len(emails.split(',')) if emails else 0 for emails in df['emails'])
            logging.info(f"Scraping completed: {successful_scrapes}/{len(urls)} URLs successful, {total_emails} total emails found")
            
            return len(results)
            
        except Exception as e:
            logging.error(f"Error processing URLs: {str(e)}")
            return 0 