import csv
import requests
from bs4 import BeautifulSoup
import os
import re
def extract_article(url):
    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the main heading (in <h1>)
        main_heading = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
        
        # Extract subheadings (in <strong>)
        subheadings = soup.find_all('strong')
        subheading_text = '\n'.join([sub.get_text(strip=True) for sub in subheadings])
        
        # Extract body content (in <p>)
        body_paragraphs = soup.find_all('p')
        body_text = '\n'.join([p.get_text(strip=True) for p in body_paragraphs])
        # Combine all parts into a single article text
        article_text = f"{main_heading}\n\n{subheading_text}\n\n{body_text}"
        # print(article_text)
        return article_text
    except Exception as e:
        print(f"Error fetching article from {url}: {e}")
        return None, None

import os
import re

def save_to_file(url, article_text, save_dir):
    try:
        os.makedirs(save_dir, exist_ok=True)
        url_suffix = url.split("blackcoffer.com/")[-1]
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', url_suffix) 
        filename = os.path.join(save_dir, f"{safe_filename}.txt")  
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(article_text)
        print(f"Saved article to {filename}")
    except Exception as e:
        print(f"Error saving file {url}: {e}")





url_id = "https://insights.blackcoffer.com/ai-and-ml-based-youtube-analytics-and-content-creation-tool-for-optimizing-subscriber-engagement-and-content-strategy"
article_text = extract_article(url_id)
save_dir = "articles"
save_to_file(url_id, article_text, save_dir)