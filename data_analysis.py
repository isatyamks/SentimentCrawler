




import string

def positive_score(positive_words_file, article_file):
    # Step 1: Load positive words
    with open(positive_words_file, 'r') as file:
        positive_words = set(file.read().splitlines())
    
    # Step 2: Read and preprocess the article
    with open(article_file, 'r') as file:
        article = file.read()
    # Remove punctuation and convert to lowercase
    translator = str.maketrans('', '', string.punctuation)
    article = article.translate(translator).lower()
    words = article.split()
    
    # Step 3: Count positive words
    positive_count = sum(1 for word in words if word in positive_words)
    
    # Step 4: Calculate the normalized score
    total_words = len(words)
    normalized_score = (positive_count / total_words) * 100 if total_words > 0 else 0
    
    return positive_count, normalized_score

# Example usage
positive_words_file = "MasterDictionary\positive-words.txt"
article_file = "test\\Netclan20241017.txt"              
positive_count, normalized_score = positive_score(positive_words_file, article_file)

print(f"Positive Word Count: {positive_count}")
print(f"Normalized Positive Score: {normalized_score:.2f}%")


