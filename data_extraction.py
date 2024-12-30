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
        return article_text
    except Exception as e:
        print(f"Error fetching article from {url}: {e}")
        return None

def save_to_file(file_id, article_text, save_dir):
    try:
        os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists
        filename = os.path.join(save_dir, f"{file_id}.txt")  # Use file_id as the filename
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(article_text)
        print(f"Saved article to {filename}")
    except Exception as e:
        print(f"Error saving file {file_id}: {e}")






def process_csv(csv_file, save_dir):
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)  # Read CSV as a dictionary
            for row in reader:
                file_id = row['URL_ID']  # Use the `id` column
                url = row['URL']  # Use the `url` column
                print(f"Processing ID: {file_id}, URL: {url}")
                article_text = extract_article(url)
                if article_text:
                    save_to_file(file_id, article_text, save_dir)
    except Exception as e:
        print(f"Error processing CSV file {csv_file}: {e}")

csv_file = "data/input.csv" 
save_dir = "articles"  
process_csv(csv_file, save_dir)

