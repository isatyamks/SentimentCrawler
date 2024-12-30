import string
import re
import os
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re







csv_file = "input.csv" 
save_dir = "articles"  

# Example usage
articles_folder = "articles"  # Folder containing articles
positive_words_file = "MasterDictionary\\positive-words.txt"
negative_words_file = "MasterDictionary\\negative-words.txt"
csv_file = "output.csv"



def extract_article(url):
    response = requests.get(url)
    response.raise_for_status() 
    soup = BeautifulSoup(response.content, 'html.parser')
    main_heading = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
    subheadings = soup.find_all('strong')
    subheading_text = '\n'.join([sub.get_text(strip=True) for sub in subheadings])
    body_paragraphs = soup.find_all('p')
    body_text = '\n'.join([p.get_text(strip=True) for p in body_paragraphs])
    article_text = f"{main_heading}\n\n{subheading_text}\n\n{body_text}"
    return article_text


def save_to_file(file_id, article_text, save_dir):
    os.makedirs(save_dir, exist_ok=True) 
    filename = os.path.join(save_dir, f"{file_id}.txt")  
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(article_text)


def process_csv(csv_file, save_dir):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file) 
        for row in reader:
            file_id = row['URL_ID'] 
            url = row['URL'] 
            print(f"Processing ID: {file_id} is Completed!")
            article_text = extract_article(url)
            if article_text:
                save_to_file(file_id, article_text, save_dir)



def count_syllables(word):
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    if word and word[0] in vowels:
        syllable_count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            syllable_count += 1
    if word.endswith("e"):
        syllable_count -= 1
    return max(1, syllable_count)

def load_words(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return set(file.read().splitlines())



def preprocess_text(article):
    translator = str.maketrans('', '', string.punctuation)
    return article.translate(translator).lower()

# Master Function to Analyze Text
def analyze_text(article_file, positive_words_file, negative_words_file):
    # Load words and text
    positive_words = load_words(positive_words_file)
    negative_words = load_words(negative_words_file)
    with open(article_file, 'r', encoding='utf-8') as file:
        article = file.read()
    sentences = re.split(r'[.!?]', article)
    total_sentences = len(sentences)
    preprocessed_article = preprocess_text(article)
    words = preprocessed_article.split()
    r=3
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    polarity_score = round((positive_count - negative_count) / ((positive_count + negative_count) + 0.000001),r)
    total_words = len(words) 
    subjectivity_score =  round(((positive_count + negative_count) / total_words),r)
    avg_sentence_length = int(total_words / total_sentences)
    complex_word_count = sum(1 for word in words if count_syllables(word) >= 3)
    percentage_complex_words = round(((complex_word_count / total_words) * 100),r)
    fog_index = round((0.4 * (avg_sentence_length + percentage_complex_words)),r)
    syllables = sum(count_syllables(word) for word in words)
    syllables_per_word = round((syllables / total_words),r)
    pronouns = re.findall(r'\b(I|we|you|he|she|it|they|me|us|him|her|them|my|our|your|his|their)\b', article, re.IGNORECASE)
    personal_pronouns = len(pronouns)
    avg_word_length = int(sum(len(word) for word in words) / total_words)
    
    # Results
    return {
        "Positive Score": positive_count,
        "Negative Score": negative_count,
        "Polarity Score": polarity_score,
        "Subjectivity Score": subjectivity_score,
        "Average Sentence Length": avg_sentence_length,
        "Percentage of Complex Words": percentage_complex_words,
        "Fog Index": fog_index,
        "Average Words per Sentence": avg_sentence_length,
        "Complex Word Count": complex_word_count,
        "Word Count": len(words),
        "Syllables per Word": syllables_per_word,
        "Personal Pronouns": personal_pronouns,
        "Average Word Length": avg_word_length,
    }


def process_articles(articles_folder, positive_words_file, negative_words_file, csv_file):
    # Load positive and negative word lists
    positive_words = load_words(positive_words_file)
    negative_words = load_words(negative_words_file)
    
    # Load the existing CSV file
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        raise FileNotFoundError(f"CSV file {csv_file} does not exist.")
    
    # Convert column names to uppercase for consistent matching
    df.columns = df.columns.str.upper()

    # Ensure the necessary columns exist in the CSV
    required_columns = [
        "URL_ID", "URL", "POSITIVE SCORE", "NEGATIVE SCORE", "POLARITY SCORE", 
        "SUBJECTIVITY SCORE", "AVG SENTENCE LENGTH", "PERCENTAGE OF COMPLEX WORDS", 
        "FOG INDEX", "AVG NUMBER OF WORDS PER SENTENCE", "COMPLEX WORD COUNT", 
        "WORD COUNT", "SYLLABLE PER WORD", "PERSONAL PRONOUNS", "AVG WORD LENGTH"
    ]
    
    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in CSV file: {', '.join(missing_columns)}")
    
    # Iterate through all articles in the folder
    for article_file in os.listdir(articles_folder):
        if article_file.endswith('.txt'):
            # Extract article ID from filename
            article_id = article_file.replace('.txt', '')  # Get the base name without extension
            
            # Check if the article ID exists in the CSV
            if article_id not in df['URL_ID'].astype(str).values:
                print(f"Article ID {article_id} not found in CSV. Skipping.")
                continue
            
            # Full path to the article
            article_path = os.path.join(articles_folder, article_file)
            
            # Analyze the article
            results = analyze_text(article_path, positive_words_file, negative_words_file)
            
            # Update the corresponding row in the DataFrame with results
            df.loc[df['URL_ID'].astype(str) == article_id, 'POSITIVE SCORE'] = results['Positive Score']
            df.loc[df['URL_ID'].astype(str) == article_id, 'NEGATIVE SCORE'] = results['Negative Score']
            df.loc[df['URL_ID'].astype(str) == article_id, 'POLARITY SCORE'] = results['Polarity Score']
            df.loc[df['URL_ID'].astype(str) == article_id, 'SUBJECTIVITY SCORE'] = results['Subjectivity Score']
            df.loc[df['URL_ID'].astype(str) == article_id, 'AVG SENTENCE LENGTH'] = results['Average Sentence Length']
            df.loc[df['URL_ID'].astype(str) == article_id, 'PERCENTAGE OF COMPLEX WORDS'] = results['Percentage of Complex Words']
            df.loc[df['URL_ID'].astype(str) == article_id, 'FOG INDEX'] = results['Fog Index']
            df.loc[df['URL_ID'].astype(str) == article_id, 'AVG NUMBER OF WORDS PER SENTENCE'] = results['Average Words per Sentence']
            df.loc[df['URL_ID'].astype(str) == article_id, 'COMPLEX WORD COUNT'] = results['Complex Word Count']
            df.loc[df['URL_ID'].astype(str) == article_id, 'WORD COUNT'] = results['Word Count']
            df.loc[df['URL_ID'].astype(str) == article_id, 'SYLLABLE PER WORD'] = results['Syllables per Word']
            df.loc[df['URL_ID'].astype(str) == article_id, 'PERSONAL PRONOUNS'] = results['Personal Pronouns']
            df.loc[df['URL_ID'].astype(str) == article_id, 'AVG WORD LENGTH'] = results['Average Word Length']
    
    # Save the updated DataFrame back to the CSV
    df.to_csv(csv_file, index=False)
    print(f"Analysis complete. Results updated in {csv_file}")





process_csv(csv_file, save_dir)
process_articles(articles_folder, positive_words_file, negative_words_file, csv_file)
