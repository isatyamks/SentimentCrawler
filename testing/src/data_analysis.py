import string
import re
import os
import csv
import pandas as pd
# Utility Function: Count syllables in a word
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

# Function: Load words from a file
def load_words(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return set(file.read().splitlines())



# Function: Preprocess text
def preprocess_text(article):
    translator = str.maketrans('', '', string.punctuation)
    return article.translate(translator).lower()

# Function: Calculate Positive Score
def calculate_positive_score(words, positive_words):
    return sum(1 for word in words if word in positive_words)

# Function: Calculate Negative Score
def calculate_negative_score(words, negative_words):
    return sum(1 for word in words if word in negative_words)

# Function: Calculate Polarity Score
def calculate_polarity_score(positive_count, negative_count):
    return (positive_count - negative_count) / ((positive_count + negative_count) + 0.000001)

# Function: Calculate Subjectivity Score
def calculate_subjectivity_score(positive_count, negative_count, total_words):
    return (positive_count + negative_count) / total_words

# Function: Calculate Average Sentence Length
def calculate_avg_sentence_length(total_words, total_sentences):
    return total_words / total_sentences

# Function: Calculate Percentage of Complex Words
def calculate_percentage_complex_words(complex_word_count, total_words):
    return (complex_word_count / total_words) * 100

# Function: Calculate Fog Index
def calculate_fog_index(avg_sentence_length, percentage_complex_words):
    return 0.4 * (avg_sentence_length + percentage_complex_words)

# Function: Calculate Complex Word Count
def calculate_complex_word_count(words):
    return sum(1 for word in words if count_syllables(word) >= 3)

# Function: Calculate Total Word Count
def calculate_word_count(words):
    return len(words)

# Function: Calculate Syllables per Word
def calculate_syllables_per_word(total_syllables, total_words):
    return total_syllables / total_words

# Function: Count Personal Pronouns
def count_personal_pronouns(article):
    pronouns = re.findall(r'\b(I|we|you|he|she|it|they|me|us|him|her|them|my|our|your|his|their)\b', article, re.IGNORECASE)
    return len(pronouns)

# Function: Calculate Average Word Length
def calculate_avg_word_length(total_characters, total_words):
    return total_characters / total_words

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
    
    # Metrics calculations
    positive_count = calculate_positive_score(words, positive_words)
    negative_count = calculate_negative_score(words, negative_words)
    polarity_score = calculate_polarity_score(positive_count, negative_count)
    subjectivity_score = calculate_subjectivity_score(positive_count, negative_count, len(words))
    avg_sentence_length = calculate_avg_sentence_length(len(words), total_sentences)
    complex_word_count = calculate_complex_word_count(words)
    percentage_complex_words = calculate_percentage_complex_words(complex_word_count, len(words))
    fog_index = calculate_fog_index(avg_sentence_length, percentage_complex_words)
    syllables = sum(count_syllables(word) for word in words)
    syllables_per_word = calculate_syllables_per_word(syllables, len(words))
    personal_pronouns = count_personal_pronouns(article)
    avg_word_length = calculate_avg_word_length(sum(len(word) for word in words), len(words))
    
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

# Example usage
articles_folder = "clean"  # Folder containing articles
positive_words_file = "MasterDictionary\\positive-words.txt"
negative_words_file = "MasterDictionary\\negative-words.txt"
csv_file = "temp.csv"







process_articles(articles_folder, positive_words_file, negative_words_file, csv_file)
