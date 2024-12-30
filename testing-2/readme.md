# Data Extraction and NLP Test Assignment 

## Problem Statement

Given a set of URLs, the task is to:
1. Extract articles from the web.
2. Perform text analysis to compute various variables.
3. Update the results into Output Data Structure file.


## Approach to the Solution

### **Step 1: Article Extraction**
To extract text from the given URLs:
- Used the `requests` library to fetch webpage content.
- Used `BeautifulSoup` (from `bs4`) to parse HTML and extract:
  - Main headings (`<h1>` tags).
  - Subheadings (`<strong>` tags).
  - Body paragraphs (`<p>` tags).
- Combined these elements to form the full article text, saved to local `.txt` files for further processing.

### **Step 2: Text Preprocessing**
To prepare the text for analysis:
- Removed punctuation and converted the text to lowercase for consistency.
- Split the text into sentences and words using Python's `re` library.

### **Step 3: Sentiment Analysis**
Using pre-defined positive and negative word lists:
- Counted the occurrences of positive and negative words in the text.

  

## How to Run Model.py

### Prerequisites
1. Python 3.8+

2. Install required libraries using: 
  ```bash
    pip install -r requirements.txt   
    ```
3. 

4. Run the script:
   ```bash
   python model.py
     ```


