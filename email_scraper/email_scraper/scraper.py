import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from tqdm import tqdm
import os
from urllib.parse import urlparse
import logging
from concurrent.futures import ThreadPoolExecutor

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
    def __init__(self, delay=0.5, max_concurrent=10):
        self.delay = delay
        self.max_concurrent = max_concurrent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.session = None

    async def init_session(self):
        """Initialize aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    def extract_emails(self, text):
        """Extract emails from text using regex."""
        return list(set(re.findall(self.email_pattern, text)))

    def get_domain_name(self, url):
        """Extract domain name from URL."""
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except:
            return url

    async def scrape_url(self, url):
        """Scrape emails from a single URL using async."""
        try:
            await self.init_session()
            
            if not self.session:
                raise Exception("Failed to initialize session")

            timeout = aiohttp.ClientTimeout(total=10)
            async with self.session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Get page title for business name
                    title = soup.title.string if soup.title else ''
                    
                    # Extract emails from text content
                    text_content = soup.get_text()
                    emails = self.extract_emails(text_content)
                    
                    # Get domain name
                    domain = self.get_domain_name(url)
                    
                    return {
                        'url': url,
                        'business': title.strip() if title else domain,
                        'emails': ', '.join(emails),
                        'domain': domain
                    }
                else:
                    logging.warning(f"HTTP {response.status} for {url}")
                    return {
                        'url': url,
                        'business': self.get_domain_name(url),
                        'emails': '',
                        'domain': self.get_domain_name(url)
                    }
                    
        except asyncio.TimeoutError:
            logging.error(f"Timeout error scraping {url}")
            return {
                'url': url,
                'business': self.get_domain_name(url),
                'emails': '',
                'domain': self.get_domain_name(url)
            }
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'business': self.get_domain_name(url),
                'emails': '',
                'domain': self.get_domain_name(url)
            }

    async def process_urls_async(self, urls):
        """Process URLs concurrently using asyncio."""
        tasks = []
        for url in urls:
            tasks.append(self.scrape_url(url))
            await asyncio.sleep(self.delay)  # Rate limiting
        
        results = await asyncio.gather(*tasks)
        return results

    def process_urls(self, input_file, output_file):
        """Process URLs from input file and save results to CSV."""
        try:
            # Read URLs from file
            with open(input_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]

            # Create event loop and run async processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(self.process_urls_async(urls))
            finally:
                loop.run_until_complete(self.close_session())
                loop.close()

            # Create DataFrame and save to CSV
            df = pd.DataFrame(results)
            
            # Ensure all required columns exist
            required_columns = ['url', 'business', 'emails', 'domain']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Ensure emails column is string type
            df['emails'] = df['emails'].fillna('').astype(str)
            
            df.to_csv(output_file, index=False)
            logging.info(f"Results saved to {output_file}")
            
            return len(results)
            
        except Exception as e:
            logging.error(f"Error processing URLs: {str(e)}")
            return 0 