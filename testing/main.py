import csv
import requests
from bs4 import BeautifulSoup
import os
import re
import string
import pandas as pd

#####################################################################################

input_csv = "input.csv" 
article_dir = "articles"  
output_csv = "output.csv"
stopwords_dir = "StopWords"
pf = "MasterDictionary\\positive-words.txt"
nf = "MasterDictionary\\negative-words.txt"

def extract_article(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    mh = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
    sh = soup.find_all('strong')
    st = '\n'.join([sub.get_text(strip=True) for sub in sh])
    b_par = soup.find_all('p')
    bt = '\n'.join([p.get_text(strip=True) for p in b_par])
    article = f"{mh}\n\n{st}\n\n{bt}"
    return article


def save_to_file(file_id, article_text, article_dir):
    os.makedirs(article_dir, exist_ok=True)
    filename = os.path.join(article_dir, f"{file_id}.txt")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(article_text)


def process_csv(input_csv, article_dir):
    with open(input_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            file_id = row['URL_ID']
            url = row['URL']
            print(f"URL_ID: {file_id} Completed\n")
            article_text = extract_article(url)
            if article_text:
                save_to_file(file_id, article_text, article_dir)


######################################################################################################################


def analyze_text(article, positive_file, negative_file):
    # Load positive and negative words
    def load_words(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return set(file.read().splitlines())

    positive_words = load_words(positive_file)
    negative_words = load_words(negative_file)

    # Preprocess text
    translator = str.maketrans('', '', string.punctuation)
    preprocessed_article = article.translate(translator).lower()

    # Tokenize words
    words = preprocessed_article.split()
    total_words = len(words)

    # Sentence splitting
    sentences = re.split(r'[.!?]', article)
    total_sentences = len(sentences)

    # Calculate Positive and Negative Scores
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    # Calculate Polarity Score
    polarity_score = (positive_count - negative_count) / ((positive_count + negative_count) + 0.000001)

    # Calculate Subjectivity Score
    subjectivity_score = (positive_count + negative_count) / total_words

    # Calculate Average Sentence Length
    avg_sentence_length = total_words / total_sentences

    # Calculate Complex Word Count
    def count_syllables(word):
        vowels = 'aeiouy'
        word = word.lower()
        syllables = 0
        if word[0] in vowels:
            syllables += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                syllables += 1
        if word.endswith('e'):
            syllables -= 1
        return max(1, syllables)

    complex_word_count = sum(1 for word in words if count_syllables(word) >= 3)

    # Calculate Percentage of Complex Words
    percentage_complex_words = (complex_word_count / total_words) * 100

    # Calculate Fog Index
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    # Calculate Syllables per Word
    total_syllables = sum(count_syllables(word) for word in words)
    syllables_per_word = total_syllables / total_words

    # Count Personal Pronouns
    pronouns = re.findall(r'\b(I|we|you|he|she|it|they|me|us(?!\b)|him|her|them|my|our|your|his|their)\b', article) #us(?!\b) for US and us conflict
    personal_pronouns = len(pronouns)

    # Calculate awl
    total_characters = sum(len(word) for word in words)
    avg_word_length = total_characters / total_words

    # Return all metrics as a dictionary
    return {
        "ps": positive_count,
        "ns": negative_count,
        "pts": polarity_score,
        "ss": subjectivity_score,
        "asl":avg_sentence_length,
        "pcw": percentage_complex_words,
        "fi": fog_index,
        "awps": avg_sentence_length,
        "cwc": complex_word_count,
        "wc": len(words),
        "spw": syllables_per_word,
        "pp": personal_pronouns,
        "awl": avg_word_length,
    }

def process_articles(article_dir, pf, nf, output_csv):
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv)
    else:
        raise FileNotFoundError(f"CSV file {output_csv} does not exist.")
    
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
    for article_file in os.listdir(article_dir):
        if article_file.endswith('.txt'):
            # Extract article ID from filename
            article_id = article_file.replace('.txt', '')  # Get the base name without extension
            
            # Check if the article ID exists in the CSV
            if article_id not in df['URL_ID'].astype(str).values:
                print(f"Article ID {article_id} not found in CSV. Skipping.")
                continue
            
            # Full path to the article
            article_path = os.path.join(article_dir, article_file)
            
            # Analyze the article
            results = analyze_text(article_path, pf, nf)
            
            # Update the corresponding row in the DataFrame with results
            df.loc[df['URL_ID'].astype(str) == article_id, 'POSITIVE SCORE'] = results['ps']
            df.loc[df['URL_ID'].astype(str) == article_id, 'NEGATIVE SCORE'] = results['ns']
            df.loc[df['URL_ID'].astype(str) == article_id, 'POLARITY SCORE'] = results['pts']
            df.loc[df['URL_ID'].astype(str) == article_id, 'SUBJECTIVITY SCORE'] = results['ss']
            df.loc[df['URL_ID'].astype(str) == article_id, 'AVG SENTENCE LENGTH'] = results['asl']
            df.loc[df['URL_ID'].astype(str) == article_id, 'PERCENTAGE OF COMPLEX WORDS'] = results['pcw']
            df.loc[df['URL_ID'].astype(str) == article_id, 'FOG INDEX'] = results['fi']
            df.loc[df['URL_ID'].astype(str) == article_id, 'AVG NUMBER OF WORDS PER SENTENCE'] = results['awps']
            df.loc[df['URL_ID'].astype(str) == article_id, 'COMPLEX WORD COUNT'] = results['cwc']
            df.loc[df['URL_ID'].astype(str) == article_id, 'WORD COUNT'] = results['wc']
            df.loc[df['URL_ID'].astype(str) == article_id, 'SYLLABLE PER WORD'] = results['spw']
            df.loc[df['URL_ID'].astype(str) == article_id, 'PERSONAL PRONOUNS'] = results['pp']
            df.loc[df['URL_ID'].astype(str) == article_id, 'AVG WORD LENGTH'] = results['awl']
    
    # Save the updated DataFrame back to the CSV
    df.to_csv(output_csv, index=False)
    print(f"Analysis complete. Results updated in {output_csv}")




















process_csv(input_csv, article_dir)
process_articles(article_dir, pf, nf, output_csv)
