# Bulk Email Scraper

A web application for scraping email addresses from multiple URLs in bulk. The app supports various file formats and provides a user-friendly interface for uploading files and downloading results.

## 🆕 Playwright Email Scraper

This project now includes a **Playwright-based email scraper** that can handle JavaScript-rendered content! The new scraper:

- ✅ **Handles JavaScript-rendered pages** - No more missed emails from dynamic content
- ✅ **Robust email regex** - Supports all TLDs (`.com`, `.online`, `.agency`, etc.)
- ✅ **Graceful error handling** - Handles timeouts, connection errors, and invalid pages
- ✅ **Clear logging** - Shows exactly what's happening during scraping
- ✅ **Duplicate removal** - Automatically removes duplicate emails
- ✅ **Simple to use** - Single file, user inputs URL

### Quick Start (Playwright Scraper)

1. **Install dependencies:**
   ```bash
   pip install playwright
   ```

2. **Setup Playwright browsers:**
   ```bash
   python setup_playwright.py
   ```

3. **Run the scraper:**
   ```bash
   python playwright_email_scraper.py
   ```

4. **Enter a URL when prompted** and watch it extract emails from JavaScript-rendered content!

### Features of the Playwright Scraper

- **15-second timeout** for page loading
- **3-5 second wait** after page load for JavaScript content
- **Network idle detection** for fully loaded pages
- **User agent spoofing** to avoid detection
- **Comprehensive error handling** with detailed logging
- **Duplicate email removal** while preserving order

## 🗺️ Google Maps Email Scraper

A specialized scraper that processes Google Maps URLs and extracts emails from business websites.

### Features

- ✅ **Multi-format input** - Supports `.xlsx`, `.csv`, `.docx` files
- ✅ **Automatic URL detection** - Finds Google Maps URLs in any column
- ✅ **Website extraction** - Extracts business websites from Google Maps listings
- ✅ **Email scraping** - Scrapes emails from business websites using Playwright
- ✅ **Dual output** - Saves results to both `.xlsx` and `.csv` formats
- ✅ **Comprehensive logging** - Detailed progress and error reporting
- ✅ **Rate limiting** - Built-in delays to avoid being blocked
- ✅ **Error handling** - Graceful handling of missing websites and failed scrapes

### Quick Start (Google Maps Scraper)

1. **Setup the scraper:**
   ```bash
   python setup_gmaps_scraper.py
   ```

2. **Run the scraper:**
   ```bash
   python gmaps_email_scraper.py
   ```

3. **Enter your input file path** when prompted (e.g., `google.xlsx`)

4. **Results will be saved** to `results.xlsx` and `results.csv`

### Input File Format

Your input file should contain Google Maps URLs in any column. The scraper will automatically detect columns with names like:
- `href`
- `Link` 
- `Website`
- `URL`
- `Maps`
- `Google`

Or any column containing Google Maps URLs.

### Output Format

The results include:
- **Original row data** (Title, Phone, Address, etc.)
- **Original_URL** - The Google Maps URL
- **Website_URL** - The extracted business website
- **Found_Emails** - Comma-separated list of emails
- **Status** - Success/error status message

## Features

- Support for multiple file formats (TXT, Excel, Word)
- Concurrent URL processing for faster scraping
- User-friendly web interface
- Progress tracking and statistics
- CSV export functionality
- Configurable scraping options

## Live Demo

The application is deployed on Streamlit Cloud:
[View Live Demo](https://your-app-name.streamlit.app)

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/email-scraper.git
cd email-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Deployment

This application is deployed using Streamlit Cloud. To deploy your own version:

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and main file (app.py)
6. Click "Deploy"

## Project Structure

```
email-scraper/
├── app.py                 # Main Streamlit application
├── email_scraper/         # Scraper package
│   ├── __init__.py
│   └── scraper.py        # Core scraping functionality
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Usage

1. Open the web interface
2. Upload a file containing URLs (TXT, Excel, or Word)
3. Configure scraping options (delay and concurrency)
4. Click "Start Scraping"
5. View results and download CSV

## Configuration

The application allows you to configure:
- Delay between requests (0.1-2.0 seconds)
- Maximum concurrent requests (1-20)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Legal Disclaimer

This tool is for educational purposes only. Make sure you have permission to scrape the target websites and comply with their terms of service and robots.txt files. The user is responsible for ensuring compliance with applicable laws and regulations. 