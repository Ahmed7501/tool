import streamlit as st
import pandas as pd
import tempfile
import os
import docx
import io
import time
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Define a base EmailScraper class for type hints
class EmailScraper:
    def __init__(self, delay: float = 0.5, max_concurrent: int = 10):
        pass
    
    def process_urls(self, input_file: str, output_file: str) -> int:
        return 0

try:
    from email_scraper.scraper import EmailScraper as RealEmailScraper
    EmailScraper = RealEmailScraper  # type: ignore
except ImportError:
    try:
        # Try direct import from current directory
        from scraper import EmailScraper as RealEmailScraper  # type: ignore
        EmailScraper = RealEmailScraper  # type: ignore
    except ImportError:
        # Use the placeholder class defined above
        pass

# Configure Streamlit page
st.set_page_config(
    page_title="Bulk Email Scraper",
    layout="centered",
    initial_sidebar_state="expanded"
)

# File size limit is configured in .streamlit/config.toml

def extract_urls_from_txt(file_content):
    """Extract URLs from text file content."""
    return [line.strip() for line in file_content.decode('utf-8').splitlines() if line.strip()]

def extract_urls_from_excel(file_content):
    """Extract URLs from Excel file content."""
    df = pd.read_excel(file_content)
    # Try to find URL column
    url_columns = [col for col in df.columns if 'url' in col.lower()]
    if url_columns:
        return df[url_columns[0]].dropna().tolist()
    # If no URL column found, try to find URLs in all columns
    urls = []
    for col in df.columns:
        urls.extend(df[col].astype(str).str.extract(r'(https?://\S+)')[0].dropna().tolist())
    return list(set(urls))

def extract_urls_from_docx(file_content):
    """Extract URLs from Word document content."""
    doc = docx.Document(io.BytesIO(file_content))
    urls = []
    for paragraph in doc.paragraphs:
        urls.extend([url.strip() for url in paragraph.text.split() if url.startswith(('http://', 'https://'))])
    return list(set(urls))

def process_file(uploaded_file):
    """Process uploaded file and extract URLs."""
    file_content = uploaded_file.read()
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'txt':
            urls = extract_urls_from_txt(file_content)
        elif file_extension in ['xlsx', 'xls']:
            urls = extract_urls_from_excel(file_content)
        elif file_extension == 'docx':
            urls = extract_urls_from_docx(file_content)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None
        
        if not urls:
            st.warning("No URLs found in the file.")
            return None
            
        return urls
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

# Main app interface
st.title("Bulk Email Scraper")
st.write("Upload a file containing URLs (supported formats: TXT, Excel, Word)")

# File uploader with multiple file types
uploaded_file = st.file_uploader(
    "Upload your file",
    type=['txt', 'xlsx', 'xls', 'docx'],
    help="Upload a file containing URLs. Supported formats: TXT, Excel (XLSX/XLS), Word (DOCX)"
)

if uploaded_file:
    st.write(f"File uploaded: {uploaded_file.name}")
    
    # Process the file
    urls = process_file(uploaded_file)
    
    if urls:
        st.write(f"Found {len(urls)} URLs in the file")
        
        # Show preview of URLs
        with st.expander("Preview URLs"):
            st.write(urls[:10])
            if len(urls) > 10:
                st.write(f"... and {len(urls) - 10} more URLs")
        
        # Scraping options
        st.write("### Scraping Options")
        col1, col2 = st.columns(2)
        with col1:
            delay = st.slider("Delay between requests (seconds)", 0.1, 2.0, 0.5, 0.1)
        with col2:
            max_concurrent = st.slider("Max concurrent requests", 1, 20, 10, 1)
        
        if st.button("Start Scraping"):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("Scraping emails. Please wait..."):
                # Create temporary files
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                    tmp.write('\n'.join(urls).encode('utf-8'))
                    tmp_path = tmp.name
                
                output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name
                
                # Initialize scraper with custom settings
                scraper = EmailScraper(delay=delay, max_concurrent=max_concurrent)
                
                # Start time
                start_time = time.time()
                
                # Process URLs
                processed_count = scraper.process_urls(tmp_path, output_file)
                
                # Calculate time taken
                time_taken = time.time() - start_time
                
                if processed_count > 0:
                    try:
                        # Read and display results
                        df = pd.read_csv(output_file)
                        
                        # Ensure required columns exist
                        if 'emails' not in df.columns:
                            df['emails'] = ''
                        
                        # Update progress to 100%
                        progress_bar.progress(100)
                        status_text.text("Scraping complete!")
                        
                        st.success(f"Scraping completed in {time_taken:.1f} seconds!")
                        
                        # Show results in expandable sections
                        with st.expander("View Results", expanded=True):
                            st.dataframe(df)
                        
                        # Download button
                        with open(output_file, "rb") as f:
                            st.download_button(
                                label="Download CSV",
                                data=f,
                                file_name="scraped_emails.csv",
                                mime="text/csv"
                            )
                        
                        # Show statistics
                        st.write("### Statistics")
                        
                        try:
                            # Handle potential non-string values in emails column
                            emails_series = df['emails'].fillna('').astype(str)
                            total_emails = emails_series.str.count(',').fillna(0).astype(int) + (emails_series != '').astype(int)
                            
                            st.write(f"Total URLs processed: {len(df)}")
                            st.write(f"Total emails found: {total_emails.sum()}")
                            st.write(f"URLs with emails: {len(df[df['emails'].fillna('') != ''])}")
                            st.write(f"Average time per URL: {time_taken/len(df):.2f} seconds")
                        except Exception as stats_error:
                            st.write(f"Total URLs processed: {len(df)}")
                            st.write("Could not calculate email statistics")
                            st.error(f"Statistics error: {str(stats_error)}")
                            
                    except Exception as e:
                        st.error(f"Error processing results: {str(e)}")
                        st.write("Raw results file created but could not be processed")
                        
                        # Try to show basic file info
                        try:
                            with open(output_file, 'r') as f:
                                content = f.read()
                                st.text_area("Raw CSV Content", content, height=200)
                        except:
                            st.write("Could not read output file")
                else:
                    st.warning("No URLs were processed successfully. Please check your URLs and try again.")
                
                # Cleanup temporary files
                os.remove(tmp_path)
                os.remove(output_file) 