import os

# Function to load stopwords from files in stopwords folder
def load_stopwords(stopwords_folder):
    stopwords = set()
    for file_name in os.listdir(stopwords_folder):
        file_path = os.path.join(stopwords_folder, file_name)
        with open(file_path, 'r',encoding='utf-8') as f:
            stopwords.update(f.read().splitlines())  # Add each word from stopwords files to the set
    return stopwords

# Function to remove stopwords from the article text
def remove_stopwords_from_article(article_path, stopwords):
    with open(article_path, 'r',encoding='utf-8') as file:
        article_content = file.read()
    
    # Tokenizing the content and removing stopwords
    filtered_content = ' '.join([word for word in article_content.split() if word.lower() not in stopwords])
    
    return filtered_content

# Path to the folder containing stopwords
stopwords_folder = "StopWords"
# Path to the folder containing articles
articles_folder = "articles-1"

# Load stopwords
stopwords = load_stopwords(stopwords_folder)

# Process each article and remove stopwords
for article_name in os.listdir(articles_folder):
    article_path = os.path.join(articles_folder, article_name)
    if article_path.endswith('.txt'):
        cleaned_content = remove_stopwords_from_article(article_path, stopwords)
        
        # Save the cleaned content to a new file or replace the original one
        with open(f"clean\\{article_name}", 'w', encoding='utf-8') as output_file:
            output_file.write(cleaned_content)
